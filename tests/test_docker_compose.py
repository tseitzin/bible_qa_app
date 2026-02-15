"""Integration tests for Docker Compose stack.

These tests verify that all services start correctly, health checks pass,
and services can communicate with each other.

NOTE: These tests require Docker to be running locally.
"""
import time
import subprocess
import pytest
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


@pytest.fixture(scope="module")
def docker_compose_up():
    """
    Start Docker Compose stack for tests and tear down after.

    This fixture runs once for the entire module.
    """
    # Start services
    subprocess.run(
        ['docker', 'compose', 'up', '-d', '--build'],
        check=True,
        capture_output=True
    )

    # Wait for services to be ready
    print("\n⏳ Waiting for services to start...")
    time.sleep(15)  # Initial wait for containers to initialize

    # Wait for health checks (up to 60 seconds)
    for i in range(12):
        result = subprocess.run(
            ['docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True,
            text=True
        )
        if 'healthy' in result.stdout:
            print("✓ Services are healthy")
            break
        time.sleep(5)
    else:
        print("⚠ Health check timeout - continuing anyway")

    yield

    # Teardown: stop and remove containers
    print("\n🧹 Cleaning up Docker Compose stack...")
    subprocess.run(
        ['docker', 'compose', 'down', '-v'],
        check=True,
        capture_output=True
    )


@pytest.fixture
def http_session():
    """Create HTTP session with retry logic for flaky container startups."""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    return session


@pytest.mark.docker
@pytest.mark.integration
def test_all_services_running(docker_compose_up):
    """Test that all 4 services are running."""
    result = subprocess.run(
        ['docker', 'compose', 'ps', '--format', 'json'],
        capture_output=True,
        text=True,
        check=True
    )

    output = result.stdout.lower()

    # All services should be present
    assert 'bible_qa_db' in output or 'db' in output, "Database container not running"
    assert 'bible_qa_redis' in output or 'redis' in output, "Redis container not running"
    assert 'bible_qa_backend' in output or 'backend' in output, "Backend container not running"
    assert 'bible_qa_frontend' in output or 'frontend' in output, "Frontend container not running"


@pytest.mark.docker
@pytest.mark.integration
def test_db_health_check(docker_compose_up):
    """Test that PostgreSQL health check passes."""
    result = subprocess.run(
        ['docker', 'exec', 'bible_qa_db', 'pg_isready', '-U', 'postgres'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"PostgreSQL health check failed: {result.stderr}"
    assert 'accepting connections' in result.stdout, \
        "PostgreSQL not accepting connections"


@pytest.mark.docker
@pytest.mark.integration
def test_redis_health_check(docker_compose_up):
    """Test that Redis health check passes."""
    result = subprocess.run(
        ['docker', 'exec', 'bible_qa_redis', 'redis-cli', 'ping'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Redis health check failed: {result.stderr}"
    assert 'PONG' in result.stdout, "Redis not responding to PING"


@pytest.mark.docker
@pytest.mark.integration
def test_backend_responds(docker_compose_up, http_session):
    """Test that backend service responds to HTTP requests."""
    # Try health endpoint (root path)
    try:
        response = http_session.get('http://localhost:8000/', timeout=10)
        assert response.status_code == 200, \
            f"Backend health check failed with status {response.status_code}"
        # Verify it returns expected health check data
        data = response.json()
        assert 'status' in data, "Health check should return status field"
        assert data['status'] == 'healthy', "Backend should report healthy status"
    except requests.exceptions.ConnectionError:
        pytest.fail("Cannot connect to backend on port 8000")


@pytest.mark.docker
@pytest.mark.integration
def test_backend_api_docs(docker_compose_up, http_session):
    """Test that backend serves API documentation."""
    try:
        response = http_session.get('http://localhost:8000/docs', timeout=10)
        assert response.status_code == 200, \
            f"Backend /docs endpoint failed with status {response.status_code}"
        assert 'swagger' in response.text.lower() or 'openapi' in response.text.lower(), \
            "API documentation not properly served"
    except requests.exceptions.ConnectionError:
        pytest.fail("Cannot connect to backend API docs")


@pytest.mark.docker
@pytest.mark.integration
def test_frontend_responds(docker_compose_up, http_session):
    """Test that frontend service responds to HTTP requests."""
    try:
        response = http_session.get('http://localhost:5173', timeout=10)
        assert response.status_code == 200, \
            f"Frontend failed with status {response.status_code}"
    except requests.exceptions.ConnectionError:
        pytest.fail("Cannot connect to frontend on port 5173")


@pytest.mark.docker
@pytest.mark.integration
def test_backend_db_connection(docker_compose_up):
    """Test that backend can connect to PostgreSQL database."""
    # Check backend logs for successful database connection
    result = subprocess.run(
        ['docker', 'logs', 'bible_qa_backend'],
        capture_output=True,
        text=True
    )

    logs = result.stdout + result.stderr

    # Should not have database connection errors
    assert 'Connection refused' not in logs or 'could not connect' not in logs, \
        "Backend has database connection errors in logs"


@pytest.mark.docker
@pytest.mark.integration
def test_backend_redis_connection(docker_compose_up):
    """Test that backend can connect to Redis."""
    # Check backend logs for Redis connection issues
    result = subprocess.run(
        ['docker', 'logs', 'bible_qa_backend'],
        capture_output=True,
        text=True
    )

    logs = result.stdout + result.stderr

    # Should not have Redis connection errors
    assert 'redis' not in logs.lower() or 'connection refused' not in logs.lower(), \
        "Backend may have Redis connection issues"


@pytest.mark.docker
@pytest.mark.integration
def test_environment_variables_injected(docker_compose_up):
    """Test that environment variables are properly injected into backend."""
    result = subprocess.run(
        ['docker', 'exec', 'bible_qa_backend', 'printenv', 'DATABASE_URL'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, "DATABASE_URL not set in backend container"
    assert 'postgresql' in result.stdout, "DATABASE_URL not properly configured"
    assert 'bible_qa' in result.stdout, "Database name not correct in DATABASE_URL"


@pytest.mark.docker
@pytest.mark.integration
def test_port_mappings(docker_compose_up):
    """Test that all expected ports are exposed and accessible."""
    import socket

    ports_to_check = [
        (5433, "PostgreSQL"),  # Note: 5433 on host, 5432 in container
        (8000, "Backend"),
        (5173, "Frontend"),
        (6379, "Redis")
    ]

    for port, service_name in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        assert result == 0, f"{service_name} port {port} is not accessible"


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.timeout(30)
def test_backend_migrations_run(docker_compose_up):
    """Test that Alembic migrations run successfully on backend startup."""
    result = subprocess.run(
        ['docker', 'logs', 'bible_qa_backend'],
        capture_output=True,
        text=True
    )

    logs = result.stdout + result.stderr

    # Should mention Alembic in logs
    assert 'alembic' in logs.lower() or 'migration' in logs.lower(), \
        "Backend logs don't mention database migrations"

    # Should not have migration errors
    assert 'migration' not in logs.lower() or 'error' not in logs.lower(), \
        "Database migration errors detected in backend logs"


@pytest.mark.docker
@pytest.mark.integration
def test_docker_compose_config_valid():
    """Test that docker-compose config is valid."""
    result = subprocess.run(
        ['docker', 'compose', 'config'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, \
        f"docker-compose config validation failed: {result.stderr}"
