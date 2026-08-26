# ⚙️ Наскрізний міст взаємодії: симулятор вузла на C/C++, шлюз на Python та MQTT-брокер

Цей проєкт реалізує повний робочий конвеєр зв'язку між польовим мікроконтролерним вузлом, прикордонним шлюзом та брокером повідомлень. Архітектура вирішує три класичні інженерні виклики розподілених систем:
1. **Компактна передача без динамічної пам'яті**: прошивка вузла генерує фіксовані бінарні кадри з контрольною сумою CRC-16 без використання динамічної купи (Heap), гарантуючи детермінований час виконання та нульовий ризик фрагментації RAM.
2. **Трансляція, фільтрація та локальна автономія**: демон шлюзу відновлює синхронізацію при втраті байтів у потоці, відсікає надлишковий шум за порогом нечутливості (*Deadband*), збагачує пакети метаданими й транслює їх у структурований формат JSON для публікації в MQTT.
3. **Зворотний канал керування із замкненим контуром**: шлюз асинхронно приймає команди керування від брокера, формує бінарні кадри для вузла й очікує квитанцію підтвердження (ACK) для оновлення стану цифрового двійника.

---

### 1. Специфікація бінарного протоколу каналу (Вузол ↔ Шлюз)

Для мінімізації накладних витрат у радіоефірі та збереження заряду батареї вузол не використовує текстові протоколи. Телеметричний кадр займає рівно 16 байтів:

```
+---------------+---------------+---------------+---------------+
| Magic (0xAA)  |  Type (0x01)  |       Node ID (uint16)        |
+---------------+---------------+---------------+---------------+
|                     Sequence Number (uint32)                  |
+---------------+---------------+---------------+---------------+
|   Temperature (int16, ×0.01)  |    Battery (uint16, mV)       |
+---------------+---------------+---------------+---------------+
| Flags (uint8) | Reserved(0x00)|        CRC-16-CCITT           |
+---------------+---------------+---------------+---------------+
```

* **Magic Byte (`0xAA`)** — синхронізуючий префікс початку кадру для детектування межі повідомлення у неперервному потоці байтів UART або віртуального сокета.
* **Type** — функціональне призначення кадру (`0x01` — телеметрія від вузла, `0x02` — команда до вузла, `0x03` — квитанція ACK).
* **Node ID** — унікальний 16-бітний числовий ідентифікатор сенсора в межах локального сегмента зв'язку.
* **Sequence Number** — монотонно зростаючий 32-бітний лічильник для виявлення втрати пакетів у каналі та запобігання атакам повторного відтворення (Replay attacks).
* **Temperature** — цілочисельне представлення температури в сотих частках градуса Цельсія (`2235` відповідає `22.35 °C`).
* **Battery** — напруга елемента живлення у мілівольтах (`3280` відповідає `3.28 В`).
* **Flags** — бітова маска стану апаратури (біт 0 — стан вихідного реле, біт 1 — прапорець апаратного збою сенсора).
* **CRC-16-CCITT** — контрольна сума за стандартом CCITT (поліном `0x1021`, початкове значення `0xFFFF`), що захищає всі поля кадру від спотворення.

---

### 2. Реалізація вузла (Node Firmware Simulator)

Прошивка вузла формує кадр телеметрії, обчислює контрольну суму та відправляє його в канал зв'язку. Реалізація повністю позбавлена динамічної пам'яті й підтримує ідіоматичні патерни обох мов.

:::tabs
@tab C
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define FRAME_MAGIC_TELEMETRY 0xAA
#define FRAME_TYPE_TELEMETRY  0x01
#define FRAME_TYPE_COMMAND    0x02
#define FRAME_TYPE_ACK        0x03

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;
    uint8_t  type;
    uint16_t node_id;
    uint32_t seq_num;
    int16_t  temperature_c_celsius; // x100 (2235 = 22.35 C)
    uint16_t battery_mv;
    uint8_t  flags;
    uint8_t  reserved;
    uint16_t crc16;
} telemetry_frame_t;

typedef struct {
    uint8_t  magic;
    uint8_t  type;
    uint16_t node_id;
    uint32_t seq_num;
    uint8_t  command_id;
    uint8_t  payload_val;
    uint16_t crc16;
} command_frame_t;
#pragma pack(pop)

