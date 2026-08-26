# ⚙️ Програмний міст для пристроїв старих версій: розбір бінарних кадрів і трансляція в шину подій

Цей проєкт демонструє повну інженерну реалізацію адаптера сумісності (Legacy Ingestion Proxy) для підтримки промислових лічильників та автономних телеметричних датчиків першого покоління (v1.0), розгорнутих понад десять років тому. Програмний комплекс розв'язує задачу двох світів: на системному рівні він забезпечує безпечний та швидкий розбір сирих компактних бінарних кадрів, верифікацію контрольної суми CRC-16 та формування зворотних команд керування; на серверному рівні він збагачує телеметрію метаданими з реєстру обладнання, перераховує сирі лічильні імпульси у фізичні величини за калібрувальними кривими та транслює результат у канонічну хмарну шину подій у форматі CloudEvents JSON.

### 1. Архітектура протоколу та дизайн бінарного кадру v1.0

Польові лічильники першого покоління розроблялися в умовах жорсткого дефіциту обчислювальних ресурсів та пам'яті (типовий мікроконтролер Texas Instruments MSP430 або STM32L0 з 32 КБ Flash та 4 КБ RAM). Передавати текстовий JSON чи навіть бінарний CBOR через модем 2G/GPRS було неприпустимо дорого з погляду трафіку та енергоспоживання. Тому протокол v1.0 використовує щільно упакований 16-байтний бінарний кадр із фіксованим розташуванням полів у мережевому порядку байтів (Big-Endian).

Використання фіксованої довжини усуває потребу в динамічному виділенні пам'яті під час прийому та передачі: розмір статичного буфера відомий на етапі компіляції. Усі багатобайтні цілі числа вирівняні за старшим байтом, що унеможливлює неоднозначність інтерпретації на процесорах із різним порядком байтів (Little-Endian мікроконтролери проти Big-Endian мережевих стеків).

| Зсув (байти) | Розмір | Поле | Тип | Призначення та діапазон значень |
|---|---|---|---|---|
| `0` | 1 байт | `magic` | `uint8_t` | Преамбула кадру. Стале значення `0xAA` для синхронізації та відсікання випадкового мережевого шуму |
| `1` | 1 байт | `version` | `uint8_t` | Версія бінарного формату. Для першого покоління завжди дорівнює `0x01` |
| `2..5` | 4 байти | `device_id` | `uint32_t` | Унікальний числовий ідентифікатор лічильника у виробничій базі даних (0..4294967295) |
| `6..7` | 2 байти | `seq_num` | `uint16_t` | Монотонний лічильник сеансів зв'язку (0..65535). Дозволяє виявляти втрачені пакети та спроби повтору |
| `8..11` | 4 байти | `raw_pulses` | `uint32_t` | Накопичена кількість імпульсів герконового або індуктивного датчика обертання крильчатки |
| `12` | 1 байт | `battery_raw` | `uint8_t` | Напруга елемента живлення. Кодується значенням 0..255, де 255 відповідає напрузі 3.60 В свіжої батареї |
| `13` | 1 байт | `flags` | `uint8_t` | Бітова маска аварійних станів: біт 0 — тривога розкриття корпусу (tamper), біт 1 — зворотний потік |
| `14..15` | 2 байти | `crc16` | `uint16_t` | Контрольна сума CRC-16-CCITT (поліном `0x1021`, початкове значення `0xFFFF`), порахована для байтів 0..13 |

Зворотний канал керування (Downlink) призначений для передачі наказів лічильнику безпосередньо під час відкритого сеансу зв'язку. Довжина кадру команди становить рівно 6 байтів:

