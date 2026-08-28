import subprocess
import pytest
import socket
import time

# Перелік версій бінарників, зібраних у процесі релізів
SUPPORTED_VERSIONS = ["v1.0", "v1.1", "v2.0", "v2.1"]

class BinaryNodeInstance:
    """Керує життєвим циклом скомпільованого бінарника прошивки конкретної версії."""
    def __init__(self, version: str, port: int):
        self.version = version
        self.port = port
        self.process = None

    def start(self):
        binary_path = f"./bin/firmware_node_{self.version}"
        self.process = subprocess.Popen(
            [binary_path, "--port", str(self.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(0.05) # Очікування відкриття сокета

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

@pytest.mark.parametrize("node_ver", SUPPORTED_VERSIONS)
@pytest.mark.parametrize("server_ver", SUPPORTED_VERSIONS)
def test_cross_version_compatibility(node_ver: str, server_ver: str):
    """
    Матричний тест: запускає клієнт версії node_ver та перевіряє 
    обмін із сервером версії server_ver.
    """
    port = 19000 + int(node_ver.replace("v", "").replace(".", "")) * 10
    node = BinaryNodeInstance(node_ver, port)
    node.start()

    try:
        # 1. Підключаємо тестовий стенд як сервер версії server_ver
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", port))
        sock.settimeout(1.0)

        # 2. Формуємо кадр опитування стану згідно зі специфікацією server_ver
        request_packet = build_status_request(version=server_ver)
        sock.sendall(request_packet)

        # 3. Отримуємо відповідь від вузла
        response_raw = sock.recv(512)
        assert len(response_raw) > 0, f"Node {node_ver} dropped connection for server {server_ver}"

        # 4. Валідуємо семантику відповіді з урахуванням мажорних версій
        node_major = int(node_ver[1])
        server_major = int(server_ver[1])

        if node_major == server_major:
            parsed = parse_telemetry_response(response_raw, expected_version=server_ver)
            assert parsed.is_valid, f"Failed parsing {node_ver} response on {server_ver} server"
            assert parsed.voltage_mv > 0
        else:
            # При мажорній розбіжності вузол повинен відкинути запит або відповісти кодом несумісності
            assert is_incompatibility_rejected(response_raw), \
                f"Node {node_ver} accepted incompatible major frame from server {server_ver}"

        sock.close()
    finally:
        node.stop()
