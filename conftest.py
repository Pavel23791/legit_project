import pytest

def pytest_addoption(parser):
    parser.addoption("--username", action="store", default="default_username")
    parser.addoption("--password", action="store", default="default_password")

@pytest.fixture
def username(request):
    return request.config.getoption("--username")

@pytest.fixture
def password(request):
    return request.config.getoption("--password")
