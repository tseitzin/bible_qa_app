"""Tests for validating git submodules are properly configured."""
import os
import subprocess
import pytest


def test_submodules_initialized():
    """Ensure git submodules are initialized and not empty."""
    # Check directories exist
    assert os.path.isdir('frontend'), "Frontend submodule directory not found"
    assert os.path.isdir('backend'), "Backend submodule directory not found"

    # Check they're not empty
    assert os.path.isfile('frontend/package.json'), \
        "Frontend submodule appears empty (no package.json)"
    assert os.path.isfile('backend/requirements.txt'), \
        "Backend submodule appears empty (no requirements.txt)"


def test_frontend_submodule_structure():
    """Verify frontend submodule has expected structure."""
    # Check key directories
    assert os.path.isdir('frontend/src'), "Frontend missing src/ directory"
    assert os.path.isdir('frontend/src/tests'), "Frontend missing src/tests/ directory"

    # Check key files
    assert os.path.isfile('frontend/vite.config.js'), "Frontend missing vite.config.js"
    assert os.path.isfile('frontend/Dockerfile'), "Frontend missing Dockerfile"


def test_backend_submodule_structure():
    """Verify backend submodule has expected structure."""
    # Check key directories
    assert os.path.isdir('backend/app'), "Backend missing app/ directory"
    assert os.path.isdir('backend/tests'), "Backend missing tests/ directory"
    assert os.path.isdir('backend/alembic'), "Backend missing alembic/ directory"

    # Check key files
    assert os.path.isfile('backend/Dockerfile'), "Backend missing Dockerfile"
    assert os.path.isfile('backend/pyproject.toml'), "Backend missing pyproject.toml"


def test_frontend_has_ci_workflow():
    """Verify frontend submodule has GitHub Actions CI configured."""
    ci_file = 'frontend/.github/workflows/ci.yml'
    assert os.path.isfile(ci_file), "Frontend missing CI workflow file"


def test_backend_has_ci_workflow():
    """Verify backend submodule has GitHub Actions CI configured."""
    ci_file = 'backend/.github/workflows/ci.yml'
    assert os.path.isfile(ci_file), "Backend missing CI workflow file"


def test_submodule_git_config():
    """Verify .gitmodules is properly configured."""
    result = subprocess.run(
        ['git', 'config', '--file', '.gitmodules', '--get-regexp', 'submodule'],
        capture_output=True,
        text=True,
        check=False
    )

    # Should have configuration for both submodules
    output = result.stdout
    assert 'frontend' in output, ".gitmodules missing frontend configuration"
    assert 'backend' in output, ".gitmodules missing backend configuration"
    assert 'bible_qa_frontend' in output, "Frontend submodule URL incorrect"
    assert 'bible_qa_fastapi' in output, "Backend submodule URL incorrect"


def test_submodules_on_commits():
    """Verify submodules are pointing to specific commits (not detached)."""
    # This is informational - submodules should be at specific commits
    frontend_result = subprocess.run(
        ['git', '-C', 'frontend', 'rev-parse', 'HEAD'],
        capture_output=True,
        text=True,
        check=False
    )

    backend_result = subprocess.run(
        ['git', '-C', 'backend', 'rev-parse', 'HEAD'],
        capture_output=True,
        text=True,
        check=False
    )

    # Should successfully get commit hashes
    assert frontend_result.returncode == 0, "Cannot get frontend commit"
    assert backend_result.returncode == 0, "Cannot get backend commit"
    assert len(frontend_result.stdout.strip()) == 40, "Invalid frontend commit hash"
    assert len(backend_result.stdout.strip()) == 40, "Invalid backend commit hash"


def test_frontend_has_tests():
    """Verify frontend submodule has test files."""
    # Check for test directories
    test_dirs = [
        'frontend/src/tests',
        'frontend/tests'
    ]

    has_tests = any(os.path.isdir(d) for d in test_dirs)
    assert has_tests, "Frontend submodule missing test directories"


def test_backend_has_tests():
    """Verify backend submodule has test files."""
    assert os.path.isdir('backend/tests'), "Backend missing tests/ directory"

    # Should have actual test files
    test_files = [f for f in os.listdir('backend/tests') if f.startswith('test_')]
    assert len(test_files) > 0, "Backend tests/ directory is empty"


def test_submodule_urls_are_https():
    """Verify submodule URLs use HTTPS (not SSH) for CI compatibility."""
    with open('.gitmodules') as f:
        content = f.read()

    # URLs should use https://
    assert 'https://github.com/' in content, \
        "Submodule URLs should use HTTPS for CI compatibility"

    # Should not use SSH
    assert 'git@github.com' not in content, \
        "Submodule URLs should not use SSH (incompatible with CI)"
