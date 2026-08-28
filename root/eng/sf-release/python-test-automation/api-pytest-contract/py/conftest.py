# conftest.py у корені набору
import pytest


def pytest_addoption(parser):
    parser.addoption("--dev", action="store", default=None,
                     help="послідовний порт плати, напр. /dev/ttyUSB0")
    parser.addoption("--allow-empty", action="store_true", default=False,
                     help="порожня вибірка не є приводом валити прогін")


def pytest_configure(config):
    config.addinivalue_line("markers", "hardware: потребує підключеної плати")


def pytest_collection_modifyitems(session, config, items):
    if config.getoption("--dev"):
        return
    skip = pytest.mark.skip(reason="плату не вказано: запустіть із --dev=/dev/ttyUSB0")
    for item in items:
        if "hardware" in item.keywords:
            item.add_marker(skip)
