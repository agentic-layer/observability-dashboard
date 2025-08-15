# Tiltfile for observability-dashboard development

# Apply Kubernetes manifests
k8s_yaml(kustomize('deploy/local'))

# Build and deploy the app
app_name = 'observability-dashboard'

docker_build(
    app_name,
    live_update=[
        # Sync source code changes into the container
        sync('src', '/app/src'),

        # Re-install dependencies if the project files change
        run(
            'uv sync --frozen',
            trigger=['backend/pyproject.toml', 'backend/uv.lock']
        )
    ]
)

k8s_resource(
    app_name,
    port_forwards='10005:8000',
    labels=['observability-dashboard']
)
