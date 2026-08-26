# ⚙️ Автоматизована генерація структур та верифікація бінарного протоколу з Kaitai Struct

Коли бінарний протокол описується лише текстовим документом у корпоративній Wiki або коментарями в заголовному файлі C, синхронізація коду між прошивкою мікроконтролера, сервером збору телеметрії та діагностичними утилітами неминуче руйнується. Будь-яка зміна типу поля з `int16_t` на `uint16_t` або додавання прапорця стану в середину структури вимагає синхронного ручного оновлення десеріалізаторів трьома різними мовами програмування.

Розв'язанням є декларативна модель «єдиного джерела правди» (Single Source of Truth, SSOT), де весь протокол описується нейтральною схемою [Kaitai Struct](https://kaitai.io/), а компілятор `ksc` автоматично генерує строго типізовані парсери для C++, C, Python, Go та Rust без ручного дублювання логіки зсувів і порядків байтів.

---

## 1. Архітектура декларативного опису та модель Kaitai Struct

Kaitai Struct — це декларативна мова опису двійкових структур на основі формату YAML. На відміну від класичних серіалізаторів (Protobuf або FlatBuffers), які нав'язують власний внутрішній формат пакування зі службовими тегами, Kaitai Struct дозволяє описати будь-який уже існуючий або кастомний бінарний формат байт-у-байт.

Специфікація компілюється за допомогою утиліти `ksc` (Kaitai Struct Compiler) у незалежні вихідні файли цільових мов. У процесі компіляції генератор створює абстрактне синтаксичне дерево (AST) протоколу, автоматично враховуючи:
- **Базові бінарні типи:** однобайтові числа (`u1`, `s1`), двобайтові та чотирибайтові цілі (`u2`, `s2`, `u4`, `s4`) із фіксованим порядком байтів (`endian: le` або `be`).
- **Динамічну типізацію на основі селекторів (`switch-on`):** автоматичний вибір структури корисного навантаження залежно від поля `msg_id` у заголовку.
- **Обчислювані властивості (`instances`):** декларативні правила інженерного перетворення сирих цілочисельних кодів датчиків у фізичні величини з плаваючою комою (наприклад, множення на коефіцієнт масштабу `0.01`).

Головна перевага обчислюваних властивостей полягає у відсутності потреби зберігати значення з плаваючою комою на рівні двійкового каналу. Мікроконтролер передає компактне 16-бітне ціле число в коді датчика, а клієнтський додаток на Python чи веб-інтерфейс на TypeScript отримує готовий геттер `temperature_c`, який автоматично масштабує значення при першому зверненні.

Нижче наведено повну схему протоколу обміну `telemetry_protocol.ksy`, що описує кадр телеметрії сенсорного вузла, команди налаштування та підтвердження.

