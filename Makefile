VERSION ?= latest
IMAGE_TAG_BASE ?= observability-dashboard
IMG ?= $(IMAGE_TAG_BASE):$(VERSION)
PLATFORMS ?= linux/arm64,linux/amd64


.PHONY: all
all: build docker-build


.PHONY: build
build:
	uv sync


.PHONY: run
run: build
	uv run fastapi run --port 10005


.PHONY: dev
dev: build
	uv run fastapi dev --port 10005


.PHONY: test
test: build
	uv run pytest


.PHONY: check
check: build test
	uv run mypy .
	uv run ruff check
	uv run lint-imports
	uv run bandit -c pyproject.toml -r .


.PHONY: check-fix
check-fix: build
	uv run ruff format
	uv run ruff check --fix


.PHONY: docker-build
docker-build:
	docker build -t $(IMG) .

.PHONY: docker-run
docker-run: docker-build
	docker run --rm -it -p 8000:8000 $(IMG)