| Зсув (байти) | Розмір | Поле | Тип | Призначення |
|---|---|---|---|---|
| `0` | 1 байт | `magic` | `uint8_t` | Преамбула команди. Стале значення `0x55` |
| `1` | 1 байт | `cmd_type` | `uint8_t` | Код операції: `0x01` — перекрити аварійний клапан, `0x02` — встановити період виходу на зв'язок |
| `2..3` | 2 байти | `param` | `uint16_t` | Числовий параметр команди (наприклад, період у хвилинах від 1 до 65535) |
| `4..5` | 2 байти | `crc16` | `uint16_t` | Контрольна сума CRC-16-CCITT байтів 0..3 |

Для 16-байтних пакетів алгоритм CRC-16-CCITT забезпечує гарантовану відстань Хеммінга `d = 4`: будь-які три довільні бітові помилки в кадрі виявляються на 100%. Ймовірність пропуску випадкового пошкодження пакету становить менше ніж `1 / 65536` (`0.0015%`), що є достатнім для надійного прийому телеметрії через нестабільні стільникові мережі.

### 2. Системний парсер та пакувальник бінарних кадрів

Нижче наведено модуль розбору, валідації та пакування пакетів. Модуль спроєктовано з дотриманням жорстких вимог безпеки пам'яті: функція перевіряє межі вхідного масиву до звернення до будь-якого байта, не виконує динамічного виділення пам'яті (`malloc`/`new`) і забезпечує лінійну складність розбору `O(N)`.

Зверніть увагу на спосіб вилучення полів: замість прямого накладання структури C через приведення покажчика `(legacy_telemetry_t*)buf` (що призводить до невизначеної поведінки Undefined Behavior через різницю у вирівнюванні пам'яті та порядок байтів CPU), парсер вилучає байти індивідуальними побітовими зсувами. Це гарантує ідентичну поведінку на будь-якій архітектурі: x86_64, ARM64 або RISC-V.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define LEGACY_FRAME_MAGIC    0xAA
#define LEGACY_FRAME_VERSION  0x01
#define LEGACY_FRAME_SIZE     16

#define LEGACY_CMD_MAGIC      0x55
#define LEGACY_CMD_SIZE       6

typedef struct {
    uint32_t device_id;
    uint16_t seq_num;
    uint32_t raw_pulses;
    uint8_t  battery_raw;
    bool     tamper_alarm;
    bool     reverse_flow;
} legacy_telemetry_t;

typedef enum {
    PARSE_OK = 0,
    PARSE_ERR_BUFFER_TOO_SMALL,
    PARSE_ERR_INVALID_MAGIC,
    PARSE_ERR_UNSUPPORTED_VERSION,
    PARSE_ERR_CRC_MISMATCH
} parse_result_t;

/* Обчислення контрольної суми CRC-16-CCITT (Поліном 0x1021, init 0xFFFF) */
static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

/* Безпечне вилучення 16-бітного цілого в форматі Big-Endian */
static inline uint16_t read_be16(const uint8_t *p) {
    return (uint16_t)((p[0] << 8) | p[1]);
}

/* Безпечне вилучення 32-бітного цілого в форматі Big-Endian */
static inline uint32_t read_be32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) |
           ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8)  |
           ((uint32_t)p[3]);
}

/* Безпечний запис 16-бітного цілого в форматі Big-Endian */
static inline void write_be16(uint8_t *p, uint16_t val) {
    p[0] = (uint8_t)(val >> 8);
    p[1] = (uint8_t)(val & 0xFF);
}

