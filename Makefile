.PHONY: help venv run test freeze podman-up podman-down superuser

help:
	@echo "Targets:"
	@echo "  make venv        - create venv, install deps, migrate (SQLite)"
	@echo "  make run         - run dev server from venv (localhost:8000)"
	@echo "  make test        - run pytest from venv"
	@echo "  make freeze      - write requirements.txt from venv"
	@echo "  make podman-up   - start containers (web+postgres)"
	@echo "  make podman-down - stop containers"
	@echo "  make superuser   - create Django admin user (venv or container)"

venv:
	./scripts/setup_venv.sh

run:
	./scripts/run_venv.sh

test:
	. .venv/bin/activate && python -m pytest -q

freeze:
	./scripts/freeze_requirements.sh

podman-up:
	./scripts/up_podman.sh

podman-down:
	./scripts/down_podman.sh

# Creates a superuser in the venv by default; set MODE=podman to do it in container
superuser:
	@if [ "$(MODE)" = "podman" ]; then \
		podman-compose exec web python manage.py createsuperuser; \
	else \
		. .venv/bin/activate && python manage.py createsuperuser; \
	fi
