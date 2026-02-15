"""Tests for validating configuration files in the main app."""
import os
import yaml
import pytest


def test_docker_compose_yaml_exists():
    """Verify docker-compose.yml file exists."""
    assert os.path.isfile('docker-compose.yml'), "docker-compose.yml not found"


def test_docker_compose_yaml_valid():
    """Validate docker-compose.yml is valid YAML with required services."""
    with open('docker-compose.yml') as f:
        config = yaml.safe_load(f)

    assert 'services' in config, "No services defined in docker-compose.yml"
    assert 'db' in config['services'], "PostgreSQL service 'db' not found"
    assert 'redis' in config['services'], "Redis service 'redis' not found"
    assert 'backend' in config['services'], "Backend service not found"
    assert 'frontend' in config['services'], "Frontend service not found"


def test_docker_compose_has_health_checks():
    """Verify critical services have health checks configured."""
    with open('docker-compose.yml') as f:
        config = yaml.safe_load(f)

    # Database should have health check
    assert 'healthcheck' in config['services']['db'], \
        "PostgreSQL service missing health check"
    assert config['services']['db']['healthcheck']['test'][0] == 'CMD-SHELL', \
        "PostgreSQL health check should use CMD-SHELL"

    # Redis should have health check
    assert 'healthcheck' in config['services']['redis'], \
        "Redis service missing health check"
    assert 'redis-cli' in str(config['services']['redis']['healthcheck']['test']), \
        "Redis health check should use redis-cli"


def test_docker_compose_port_mappings():
    """Verify expected port mappings are configured."""
    with open('docker-compose.yml') as f:
        config = yaml.safe_load(f)

    # Check database port mapping (5433:5432 to avoid local conflicts)
    db_ports = config['services']['db']['ports']
    assert '5433:5432' in db_ports, "Database should map to port 5433"

    # Check backend port
    backend_ports = config['services']['backend']['ports']
    assert '8000:8000' in backend_ports, "Backend should expose port 8000"

    # Check frontend port
    frontend_ports = config['services']['frontend']['ports']
    assert '5173:5173' in frontend_ports, "Frontend should expose port 5173"

    # Check Redis port
    redis_ports = config['services']['redis']['ports']
    assert '6379:6379' in redis_ports, "Redis should expose port 6379"


def test_docker_compose_service_dependencies():
    """Verify service dependencies are correctly configured."""
    with open('docker-compose.yml') as f:
        config = yaml.safe_load(f)

    # Backend should depend on db and redis with health conditions
    backend_deps = config['services']['backend'].get('depends_on', {})
    assert 'db' in backend_deps, "Backend should depend on db"
    assert 'redis' in backend_deps, "Backend should depend on redis"
    assert backend_deps['db']['condition'] == 'service_healthy', \
        "Backend should wait for db health check"
    assert backend_deps['redis']['condition'] == 'service_healthy', \
        "Backend should wait for redis health check"

    # Frontend should depend on backend
    frontend_deps = config['services']['frontend'].get('depends_on', [])
    assert 'backend' in frontend_deps, "Frontend should depend on backend"


def test_docker_compose_volumes_defined():
    """Verify persistent volumes are defined."""
    with open('docker-compose.yml') as f:
        config = yaml.safe_load(f)

    assert 'volumes' in config, "No volumes defined"
    assert 'postgres_data' in config['volumes'], "postgres_data volume missing"
    assert 'redis_data' in config['volumes'], "redis_data volume missing"


def test_env_example_exists():
    """Verify .env.example file exists."""
    assert os.path.isfile('.env.example'), ".env.example not found"


def test_env_example_has_required_variables():
    """Verify .env.example contains all required environment variables."""
    with open('.env.example') as f:
        content = f.read()

    # Must have OPENAI_API_KEY
    assert 'OPENAI_API_KEY' in content, ".env.example missing OPENAI_API_KEY"


def test_gitmodules_exists():
    """Verify .gitmodules file exists."""
    assert os.path.isfile('.gitmodules'), ".gitmodules not found"


def test_gitmodules_has_submodules():
    """Verify .gitmodules defines both frontend and backend submodules."""
    with open('.gitmodules') as f:
        content = f.read()

    assert 'submodule "frontend"' in content or '[submodule "frontend"]' in content, \
        "Frontend submodule not defined in .gitmodules"
    assert 'submodule "backend"' in content or '[submodule "backend"]' in content, \
        "Backend submodule not defined in .gitmodules"
    assert 'bible_qa_frontend' in content, \
        "Frontend submodule URL not correct"
    assert 'bible_qa_fastapi' in content, \
        "Backend submodule URL not correct"


def test_readme_exists():
    """Verify README.md exists and contains key information."""
    assert os.path.isfile('README.md'), "README.md not found"

    with open('README.md') as f:
        content = f.read()

    # Should mention Docker Compose
    assert 'docker' in content.lower() or 'compose' in content.lower(), \
        "README should mention Docker Compose"

    # Should mention key ports
    assert '8000' in content, "README should mention backend port 8000"
    assert '5173' in content, "README should mention frontend port 5173"


def test_deploy_script_exists():
    """Verify deploy.sh script exists and is executable."""
    assert os.path.isfile('deploy.sh'), "deploy.sh not found"

    # Check if executable (on Unix-like systems)
    if os.name != 'nt':  # Skip on Windows
        stat_info = os.stat('deploy.sh')
        is_executable = bool(stat_info.st_mode & 0o111)
        assert is_executable, "deploy.sh should be executable"
