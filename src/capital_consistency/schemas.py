"""Versioned, deliberately small economic-history schema."""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Tuple

from .numeric import require_finite, require_nonnegative_integer


SCHEMA_VERSION = "1.0"
FLOW_KINDS = frozenset(
    {"drawing", "repayment", "recovery", "collateral_proceeds", "recovery_cost", "write_off"}
)
STATES = frozenset({"performing", "default", "cured", "probation", "terminated"})
UNITS = frozenset({"facility", "obligor", "grade", "segment", "cohort", "calendar_period"})


@dataclass(frozen=True)
class LimitObservation:
    time: float
    commitment: float
    drawn: float

    def validate(self) -> None:
        require_finite("limit observation", self.time, self.commitment, self.drawn)
        if self.time < 0 or self.commitment < 0 or self.drawn < 0:
            raise ValueError("time, commitment, and drawn must be nonnegative")


@dataclass(frozen=True)
class CashFlow:
    time: float
    amount: float
    discount_factor: float
    kind: str
    default_episode: int = 0

    def validate(self) -> None:
        require_finite("cash flow", self.time, self.amount, self.discount_factor)
        require_nonnegative_integer("default_episode", self.default_episode)
        if self.time < 0 or self.amount < 0 or self.discount_factor < 0:
            raise ValueError("time, amount, and discount factor must be nonnegative")
        if self.kind not in FLOW_KINDS:
            raise ValueError("unknown cash-flow kind: %s" % self.kind)


@dataclass(frozen=True)
class StateTransition:
    time: float
    state: str
    default_episode: int = 0

    def validate(self) -> None:
        require_finite("state transition time", self.time)
        require_nonnegative_integer("default_episode", self.default_episode)
        if self.time < 0 or self.default_episode < 0 or self.state not in STATES:
            raise ValueError("invalid state transition")


@dataclass(frozen=True)
class EconomicHistory:
    history_id: str
    observation_unit: str
    limits: Tuple[LimitObservation, ...]
    cashflows: Tuple[CashFlow, ...]
    states: Tuple[StateTransition, ...]
    schema_version: str = SCHEMA_VERSION

    def validate(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported schema_version")
        if not self.history_id:
            raise ValueError("history_id is required")
        if self.observation_unit not in UNITS:
            raise ValueError("invalid observation_unit")
        for sequence in (self.limits, self.cashflows, self.states):
            previous = -1.0
            for item in sequence:
                item.validate()
                if item.time < previous:
                    raise ValueError("events must be time ordered within each sequence")
                previous = item.time

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EconomicHistory":
        history = cls(
            history_id=str(data["history_id"]),
            observation_unit=str(data["observation_unit"]),
            limits=tuple(LimitObservation(**x) for x in data.get("limits", [])),
            cashflows=tuple(CashFlow(**x) for x in data.get("cashflows", [])),
            states=tuple(StateTransition(**x) for x in data.get("states", [])),
            schema_version=str(data.get("schema_version", "")),
        )
        history.validate()
        return history
