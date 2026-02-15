"""Tests for validating deployment scripts and processes."""
import os
import subprocess
import pytest


@pytest.mark.deployment
def test_deploy_script_exists():
    """Verify deploy.sh file exists."""
    assert os.path.isfile('deploy.sh'), "deploy.sh not found"


@pytest.mark.deployment
def test_deploy_script_syntax():
    """Validate deploy.sh has valid bash syntax."""
    result = subprocess.run(
        ['bash', '-n', 'deploy.sh'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Bash syntax error in deploy.sh: {result.stderr}"


@pytest.mark.deployment
def test_deploy_script_has_shebang():
    """Verify deploy.sh has proper shebang."""
    with open('deploy.sh') as f:
        first_line = f.readline().strip()

    assert first_line.startswith('#!'), "deploy.sh missing shebang"
    assert 'bash' in first_line, "deploy.sh shebang should specify bash"


@pytest.mark.deployment
def test_deploy_script_mentions_heroku():
    """Verify deployment script is configured for Heroku."""
    with open('deploy.sh') as f:
        content = f.read()

    assert 'heroku' in content.lower(), "deploy.sh should mention Heroku"


@pytest.mark.deployment
def test_deploy_script_has_menu_options():
    """Verify deployment script has expected menu choices."""
    with open('deploy.sh') as f:
        content = f.read()

    # Should have options 1-4
    assert '1)' in content, "deploy.sh missing option 1"
    assert '2)' in content, "deploy.sh missing option 2"
    assert '3)' in content, "deploy.sh missing option 3"
    assert '4)' in content, "deploy.sh missing option 4 (exit)"


@pytest.mark.deployment
def test_deploy_script_handles_backend():
    """Verify script has backend deployment logic."""
    with open('deploy.sh') as f:
        content = f.read()

    assert 'backend' in content.lower(), "deploy.sh should reference backend"
    assert 'cd backend' in content, "deploy.sh should navigate to backend directory"


@pytest.mark.deployment
def test_deploy_script_handles_frontend():
    """Verify script has frontend deployment logic."""
    with open('deploy.sh') as f:
        content = f.read()

    assert 'frontend' in content.lower(), "deploy.sh should reference frontend"
    assert 'cd frontend' in content, "deploy.sh should navigate to frontend directory"


@pytest.mark.deployment
def test_deploy_script_checks_heroku_cli():
    """Verify script checks for Heroku CLI."""
    with open('deploy.sh') as f:
        content = f.read()

    # Should check if heroku command exists
    assert 'command -v heroku' in content or 'which heroku' in content, \
        "deploy.sh should check for Heroku CLI"


@pytest.mark.deployment
def test_deploy_script_sets_environment_variables():
    """Verify script configures environment variables."""
    with open('deploy.sh') as f:
        content = f.read()

    # Should set OPENAI_API_KEY
    assert 'OPENAI_API_KEY' in content, \
        "deploy.sh should configure OPENAI_API_KEY"

    # Should set allowed origins
    assert 'ALLOWED_ORIGINS' in content or 'allowed' in content.lower(), \
        "deploy.sh should configure CORS origins"


@pytest.mark.deployment
def test_deploy_script_has_error_handling():
    """Verify script has basic error handling."""
    with open('deploy.sh') as f:
        content = f.read()

    # Should have 'set -e' for exit on error
    assert 'set -e' in content, "deploy.sh should use 'set -e' for error handling"
