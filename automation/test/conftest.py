import pytest
import yaml


def pytest_addoption(parser):
    parser.addoption(
        "--testbed", action="store", default='./resources/testbeds/local_host.yml',
        help="defines the environment being tested"
    )
    parser.addoption(
        "--validationConfig", action="store", default='./resources/validation/validation_config.yml',
        help="defines validation used by some tests"
    )


@pytest.fixture(scope="session")
def env_config(request):
    testbed_file = request.config.getoption("--testbed")
    with open(testbed_file, 'r') as f:
        env_config = yaml.safe_load(f)
        yield env_config


@pytest.fixture(scope="session")
def validation_config(request):
    validation_config_file = request.config.getoption("--validationConfig")
    with open(validation_config_file, 'r') as f:
        validation_config = yaml.safe_load(f)
        yield validation_config

