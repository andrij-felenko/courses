import asyncio
import struct
import datetime
import json
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Імітація бази даних реєстру пристроїв (Device Registry)
DEVICE_METADATA_DB = {
    1739780: {
        "serial": "MTR-2012-004812",
        "pulse_ratio_m3": 0.01,  # 1 імпульс = 10 літрів (0.01 м³)
        "tenant_id": "kyiv-vodokanal",
        "location": "Podil, District 3",
        "pending_downlink": {"cmd": 0x02, "param": 1440}  # встановити інтервал 24 години
    },
    2841092: {
        "serial": "GAS-2014-099142",
        "pulse_ratio_m3": 0.1,   # 1 імпульс = 100 літрів (0.1 м³)
        "tenant_id": "lviv-gaz",
        "location": "Sykhiv, Station 12",
        "pending_downlink": None
    }
}

def calculate_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


class LegacyProtocolBridge:
    def __init__(self, host: str = "0.0.0.0", port: int = 5005):
        self.host = host
        self.port = port

    async def handle_device_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer_addr = writer.get_extra_info("peername")
        logging.info(f"З'єднання з польовим пристроєм: {peer_addr}")

        try:
            # Очікування рівно 16 байтів із захистом від зависання каналу
            data = await asyncio.wait_for(reader.readexactly(16), timeout=10.0)
            
            magic, version = data[0], data[1]
            if magic != 0xAA or version != 0x01:
                logging.warning(f"Відхилено некоректний заголовок від {peer_addr}: magic={hex(magic)}, ver={version}")
                return

            expected_crc = struct.unpack(">H", data[14:16])[0]
            actual_crc = calculate_crc16(data[:14])
            if expected_crc != actual_crc:
                logging.warning(f"Помилка CRC від {peer_addr}: очікувалось={hex(expected_crc)}, отримано={hex(actual_crc)}")
                return

            # Розпакування полів Big-Endian
            dev_id, seq, pulses, batt_raw, flags = struct.unpack(">IHIBB", data[2:14])
            tamper = bool(flags & 0x01)
            reverse = bool(flags & 0x02)

            logging.info(f"Телеметрія v1.0: ID={dev_id}, Seq={seq}, Імпульси={pulses}, Батарея={batt_raw}")

            # Отримання паспорта приладу з реєстру
            meta = DEVICE_METADATA_DB.get(dev_id, {
                "serial": f"UNKNOWN-{dev_id}",
                "pulse_ratio_m3": 0.001,
                "tenant_id": "unassigned",
                "location": "unregistered",
                "pending_downlink": None
            })

            # Нормалізація фізичних величин
            volume_m3 = round(pulses * meta["pulse_ratio_m3"], 3)
            # Перетворення байта напруги 0..255 на вольти (255 = 3.60 В)
            voltage_v = round((batt_raw / 255.0) * 3.60, 2)

            # Формування канонічної події CloudEvents v5.0
            canonical_event = {
                "specversion": "1.0",
                "type": "com.utility.meter.reading",
                "source": f"/iot/adapters/legacy-v1/{dev_id}",
                "id": f"evt-{dev_id}-{seq}",
                "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "datacontenttype": "application/json",
                "data": {
                    "device_serial": meta["serial"],
                    "tenant_id": meta["tenant_id"],
                    "location": meta["location"],
                    "reading_m3": volume_m3,
                    "battery_volts": voltage_v,
                    "alerts": {
                        "tamper": tamper,
                        "reverse_flow": reverse
                    },
                    "telemetry_source": "legacy_bin_v1.0"
                }
            }

            # Відправка події в шину бекенду
            await self.publish_to_message_bus(canonical_event)

            # Перевірка наявності зворотних команд (Downlink)
            pending_cmd = meta.get("pending_downlink")
            if pending_cmd:
                cmd_buf = bytearray(6)
                cmd_buf[0] = 0x55
                cmd_buf[1] = pending_cmd["cmd"]
                struct.pack_into(">H", cmd_buf, 2, pending_cmd["param"])
                cmd_crc = calculate_crc16(cmd_buf[:4])
                struct.pack_into(">H", cmd_buf, 4, cmd_crc)

                writer.write(cmd_buf)
                await writer.drain()
                logging.info(f"Відправлено Downlink-команду для {dev_id}: {cmd_buf.hex()}")
                meta["pending_downlink"] = None  # Скидання виконаної команди

        except asyncio.TimeoutError:
            logging.warning(f"Таймаут прийому даних від {peer_addr}")
        except asyncio.IncompleteReadError:
            logging.warning(f"Пристрій {peer_addr} розірвав зв'язок до передачі 16 байтів")
        except Exception as e:
            logging.error(f"Виняткова ситуація під час обробки: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def publish_to_message_bus(self, event: Dict[str, Any]):
        # У виробничому середовищі: відправка у топік Kafka через aiokafka
        payload_str = json.dumps(event, ensure_ascii=False)
        logging.info(f"-> [KAFKA / EVENT BUS] Опубліковано: {payload_str}")

    async def run(self):
        server = await asyncio.start_server(self.handle_device_connection, self.host, self.port)
        logging.info(f"Шлюз сумісності запущено на порту {self.port}...")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    bridge = LegacyProtocolBridge()
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        logging.info("Шлюз зупинено.")
