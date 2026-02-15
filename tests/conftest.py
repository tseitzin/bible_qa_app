"""Pytest configuration and fixtures for main app integration tests."""
import pytest
import os
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load .env file for all tests."""
    load_dotenv()
    # Ensure test environment has required variables (or use dummy for CI)
    if not os.getenv('OPENAI_API_KEY'):
        # Set a dummy key for CI environments without secrets
        os.environ['OPENAI_API_KEY'] = 'sk-test-dummy-key-for-ci'


@pytest.fixture
def docker_compose_project_name():
    """Use unique project name for Docker Compose in tests."""
    return "bible_qa_test"


@pytest.fixture
def compose_file():
    """Path to docker-compose.yml."""
    return "docker-compose.yml"
