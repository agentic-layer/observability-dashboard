# Tiltfile for observability-dashboard development

# Apply Kubernetes manifests
k8s_yaml(kustomize('deploy/local'))

# Build and deploy the app
app_name = 'observability-dashboard'

# Build frontend initially
local_resource(
    'frontend-build',
    cmd='cd frontend && npm ci && npm run build',
    deps=['frontend/src', 'frontend/package.json', 'frontend/package-lock.json', 'frontend/vite.config.ts', 'frontend/tsconfig.json'],
    resource_deps=[]
)

docker_build(
    app_name,
    '.',
    live_update=[
        # Sync backend source code changes
        sync('src', '/app/src'),

        # Sync built frontend files to container static directory
        sync('frontend/dist', '/app/frontend/dist'),

        # Re-install backend dependencies if project files change
        run(
            'uv sync --frozen',
            trigger=['pyproject.toml', 'uv.lock']
        )
    ]
)

k8s_resource(
    app_name,
    port_forwards='10005:8000',
    labels=['observability-dashboard']
)
