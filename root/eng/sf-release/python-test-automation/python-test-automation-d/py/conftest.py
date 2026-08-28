# conftest.py — фікстури, видимі всім тестам цієї теки й нижче
import pytest
from serial import Serial

@pytest.fixture(scope="session")
def port(request):
    dev = request.config.getoption("--dev")          # напр. /dev/ttyUSB0
    s = Serial(dev, baudrate=115200, timeout=0.2)
    yield s                                          # усе після yield — прибирання
    s.close()

@pytest.fixture
def device(port):                                    # залежить від фікстури port
    reset(port)                                      # кожен тест — з відомого стану
    wait_ready(port, timeout=3.0)
    yield Device(port)
    dump_logs(port)                                  # виконається й після падіння
