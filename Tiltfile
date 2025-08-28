# Tiltfile for observability-dashboard development

# Apply Kubernetes manifests
k8s_yaml(kustomize('deploy/local'))

# Build and deploy the app
app_name = 'observability-dashboard'

docker_build(
    app_name,
    context='.',
    live_update=[
        # Sync backend source code changes
        sync('app', '/app/app'),
        sync('pyproject.toml', '/app/pyproject.toml'),
        sync('uv.lock', '/app/uv.lock'),

        # Re-install backend dependencies if project files change
        run(
            'cd /app && uv sync --frozen',
            trigger=['pyproject.toml', 'uv.lock']
        )
    ],
    entrypoint=["uv", "run", "fastapi", "run", "--reload"],
)

k8s_resource(
    app_name,
    port_forwards='10005:8000',
    labels=[app_name],
)
