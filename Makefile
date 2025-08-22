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
	uv run fastapi run src/agent_monitor/main.py

.PHONY: dev
dev: build
	uv run fastapi dev src/agent_monitor/main.py

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
