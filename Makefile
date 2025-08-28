VERSION ?= $(shell echo "$$(git rev-parse --abbrev-ref HEAD)-$$(git rev-parse --short=7 HEAD)-$$(date +%s)")
IMAGE_TAG_BASE ?= eu.gcr.io/agentic-layer/observability-dashboard
IMG ?= $(IMAGE_TAG_BASE):$(VERSION)
GCP_LOCATION ?= europe-west3
GCP_PROJECT_ID ?= qaware-paal
GCP_REPOSITORY ?= agentic-layer
PLATFORMS ?= linux/arm64,linux/amd64

.PHONY: all
all: build docker-build


.PHONY: build
build:
	uv sync


.PHONY: run
run: build
	uv run fastapi run


.PHONY: dev
dev: build
	uv run fastapi dev


.PHONY: test
test: build
	uv run pytest


.PHONY: check
check: build test
	uv run mypy .
	uv run ruff check
	uv run lint-imports
	uv run bandit -c pyproject.toml -r .
	uv export --frozen --no-hashes | pip-audit -r /dev/stdin


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

.PHONY: docker-push
docker-push:
	- docker buildx create --name agent-builder
	docker buildx use agent-builder
	docker buildx build --push --platform=$(PLATFORMS) --tag ${IMG} .
