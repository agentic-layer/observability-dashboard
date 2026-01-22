# Tiltfile for observability-dashboard development

# Install base resources via Helm chart (local development)
# Override image repositories to use local Tilt-built images (without registry prefix)
k8s_yaml(helm(
    'chart',
    name='observability-dashboard',
    namespace='observability-dashboard',
    values=['chart/values.yaml'],
    set=[
        'image.repository=observability-dashboard',
    ],
))

docker_build(
    'observability-dashboard',
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
    'observability-dashboard',
    port_forwards='10005:8000',
    labels=['observability-dashboard'],
)
