# Tiltfile for agent-communications-dashboard development

# Apply Kubernetes manifests
k8s_yaml(kustomize('deploy/local'))

# Build and deploy the agent communications dashboard backend
dashboard_backend_name = 'agent-communications-dashboard-backend'

docker_build(
    dashboard_backend_name,
    context='backend',
    live_update=[
        # Sync source code changes into the container
        sync('backend/src', '/app/src'),

        # Re-install dependencies if the project files change
        run(
            'uv sync --frozen',
            trigger=['backend/pyproject.toml', 'backend/uv.lock']
        )
    ]
)

k8s_resource(
    dashboard_backend_name,
    port_forwards='10005:8000',
    labels=['agent-communications-dashboard']
)