```yaml
meta:
  id: telemetry_protocol
  title: Microcontroller Telemetry and Command Protocol
  endian: le
  file-extension: bin

seq:
  - id: sof
    contents: [0xaa]
    doc: Стартовий байт кадру (Start of Frame)
  - id: version
    type: u1
    doc: Мажорна версія протоколу (0x01)
  - id: msg_id
    type: u1
    enum: msg_type
    doc: Ідентифікатор типу повідомлення
  - id: seq_id
    type: u1
    doc: Номер послідовності транзакції (0..255)
  - id: payload_len
    type: u2
    doc: Довжина корисного навантаження в байтах
  - id: payload
    size: payload_len
    type:
      switch-on: msg_id
      cases:
        'msg_type::telemetry_report': msg_telemetry
        'msg_type::cmd_set_config': msg_set_config
        'msg_type::cmd_response': msg_ack_response
    doc: Типізоване корисне навантаження
  - id: crc16
    type: u2
    doc: Контрольна сума CRC-16 CCITT (поліном 0x1021, init 0xFFFF)
  - id: eof
    contents: [0x55]
    doc: Кінцевий байт кадру (End of Frame)

enums:
  msg_type:
    0x01: cmd_ping
    0x02: cmd_set_config
    0x20: telemetry_report
    0x80: cmd_response

  status_code:
    0x00: ok
    0x01: invalid_crc
    0x02: unknown_cmd
    0x03: payload_length_mismatch
    0x04: param_out_of_range
    0x05: hardware_busy

types:
  msg_telemetry:
    seq:
      - id: temp_raw
        type: s2
        doc: Температура сенсора (Scale: 0.01 °C, діапазон -40.00..+125.00)
      - id: pressure_raw
        type: u2
        doc: Атмосферний тиск (Scale: 0.1 hPa, діапазон 300.0..1100.0)
      - id: voltage_mv
        type: u2
        doc: Напруга живлення вузла у мілівольтах (0..5000 mV)
      - id: flags
        type: u1
        doc: Бітова маска станів вузла
      - id: reserved
        type: u1
        doc: Байт вирівнювання до 8 байтів (фіксований 0x00)
    instances:
      temperature_c:
        value: temp_raw * 0.01
      pressure_hpa:
        value: pressure_raw * 0.1

  msg_set_config:
    seq:
      - id: sample_rate_hz
        type: u2
        doc: Частота вибірки АЦП (1..1000 Гц)
      - id: alert_threshold_c
        type: s2
        doc: Поріг спрацьовування аварії за температурою (0.01 °C)
      - id: flags_enable
        type: u1
        doc: Прапорці активації підсистем

  msg_ack_response:
    seq:
      - id: target_seq_id
        type: u1
        doc: Номер послідовності підтверджуваного запиту
      - id: status
        type: u1
        enum: status_code
        doc: Код виконання операції
```

---

## 2. Кодогенерація та вбудований нуль-копіювальний парсер

Для генерації цільових парсерів у терміналі викликається компілятор `ksc`:

```bash
# Генерація C++ парсера для мікроконтролера / шлюзу
ksc -t cpp_stl telemetry_protocol.ksy --outdir generated/cpp

# Генерація Python модуля для бекенду та стендових скриптів
ksc -t python telemetry_protocol.ksy --outdir generated/python
```

У мікроконтролерах із жорсткими обмеженнями на оперативну пам'ять (RAM < 32 КБ) використання стандартного рантайму Kaitai C++ STL небажане через виклики динамічного виділення пам'яті (`std::string`, `std::vector`, потік `std::istream`). Для вбудованих пристроїв використовують статичний нуль-копіювальний (Zero-Copy) парсер, що реалізує ідентичну логіку зміщень і перевірки контрольної суми, гарантуючи детерміноване споживання ресурсів.

Особливу увагу слід звернути на побітове збирання Little-Endian чисел. Замість прямого приведення типу вказівника на структуру `(proto_telemetry_t*)buf`, яке спричиняє невизначену поведінку (Undefined Behavior) через порушення правил Strict Aliasing та аварійне виключення `HardFault` на ядрах ARM Cortex-M0 при непарних адресах, парсер явно конструює 16-бітні значення через операції зсуву `(b0 | (b1 << 8))`. Компілятор GCC/Clang оптимізує таку конструкцію в одну машинну інструкцію `LDRH` або `REV16`.

Нижче наведено парсери мовами C та сучасним C++20, які повністю відповідають контракту `telemetry_protocol.ksy`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PROTO_SOF 0xAA
#define PROTO_EOF 0x55
#define PROTO_HEADER_LEN 6
#define PROTO_FOOTER_LEN 3
#define PROTO_MIN_FRAME_LEN (PROTO_HEADER_LEN + PROTO_FOOTER_LEN)

typedef enum {
    STATUS_OK = 0x00,
    ERR_INVALID_SOF = 0x01,
    ERR_INVALID_EOF = 0x02,
    ERR_INVALID_CRC = 0x03,
    ERR_INVALID_LEN = 0x04,
    ERR_UNKNOWN_MSG = 0x05
} proto_status_t;

typedef enum {
    MSG_CMD_PING = 0x01,
    MSG_CMD_SET_CONFIG = 0x02,
    MSG_TELEMETRY_REPORT = 0x20,
    MSG_CMD_RESPONSE = 0x80
} proto_msg_id_t;