parse_result_t legacy_parse_telemetry(const uint8_t *buf, size_t len, legacy_telemetry_t *out) {
    if (len < LEGACY_FRAME_SIZE) {
        return PARSE_ERR_BUFFER_TOO_SMALL;
    }

    if (buf[0] != LEGACY_FRAME_MAGIC) {
        return PARSE_ERR_INVALID_MAGIC;
    }

    if (buf[1] != LEGACY_FRAME_VERSION) {
        return PARSE_ERR_UNSUPPORTED_VERSION;
    }

    /* Верифікація CRC16 для байтів заголовка та корисного навантаження (0..13) */
    uint16_t expected_crc = read_be16(&buf[14]);
    uint16_t actual_crc = crc16_ccitt(buf, 14);
    if (expected_crc != actual_crc) {
        return PARSE_ERR_CRC_MISMATCH;
    }

    /* Розпакування полів без ризику непарного вирівнювання пам'яті */
    out->device_id   = read_be32(&buf[2]);
    out->seq_num     = read_be16(&buf[6]);
    out->raw_pulses  = read_be32(&buf[8]);
    out->battery_raw = buf[12];
    
    uint8_t flags    = buf[13];
    out->tamper_alarm = (flags & 0x01) != 0;
    out->reverse_flow = (flags & 0x02) != 0;

    return PARSE_OK;
}

