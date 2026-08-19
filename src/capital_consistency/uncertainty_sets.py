"""Small exact-form support calculations for ellipsoids and boxes."""

import math
from typing import Sequence, Tuple

from .numeric import require_finite


Vector = Sequence[float]
Matrix = Sequence[Sequence[float]]


def dot(left: Vector, right: Vector) -> float:
    if len(left) != len(right):
        raise ValueError("dimension mismatch")
    require_finite("vectors", *left, *right)
    result = sum(x * y for x, y in zip(left, right))
    require_finite("dot-product result", result)
    return result


def quadratic_form(vector: Vector, matrix: Matrix) -> float:
    n = len(vector)
    if len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("dimension mismatch")
    require_finite("quadratic-form vector", *vector)
    require_finite("quadratic-form matrix", *(value for row in matrix for value in row))
    result = sum(vector[i] * matrix[i][j] * vector[j] for i in range(n) for j in range(n))
    require_finite("quadratic-form result", result)
    return result


def validate_covariance(matrix: Matrix, tolerance: float = 1e-12) -> None:
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("covariance must be nonempty and square")
    require_finite("covariance tolerance", tolerance)
    if not 0 <= tolerance < 1:
        raise ValueError("covariance tolerance must lie in [0,1)")
    require_finite("covariance", *(value for row in matrix for value in row))
    # Scale first, then use a diagonally pivoted Schur-complement test. This is
    # O(n^3), supports singular PSD matrices, and avoids absolute tolerances and
    # overflow in products such as a_ij^2 / a_ii.
    raw = [list(map(float, row)) for row in matrix]
    scale = max(abs(value) for row in raw for value in row)
    if scale == 0.0:
        return
    work = [[value / scale for value in row] for row in raw]
    for i in range(n):
        for j in range(n):
            if abs(work[i][j] - work[j][i]) > tolerance:
                raise ValueError("covariance must be symmetric")
    threshold = tolerance
    for column in range(n):
        pivot = max(range(column, n), key=lambda index: work[index][index])
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            for row in work:
                row[column], row[pivot] = row[pivot], row[column]
        pivot_value = work[column][column]
        if pivot_value < -threshold:
            raise ValueError("covariance is not positive semidefinite")
        if pivot_value <= threshold:
            if any(
                abs(work[i][j]) > threshold
                for i in range(column, n)
                for j in range(column, n)
            ):
                raise ValueError("covariance is not positive semidefinite")
            return
        for i in range(column + 1, n):
            for j in range(i, n):
                updated = work[i][j] - work[i][column] * work[j][column] / pivot_value
                work[i][j] = updated
                work[j][i] = updated


def ellipsoid_affine_upper(
    center: Vector, covariance: Matrix, gradient: Vector, radius: float
) -> float:
    """Support value over center + covariance^(1/2) z, ||z||_2 <= radius.

    The formula remains valid for singular positive-semidefinite covariance.
    """

    if radius < 0 or len(center) != len(gradient):
        raise ValueError("invalid radius or dimensions")
    require_finite("ellipsoid radius", radius)
    require_finite("ellipsoid center and gradient", *center, *gradient)
    validate_covariance(covariance)
    matrix_scale = max(abs(value) for row in covariance for value in row)
    gradient_scale = max((abs(value) for value in gradient), default=0.0)
    if matrix_scale == 0.0 or gradient_scale == 0.0:
        support_norm = 0.0
    else:
        normalized_gradient = [value / gradient_scale for value in gradient]
        normalized_matrix = [[value / matrix_scale for value in row] for row in covariance]
        normalized_variance = sum(
            normalized_gradient[i] * normalized_matrix[i][j] * normalized_gradient[j]
            for i in range(len(gradient))
            for j in range(len(gradient))
        )
        if normalized_variance < -1e-12:
            raise ValueError("negative quadratic form after PSD validation")
        support_norm = (
            math.sqrt(matrix_scale)
            * math.sqrt(max(0.0, normalized_variance))
            * gradient_scale
        )
    result = dot(gradient, center) + radius * support_norm
    require_finite("ellipsoid support result", result)
    return result


def box_affine_upper(center: Vector, half_widths: Vector, gradient: Vector) -> float:
    if len(center) != len(half_widths) or len(center) != len(gradient):
        raise ValueError("dimension mismatch")
    require_finite("box inputs", *center, *half_widths, *gradient)
    if any(width < 0 for width in half_widths):
        raise ValueError("box half-widths must be nonnegative")
    result = dot(gradient, center) + sum(abs(a) * width for a, width in zip(gradient, half_widths))
    require_finite("box support result", result)
    return result