typedef struct {
    int16_t temp_raw;
    uint16_t pressure_raw;
    uint16_t voltage_mv;
    uint8_t flags;
    uint8_t reserved;
} __attribute__((packed)) proto_telemetry_t;

static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

proto_status_t parse_telemetry_frame(const uint8_t *buf, size_t buf_len, proto_telemetry_t *out_data) {
    if (buf_len < PROTO_MIN_FRAME_LEN + sizeof(proto_telemetry_t)) {
        return ERR_INVALID_LEN;
    }
    if (buf[0] != PROTO_SOF) {
        return ERR_INVALID_SOF;
    }
    if (buf[buf_len - 1] != PROTO_EOF) {
        return ERR_INVALID_EOF;
    }

    uint8_t msg_id = buf[2];
    if (msg_id != MSG_TELEMETRY_REPORT) {
        return ERR_UNKNOWN_MSG;
    }

    uint16_t payload_len = (uint16_t)buf[4] | ((uint16_t)buf[5] << 8);
    if (payload_len != sizeof(proto_telemetry_t) || buf_len != PROTO_HEADER_LEN + payload_len + PROTO_FOOTER_LEN) {
        return ERR_INVALID_LEN;
    }

    // Перевірка CRC над заголовком і payload
    uint16_t expected_crc = (uint16_t)buf[buf_len - 3] | ((uint16_t)buf[buf_len - 2] << 8);
    uint16_t calculated_crc = crc16_ccitt(&buf[1], PROTO_HEADER_LEN - 1 + payload_len);
    if (calculated_crc != expected_crc) {
        return ERR_INVALID_CRC;
    }

    // Побайтове копіювання з явним порядком Little-Endian
    const uint8_t *p = &buf[PROTO_HEADER_LEN];
    out_data->temp_raw = (int16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
    out_data->pressure_raw = (uint16_t)p[2] | ((uint16_t)p[3] << 8);
    out_data->voltage_mv = (uint16_t)p[4] | ((uint16_t)p[5] << 8);
    out_data->flags = p[6];
    out_data->reserved = p[7];

    return STATUS_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <array>

enum class ProtoStatus : uint8_t {
    Ok = 0x00,
    InvalidSof = 0x01,
    InvalidEof = 0x02,
    InvalidCrc = 0x03,
    InvalidLen = 0x04,
    UnknownMsg = 0x05
};

enum class MsgType : uint8_t {
    Ping = 0x01,
    SetConfig = 0x02,
    TelemetryReport = 0x20,
    Response = 0x80
};

struct TelemetryReport {
    int16_t temp_raw;
    uint16_t pressure_raw;
    uint16_t voltage_mv;
    uint8_t flags;
    uint8_t reserved;

    [[nodiscard]] constexpr double temperature_c() const noexcept {
        return temp_raw * 0.01;
    }
    [[nodiscard]] constexpr double pressure_hpa() const noexcept {
        return pressure_raw * 0.1;
    }
};

class FrameParser {
public:
    static constexpr uint8_t SofMarker = 0xAA;
    static constexpr uint8_t EofMarker = 0x55;
    static constexpr size_t HeaderLen = 6;
    static constexpr size_t FooterLen = 3;
    static constexpr size_t MinFrameLen = HeaderLen + FooterLen;

    [[nodiscard]] static constexpr uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }

    [[nodiscard]] static std::expected<TelemetryReport, ProtoStatus> parse_telemetry(
        std::span<const uint8_t> frame) noexcept 
    {
        if (frame.size() < MinFrameLen + sizeof(TelemetryReport)) {
            return std::unexpected(ProtoStatus::InvalidLen);
        }
        if (frame.front() != SofMarker) {
            return std::unexpected(ProtoStatus::InvalidSof);
        }
        if (frame.back() != EofMarker) {
            return std::unexpected(ProtoStatus::InvalidEof);
        }
        if (static_cast<MsgType>(frame[2]) != MsgType::TelemetryReport) {
            return std::unexpected(ProtoStatus::UnknownMsg);
        }

        const uint16_t payload_len = static_cast<uint16_t>(frame[4]) | 
                                    (static_cast<uint16_t>(frame[5]) << 8);
        if (payload_len != 8 || frame.size() != HeaderLen + payload_len + FooterLen) {
            return std::unexpected(ProtoStatus::InvalidLen);
        }

        const uint16_t expected_crc = static_cast<uint16_t>(frame[frame.size() - 3]) |
                                     (static_cast<uint16_t>(frame[frame.size() - 2]) << 8);
        const uint16_t actual_crc = calculate_crc16(frame.subspan(1, HeaderLen - 1 + payload_len));
        if (actual_crc != expected_crc) {
            return std::unexpected(ProtoStatus::InvalidCrc);
        }

        const auto payload = frame.subspan(HeaderLen, payload_len);
        TelemetryReport report{
            .temp_raw = static_cast<int16_t>(static_cast<uint16_t>(payload[0]) | (static_cast<uint16_t>(payload[1]) << 8)),
            .pressure_raw = static_cast<uint16_t>(payload[2]) | static_cast<uint16_t>(payload[3] << 8),
            .voltage_mv = static_cast<uint16_t>(payload[4]) | static_cast<uint16_t>(payload[5] << 8),
            .flags = payload[6],
            .reserved = payload[7]
        };

        return report;
    }
};
```
:::

---

## 3. Автоматизована верифікація тестовими векторами (Golden Packets)

Для гарантування повної відповідності між прошивкою, скомпільованим бекендом та схемою Kaitai Struct створюється автоматизований тестовий набір на основі еталонних бінарних векторів (Golden Packets).

Еталонний вектор — це зафіксований масив байтів із наперед відомими значеннями полів. Тестовий скрипт згодовує цей масив згенерованому парсеру й перевіряє точність кожного розкодованого значення. Такий підхід дозволяє перевірити не лише збіг числових значень, а й коректність розрахунку контрольної суми CRC-16 та поведінку при роботі зі знаковими від'ємними числами.

```python
#!/usr/bin/env python3
"""Стендовий скрипт валідації бінарних пакетів проти схеми Kaitai Struct."""
import io
import struct
from telemetry_protocol import TelemetryProtocol


def test_golden_telemetry_packet():
    # Байт 0: SOF (0xAA)
    # Байт 1: Version (0x01)
    # Байт 2: Msg ID (0x20 -> Telemetry)
    # Байт 3: Seq ID (0x4A)
    # Байти 4..5: Length (0x0008 -> 8 байтів LE)
    # Байти 6..7: temp_raw = 2450 (24.50 °C -> 0x0992 LE -> 0x92 0x09)
    # Байти 8..9: pressure_raw = 10132 (1013.2 hPa -> 0x2794 LE -> 0x94 0x27)
    # Байти 10..11: voltage_mv = 3300 mV (0x0CE4 LE -> 0xE4 0x0C)
    # Байт 12: flags = 0x01
    # Байт 13: reserved = 0x00
    # Байти 14..15: CRC-16 CCITT над байтами 1..13
    # Байт 16: EOF (0x55)

    header_payload = bytes([
        0x01,        # Version
        0x20,        # Msg ID
        0x4A,        # Seq ID
        0x08, 0x00,  # Payload Len = 8
        0x92, 0x09,  # Temp = 24.50 C
        0x94, 0x27,  # Pressure = 1013.2 hPa
        0xE4, 0x0C,  # Voltage = 3300 mV
        0x01,        # Flags
        0x00         # Reserved
    ])

    # Обчислення CRC-16 CCITT (init 0xFFFF, poly 0x1021)
    crc = 0xFFFF
    for b in header_payload:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF

    golden_frame = bytes([0xAA]) + header_payload + struct.pack("<H", crc) + bytes([0x55])

    # Розпакування через згенерований Kaitai Struct парсер
    pkt = TelemetryProtocol.from_io(io.BytesIO(golden_frame))

    assert pkt.sof == b"\xaa"
    assert pkt.version == 1
    assert pkt.msg_id == TelemetryProtocol.MsgType.telemetry_report
    assert pkt.seq_id == 0x4A
    assert pkt.payload_len == 8
    assert abs(pkt.payload.temperature_c - 24.50) < 1e-3
    assert abs(pkt.payload.pressure_hpa - 1013.2) < 1e-3
    assert pkt.payload.voltage_mv == 3300
    assert pkt.payload.flags == 0x01
    assert pkt.crc16 == crc
    assert pkt.eof == b"\x55"

    print(f"[OK] Golden Vector: Temp={pkt.payload.temperature_c} C, Press={pkt.payload.pressure_hpa} hPa, CRC=0x{crc:04X}")


if __name__ == "__main__":
    test_golden_telemetry_packet()
```

---

## 4. Граничні випадки та інтеграція у конвеєр CI/CD

Автоматизована валідація у конвеєрі неперервної інтеграції (Continuous Integration) включає перевірку стійкості парсерів до навмисно пошкоджених та некоректних пакетів (Negative Testing).

Для цього створюється набір негативних тестів, які перевіряють усі критичні граничні стани парсера:

1. **Недійсний стартовий або кінцевий маркер:** якщо пакет починається з байта `0x00` замість `0xAA` або обривається до приходу байта `0x55`, парсер негайно повертає код помилки `ERR_INVALID_SOF` або `ERR_INVALID_EOF`, не намагаючись зчитувати внутрішні зміщення. Це запобігає застряганню автомата станів при виникненні шумів у паузах між пакетами.
2. **Невідповідність контрольної суми CRC:** спотворення хоча б одного біта в корисному навантаженні змінює розраховану контрольну суму, в результаті чого парсер відкидає пакет із кодом `ERR_INVALID_CRC`, запобігаючи виконанню хибних команд на приводі або збереженню сміттєвих даних у базу телеметрії.
3. **Невідповідність заявленої довжини (`payload_len`):** якщо заголовок декларує довжину корисного навантаження 8 байтів, а фізичний буфер кадру містить лише 4 байти, парсер виявляє вихід за межі буфера (`ERR_INVALID_LEN`) ще до звернення до даних, унеможливлюючи вразливості переповнення буфера (Buffer Overflow).
4. **Невідомий ідентифікатор команди (`msg_id`):** отримання пакета з невідомим ID повертає статус `ERR_UNKNOWN_MSG`, що дозволяє системі штатно реагувати на пакети майбутніх версій протоколу без аварійного падіння прошивки чи сервера.
5. **Знакове переповнення при від'ємних температурах:** окремий тестовий вектор передає `temp_raw = 0xFEC8` (-312 -> -3.12 °C), перевіряючи, що десеріалізатори на всіх платформах коректно відновлюють від'ємний знак числа у додатковому коді.

### Приклад конфігурації автоматизованого CI-конвеєра

У файлі конфігурації репозиторію (наприклад, `.github/workflows/protocol-check.yml`) налаштовується автоматичний запуск перевірок при кожному оновленні схеми `telemetry_protocol.ksy`:

```yaml
name: Protocol Verification and Codegen

on:
  push:
    paths:
      - 'protocol/**'
  pull_request:
    paths:
      - 'protocol/**'

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Kaitai Struct Compiler
        run: |
          sudo apt-get update
          sudo apt-get install -y default-jre
          wget https://github.com/kaitai-io/kaitai_struct_compiler/releases/download/0.10/kaitai-struct-compiler_0.10_all.deb
          sudo dpkg -i kaitai-struct-compiler_0.10_all.deb

      - name: Generate Code
        run: |
          ksc -t cpp_stl protocol/telemetry_protocol.ksy --outdir generated/cpp
          ksc -t python protocol/telemetry_protocol.ksy --outdir generated/python

      - name: Run Golden Packet Conformance Tests
        run: |
          python3 -m pip install kaitaistruct pytest
          PYTHONPATH=generated/python pytest tests/test_protocol_vectors.py
```

Завдяки зв'язці «декларативна схема Kaitai Struct → згенеровані парсери → CI-тести із золотими векторами» будь-яка спроба несанкціонованої зміни формату пакета блокується автоматично на етапі перевірки коду, гарантуючи безперервну сумісність між прошивкою пристрою та хмарними сервісами.
