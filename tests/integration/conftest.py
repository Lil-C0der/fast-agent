import importlib
import os
from pathlib import Path

import pytest

from mcp_agent.core.fastagent import FastAgent


# Keep the auto-cleanup fixture
@pytest.fixture(scope="function", autouse=True)
def cleanup_event_bus():
    """Reset the AsyncEventBus between tests using its reset method"""
    # Run the test
    yield

    # Reset the AsyncEventBus after each test
    try:
        # Import the module with the AsyncEventBus
        transport_module = importlib.import_module("mcp_agent.logging.transport")
        AsyncEventBus = getattr(transport_module, "AsyncEventBus", None)

        # Call the reset method if available
        if AsyncEventBus and hasattr(AsyncEventBus, "reset"):
            AsyncEventBus.reset()
    except Exception:
        pass


# Set the project root directory for tests
@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory as a Path object"""
    # Go up from tests/e2e directory to find project root
    return Path(__file__).parent.parent.parent


# Fixture to set the current working directory for tests
@pytest.fixture
def set_cwd(project_root):
    """Change to the project root directory during tests"""
    # Save the original working directory
    original_cwd = os.getcwd()

    # Change to the project root directory
    os.chdir(project_root)

    # Run the test
    yield

    # Restore the original working directory
    os.chdir(original_cwd)


# Add a fixture that uses the test file's directory
@pytest.fixture
def fast_agent(request):
    """
    Creates a FastAgent with config from the test file's directory.
    Automatically changes working directory to match the test file location.
    """
    # Get the directory where the test file is located
    test_module = request.module.__file__
    test_dir = os.path.dirname(test_module)

    # Save original directory
    original_cwd = os.getcwd()

    # Change to the test file's directory
    os.chdir(test_dir)

    # Create agent with local config
    agent = FastAgent(
        "Test Agent",
        config_path="fastagent.config.yaml",  # Uses local config in test directory
        ignore_unknown_args=True,
    )

    # Provide the agent
    yield agent

    # Restore original directory
    os.chdir(original_cwd)
