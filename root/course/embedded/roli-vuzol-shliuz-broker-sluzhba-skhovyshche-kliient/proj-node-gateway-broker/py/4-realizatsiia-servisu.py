import struct
import time
import json
import socket
import threading
import paho.mqtt.client as mqtt

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
GATEWAY_ID = "gw_edge_01"
TENANT_ID = "org_alpha"

FRAME_FORMAT = "<BBHIhHBBH"
FRAME_SIZE = struct.calcsize(FRAME_FORMAT) # 16 байтів


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


class GatewayBridge:
    def __init__(self):
        self.last_reported = {}  # node_id -> {"temp": float, "ts": float}
        self.mqtt_client = mqtt.Client(client_id=f"gateway_{GATEWAY_ID}")
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

    def on_mqtt_connect(self, client, userdata, flags, rc):
        print(f"[GW] Підключено до MQTT брокера з кодом rc={rc}")
        # Підписуємося на команди для всіх вузлів цього шлюзу
        sub_topic = f"command/{TENANT_ID}/{GATEWAY_ID}/+"
        client.subscribe(sub_topic, qos=1)
        print(f"[GW] Підписка на топік команд: {sub_topic}")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic_parts = msg.topic.split("/")
            node_id_str = topic_parts[-1]
            node_id = int(node_id_str.replace("node_", ""))
            cmd_id = payload.get("cmd_id", 0x10)
            val = payload.get("val", 0)

            print(f"[GW] Отримано команду від брокера для Node {node_id}: cmd={cmd_id}, val={val}")
            # Формування бінарного кадру команди для надсилання у радіоканал
            cmd_data = struct.pack("<BBHIHB", 0xAA, 0x02, node_id, 0, cmd_id, val)
            cmd_crc = crc16_ccitt(cmd_data)
            full_frame = cmd_data + struct.pack("<H", cmd_crc)
            # Тут викликається фізична відправка у UART/радіотрансивер
            print(f"[GW -> Node] Надіслано {len(full_frame)} байтів у польовий канал")
        except Exception as e:
            print(f"[GW] Помилка обробки команди: {e}")

    def should_forward_telemetry(self, node_id: int, temp_c: float) -> bool:
        """Локальна deadband-фільтрація: зменшення трафіку в хмару."""
        now = time.time()
        if node_id not in self.last_reported:
            self.last_reported[node_id] = {"temp": temp_c, "ts": now}
            return True

        last = self.last_reported[node_id]
        delta_temp = abs(temp_c - last["temp"])
        delta_time = now - last["ts"]

        # Відправляємо, якщо температура змінилася на >= 0.2 C або минуло 60 с (heartbeat)
        if delta_temp >= 0.2 or delta_time >= 60.0:
            self.last_reported[node_id] = {"temp": temp_c, "ts": now}
            return True
        return False

    def process_incoming_frame(self, raw_bytes: bytes):
        if len(raw_bytes) != FRAME_SIZE:
            return

        magic, f_type, node_id, seq, temp_raw, bat_mv, flags, res, rx_crc = struct.unpack(
            FRAME_FORMAT, raw_bytes
        )

        if magic != 0xAA or f_type != 0x01:
            print(f"[GW] Невалідний заголовок кадру: magic=0x{magic:02X}, type={f_type}")
            return

        # Перевірка CRC
        payload_to_check = raw_bytes[:-2]
        expected_crc = crc16_ccitt(payload_to_check)
        if rx_crc != expected_crc:
            print(f"[GW] CRC mismatch для Node {node_id}: rx=0x{rx_crc:04X}, calc=0x{expected_crc:04X}")
            return

        temp_c = temp_raw / 100.0

        if not self.should_forward_telemetry(node_id, temp_c):
            print(f"[GW] Deadband: вимір Node {node_id} ({temp_c:.2f} C) відфільтровано локально")
            return

        # Збагачення метаданими та пакування в JSON
        telemetry_doc = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "gateway_id": GATEWAY_ID,
            "node_id": node_id,
            "seq": seq,
            "metrics": {
                "temperature": temp_c,
                "battery_mv": bat_mv,
                "relay_status": bool(flags & 0x01),
            },
            "rssi_dbm": -68, # Додається радіомодулем шлюзу
        }

        topic = f"telemetry/{TENANT_ID}/{GATEWAY_ID}/node_{node_id}"
        self.mqtt_client.publish(topic, json.dumps(telemetry_doc), qos=1)
        print(f"[GW -> MQTT] Опубліковано в {topic}: {temp_c:.2f} C, {bat_mv} mV")

    def run(self, host="127.0.0.1", port=9000):
        self.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        self.mqtt_client.loop_start()

        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind((host, port))
        print(f"[GW] Шлюз слухає UDP-канал польових вузлів на {host}:{port}...")

        try:
            while True:
                data, addr = server.recvfrom(128)
                self.process_incoming_frame(data)
        except KeyboardInterrupt:
            print("[GW] Зупинка шлюзу...")
        finally:
            self.mqtt_client.loop_stop()
            server.close()


if __name__ == "__main__":
    bridge = GatewayBridge()
    bridge.run()