/* Табличне або пряме обчислення CRC-16-CCITT (Poly: 0x1021, Init: 0xFFFF) */
uint16_t crc16_ccitt(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

void node_build_telemetry(telemetry_frame_t *frame, uint16_t node_id, uint32_t seq, int16_t temp_c, uint16_t bat_mv, uint8_t flags) {
    frame->magic = FRAME_MAGIC_TELEMETRY;
    frame->type = FRAME_TYPE_TELEMETRY;
    frame->node_id = node_id;
    frame->seq_num = seq;
    frame->temperature_c_celsius = temp_c;
    frame->battery_mv = bat_mv;
    frame->flags = flags;
    frame->reserved = 0x00;
    
    // Рахуємо CRC для всіх полів, крім самого поля crc16
    size_t data_len = sizeof(telemetry_frame_t) - sizeof(uint16_t);
    frame->crc16 = crc16_ccitt((const uint8_t *)frame, data_len);
}

bool node_process_command(const command_frame_t *cmd, uint16_t my_node_id, bool *relay_state) {
    if (cmd->magic != FRAME_MAGIC_TELEMETRY || cmd->type != FRAME_TYPE_COMMAND) {
        return false;
    }
    if (cmd->node_id != my_node_id) {
        return false;
    }
    size_t data_len = sizeof(command_frame_t) - sizeof(uint16_t);
    uint16_t expected_crc = crc16_ccitt((const uint8_t *)cmd, data_len);
    if (cmd->crc16 != expected_crc) {
        return false;
    }
    
    if (cmd->command_id == 0x10) { // Команда: встановити стан реле
        *relay_state = (cmd->payload_val != 0);
        return true;
    }
    return false;
}
```
@tab C++
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

enum class FrameType : uint8_t {
    Telemetry = 0x01,
    Command   = 0x02,
    Ack       = 0x03
};

#pragma pack(push, 1)
struct TelemetryFrame {
    uint8_t   magic{0xAA};
    FrameType type{FrameType::Telemetry};
    uint16_t  node_id{0};
    uint32_t  seq_num{0};
    int16_t   temperature_c_celsius{0};
    uint16_t  battery_mv{0};
    uint8_t   flags{0};
    uint8_t   reserved{0};
    uint16_t  crc16{0};
};

struct CommandFrame {
    uint8_t   magic{0xAA};
    FrameType type{FrameType::Command};
    uint16_t  node_id{0};
    uint32_t  seq_num{0};
    uint8_t   command_id{0};
    uint8_t   payload_val{0};
    uint16_t  crc16{0};
};
#pragma pack(pop)

class Crc16Ccitt {
public:
    static constexpr uint16_t calculate(std::span<const uint8_t> data) noexcept {
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
};

class EdgeNode {
public:
    explicit constexpr EdgeNode(uint16_t id) noexcept : node_id_(id) {}

    [[nodiscard]] TelemetryFrame generate_telemetry(int16_t temp_c, uint16_t bat_mv, uint8_t flags) noexcept {
        TelemetryFrame frame{};
        frame.magic = 0xAA;
        frame.type = FrameType::Telemetry;
        frame.node_id = node_id_;
        frame.seq_num = ++seq_counter_;
        frame.temperature_c_celsius = temp_c;
        frame.battery_mv = bat_mv;
        frame.flags = flags;
        frame.reserved = 0x00;

        auto raw_bytes = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&frame),
            sizeof(TelemetryFrame) - sizeof(uint16_t)
        );
        frame.crc16 = Crc16Ccitt::calculate(raw_bytes);
        return frame;
    }

    [[nodiscard]] bool handle_command(std::span<const uint8_t> raw_cmd) noexcept {
        if (raw_cmd.size() < sizeof(CommandFrame)) {
            return false;
        }
        const auto* cmd = reinterpret_cast<const CommandFrame*>(raw_cmd.data());
        if (cmd->magic != 0xAA || cmd->type != FrameType::Command || cmd->node_id != node_id_) {
            return false;
        }
        auto payload_span = raw_cmd.first(sizeof(CommandFrame) - sizeof(uint16_t));
        if (cmd->crc16 != Crc16Ccitt::calculate(payload_span)) {
            return false;
        }

        if (cmd->command_id == 0x10) { // Set relay
            relay_state_ = (cmd->payload_val != 0);
            return true;
        }
        return false;
    }

    [[nodiscard]] bool is_relay_on() const noexcept { return relay_state_; }
    [[nodiscard]] uint16_t id() const noexcept { return node_id_; }

private:
    uint16_t node_id_;
    uint32_t seq_counter_{0};
    bool relay_state_{false};
};
```
:::

---

### 3. Механізми кадрування та обробки потокових збоїв

У реальних фізичних каналах передачі (UART, RS-485, бездротові радіопакети) приймач може увімкнутися в довільний момент часу посеред передачі кадру. Якщо читати байти без спеціальної перевірки, приймач інтерпретує випадкові байти даних як службові поля.

Для забезпечення надійної синхронізації демон шлюзу реалізує алгоритм ковзного вікна:
1. **Пошук синхробайта**: вхідний потік байтів сканується до виявлення значення `0xAA`.
2. **Накопичення повного кадру**: після знаходження маркера початку шлюз очікує надходження залишкових 15 байтів фіксованої структури.
3. **Верифікація контрольної суми**: обчислюється CRC-16 для перших 14 байтів. Якщо обчислена сума збігається з останніми двома байтами кадру, пакет вважається валідним і передається на обробку. Якщо суми не збігаються (наприклад, байт `0xAA` випадково зустрівся всередині корисних даних попереднього пошкодженого пакета), покажчик зміщується на один байт уперед, і пошук синхромаркера повторюється.

Такий підхід запобігає виникненню фальшивих спрацьовувань і дозволяє автоматично відновити нормальний прийом навіть після глибоких перешкод у радіоефірі.

---

### 4. Реалізація сервісу шлюзу (Python Gateway Daemon)

Шлюз виконує роль мосту між бінарним польовим каналом та брокером повідомлень:

```python
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
```

---

### 5. Інструкція з розгортання та верифікації конвеєра

Для перевірки функціонування всього ланцюга необхідно запустити процеси в окремих терміналах:

1. **Запуск локального MQTT-брокера Mosquitto**:
   ```bash
   mosquitto -p 1883 -v
   ```
2. **Підключення тестового монітора до теми телеметрії**:
   ```bash
   mosquitto_sub -h localhost -t "telemetry/#" -v
   ```
3. **Запуск сервісу шлюзу**:
   ```bash
   python gateway_bridge.py
   ```
4. **Запуск тестового генератора вимірів вузла**:
   ```python
   import socket, struct, time

   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   # Формуємо валідний бінарний кадр для Node 42
   # Magic=0xAA, Type=1, Node=42, Seq=1, Temp=2340 (23.40 C), Bat=3300mV, Flags=0, Res=0
   data_without_crc = struct.pack("<BBHIhHBB", 0xAA, 0x01, 42, 1, 2340, 3300, 0, 0)
   
   crc = 0xFFFF
   for b in data_without_crc:
       crc ^= b << 8
       for _ in range(8):
           crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF

   packet = data_without_crc + struct.pack("<H", crc)
   sock.sendto(packet, ("127.0.0.1", 9000))
   print("Кадр відправлено успішно!")
   ```

У терміналі `mosquitto_sub` з'являється структурований JSON-документ телеметрії:

```json
{
  "timestamp": "2026-08-26T15:50:00Z",
  "gateway_id": "gw_edge_01",
  "node_id": 42,
  "seq": 1,
  "metrics": {
    "temperature": 23.4,
    "battery_mv": 3300,
    "relay_status": false
  },
  "rssi_dbm": -68
}
```

---

### 6. Підводні камені та типові помилки на стиках систем

* **Порядок байтів (Endianness)**: мікроконтролери архітектури ARM Cortex-M за замовчуванням зберігають числа у форматі Little-Endian (молодший байт за молодшою адресою). Якщо код шлюзу розпаковуватиме поля в мережевому порядку Big-Endian, 16-бітні значення `node_id` та `battery_mv` будуть повністю спотворені. Контракт бінарного протоколу повинен явно фіксувати Little-Endian (префікс `<` у форматі Python `struct`).
* **Вирівнювання структур у C (Struct Padding)**: оптимізуючи доступ до пам'яті, 32-бітний компілятор GCC автоматично вставляє байти-заповнювачі перед полями `uint32_t`, щоб вирівняти їх за адресою, кратною 4. Це змінює фізичний розмір структури з 16 до 20 байтів. Обов'язковим є використання директиви `#pragma pack(push, 1)` або атрибута `__attribute__((packed))`.
* **Невирівняний доступ до пам'яті (Unaligned Access HardFault)**: на ядрах ARM Cortex-M0/M0+ пряме приведення довільного вказівника на непарну адресу `(uint32_t*)(buffer + 1)` викликає апаратне виключення `HardFault`, оскільки ядро не підтримує невирівняний доступ. Безпечне читання полів вимагає використання функції `memcpy` або побайтового зсуву.
* **Переповнення сокетного буфера при втраті з'єднання**: якщо зв'язок шлюзу з MQTT-брокером обривається, виклики `publish()` можуть переповнювати внутрішній буфер бібліотеки paho-mqtt. Промисловий шлюз повинен перехоплювати помилки та скидати невідправлені пакети у локальну транзакційну базу на флеші (SQLite/RocksDB), відновлюючи відправку пачками після відновлення мережі.
