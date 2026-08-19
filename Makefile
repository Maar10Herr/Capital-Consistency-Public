.PHONY: test reproduce audit

test:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$(CURDIR)/src" python3 -m unittest discover -s tests -p 'test_*.py' -v

reproduce:
	bash scripts/reproduce_all.sh

audit:
	bash scripts/audit_repository.sh