bool legacy_build_command(uint8_t cmd_type, uint16_t param, uint8_t *out_buf, size_t out_capacity) {
    if (out_capacity < LEGACY_CMD_SIZE) {
        return false;
    }

    out_buf[0] = LEGACY_CMD_MAGIC;
    out_buf[1] = cmd_type;
    write_be16(&out_buf[2], param);

    uint16_t crc = crc16_ccitt(out_buf, 4);
    write_be16(&out_buf[4], crc);

    return true;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <array>

namespace legacy_v1 {

constexpr uint8_t FRAME_MAGIC   = 0xAA;
constexpr uint8_t FRAME_VERSION = 0x01;
constexpr size_t  FRAME_SIZE    = 16;

constexpr uint8_t CMD_MAGIC     = 0x55;
constexpr size_t  CMD_SIZE      = 6;

struct TelemetryData {
    uint32_t device_id{};
    uint16_t seq_num{};
    uint32_t raw_pulses{};
    uint8_t  battery_raw{};
    bool     tamper_alarm{};
    bool     reverse_flow{};
};

enum class ParseError {
    BufferTooSmall,
    InvalidMagic,
    UnsupportedVersion,
    CrcMismatch
};

/* Обчислення CRC-16-CCITT під час компіляції (constexpr) або у рантаймі */
constexpr uint16_t crc16_ccitt(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

static inline uint16_t read_be16(std::span<const uint8_t, 2> p) noexcept {
    return static_cast<uint16_t>((p[0] << 8) | p[1]);
}

static inline uint32_t read_be32(std::span<const uint8_t, 4> p) noexcept {
    return (static_cast<uint32_t>(p[0]) << 24) |
           (static_cast<uint32_t>(p[1]) << 16) |
           (static_cast<uint32_t>(p[2]) << 8)  |
           (static_cast<uint32_t>(p[3]));
}

static inline void write_be16(std::span<uint8_t, 2> p, uint16_t val) noexcept {
    p[0] = static_cast<uint8_t>(val >> 8);
    p[1] = static_cast<uint8_t>(val & 0xFF);
}

std::expected<TelemetryData, ParseError> parse_telemetry(std::span<const uint8_t> frame) noexcept {
    if (frame.size() < FRAME_SIZE) {
        return std::unexpected(ParseError::BufferTooSmall);
    }

    if (frame[0] != FRAME_MAGIC) {
        return std::unexpected(ParseError::InvalidMagic);
    }

    if (frame[1] != FRAME_VERSION) {
        return std::unexpected(ParseError::UnsupportedVersion);
    }

    auto payload = frame.subspan(0, 14);
    uint16_t expected_crc = read_be16(std::span<const uint8_t, 2>(&frame[14], 2));
    uint16_t actual_crc = crc16_ccitt(payload);

    if (expected_crc != actual_crc) {
        return std::unexpected(ParseError::CrcMismatch);
    }

    TelemetryData res{};
    res.device_id    = read_be32(std::span<const uint8_t, 4>(&frame[2], 4));
    res.seq_num      = read_be16(std::span<const uint8_t, 2>(&frame[6], 2));
    res.raw_pulses   = read_be32(std::span<const uint8_t, 4>(&frame[8], 4));
    res.battery_raw  = frame[12];

    uint8_t flags    = frame[13];
    res.tamper_alarm = (flags & 0x01) != 0;
    res.reverse_flow = (flags & 0x02) != 0;

    return res;
}

std::expected<std::array<uint8_t, CMD_SIZE>, bool> build_command(uint8_t cmd_type, uint16_t param) noexcept {
    std::array<uint8_t, CMD_SIZE> out{};
    out[0] = CMD_MAGIC;
    out[1] = cmd_type;
    write_be16(std::span<uint8_t, 2>(&out[2], 2), param);

    uint16_t crc = crc16_ccitt(std::span<const uint8_t>(out.data(), 4));
    write_be16(std::span<uint8_t, 2>(&out[4], 2), crc);

    return out;
}

} // namespace legacy_v1
```
:::

### 3. Асинхронний серверний проксі-адаптер на Python

Серверна частина проксі побудована на базі асинхронного фреймворку `asyncio`. Вона виконує функцію термінатора мережевих з'єднань, обробляє таймаути польових модемів, взаємодіє з реєстром пристроїв для отримання коефіцієнтів калібрування і транслює нормалізовану подію в чергу повідомлень.

Сервер враховує такі критичні крайові випадки польової експлуатації:

1. **Фрагментація потоку TCP.** Стільниковий модем може надіслати 16-байтний пакет двома шматками (наприклад, 10 байтів і 6 байтів) внаслідок фрагментації на рівні базових станцій GSM. Виклик `reader.readexactly(16)` гарантує накопичення повного кадру перед початком розбору.
2. **Таймаут неактивності (Dead Connection).** Якщо пристрій завис або втратив мережу після встановлення TCP-з'єднання, функція `asyncio.wait_for` із таймаутом 10 секунд примусово закриває сокет, запобігаючи вичерпанню дескрипторів файлів на сервері.
3. **Облік індивідуального калібрування.** Кожен фізичний лічильник має власний коефіцієнт імпульсу (наприклад, 10 літрів на імпульс для лічильника діаметром DN15 або 100 літрів для DN25). Проксі знаходить пристрій у базі за `device_id` і перераховує сирі імпульси в стандартні кубічні метри (м³).
4. **Формування та відправка Downlink-команд.** Якщо в черзі команд бекенду очікує дія для цього приладу, проксі генерує 6-байтний пакет і надсилає його у відкритий сокет до завершення сесії, після чого маркує команду як виконану.

```python
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
```

### 4. Рекомендації для промислового розгортання

Під час запуску адаптера сумісності у промислову експлуатацію слід дотримуватися чотирьох правил інфраструктурної гігієни:

1. **Ізоляція в окремому мережевому просторі (DMZ).** Контейнер зі шлюзом не повинен мати прямого доступу до внутрішніх баз даних чи мікросервісів бекенду. Єдиний дозволений вихідний зв'язок — публікація подій у брокер повідомлень (Kafka/NATS) за протоколом mTLS.
2. **Обмеження швидкості (Rate Limiting).** Оскільки легасі-прилади використовують спрощену схему автентифікації, вхідний порт захищають модулями обмеження з'єднань за IP-підмережами операторів зв'язку (APN Rate Limiting), щоб унеможливити атаки типу «відмова в обслуговуванні» (DoS).
3. **Моніторинг бінарних аномалій.** Усі пакети з некоректним `magic`, невідомою версією або битою контрольною сумою фіксуються в журналі безпеки з міткою часу та IP-адресою джерела для своєчасного виявлення апаратних збоїв чи сканування портів.
4. **Асинхронне кешування реєстру.** Дані калібрування лічильників кешуються в локальній пам'яті процесу проксі, щоб уникнути блокуючих запитів до зовнішніх СУБД під час масового ранкового виходу приладів на зв'язок.
