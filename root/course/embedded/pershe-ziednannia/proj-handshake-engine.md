# ⚙️ Рушій первинного рукостискання GCS на C++ та Python

Цей практикум розбирає побудову надійного, стійкого до втрати пакетів рушія первинного рукостискання (Connection Handshake Engine) між наземною станцією керування та автопілотом. У ньому наведено дві повні паралельні реалізації — мовою C++ (сучасний стандарт C++20) та мовою Python (із використанням бібліотеки `pymavlink`). Обидва варіанти реалізують єдиний кінцевий автомат (FSM), здатний витримувати високий рівень завад у напівдуплексному радіоканалі, відновлювати втрачені пакети параметрів за бітовою маскою та гарантувати цілісність навігаційного плану місії.

---

### Архітектура та принципи побудови рушія

Головна складність розробки комунікаційного рушія для безпілотних систем полягає в тому, що зв'язок ніколи не є ідеальним. У реальному польоті радіомодеми працюють в умовах багатопроменевого поширення хвиль, затінення антени корпусом апарата та взаємних перешкод від силовиків і відеопередавача. Втрата від 5% до 25% пакетів — це нормальний робочий режим радіоканалу, а не виняткова аварія.

Тому наївний підхід — надіслати запит і чекати відповіді в блокувальному виклику `recv()` — категорично неприйнятний. Він призводить до зависання всієї програми при першому ж втраченому пакеті.

Рушій первинного рукостискання будується за принципом **неблокувального реактора подій (Event-Driven Reactor)** з явним кінцевим автоматом станів (Finite State Machine, FSM).

```
[ DISCONNECTED ] ──(Відкриття каналу зв'язку)──> [ WAIT_HEARTBEAT ]
                                                        │ (HEARTBEAT отримано)
                                                        ▼
                                                [ PARAM_SYNC ] <──(Втрата пакетів: точковий дозапит)
                                                        │ (Усі параметри зібрано)
                                                        ▼
                                                [ STREAM_CONFIG ] <──(COMMAND_ACK retry)
                                                        │ (Потоки підтверджено)
                                                        ▼
                                                [ MISSION_SYNC ] <──(MISSION_ITEM_INT retry)
                                                        │ (MISSION_ACK відправлено)
                                                        ▼
                                                [ OPERATIONAL / READY ]
```

Автомат проходить шість дискретних станів:
1. `Disconnected`: комунікаційний порт закрито, ресурси звільнено.
2. `WaitHeartbeat`: станція відкрила порт і пасивно слухає ефір, очікуючи першого кадру `HEARTBEAT` від автопілота. Жодних запитів у цей момент станція не надсилає.
3. `ParamSync`: отримавши серцебиття, станція ініціює вивантаження повної таблиці параметрів через `PARAM_REQUEST_LIST`. При виявленні пропущених індексів станція автоматично переходить у режим точкового дозапиту через `PARAM_REQUEST_READ`.
4. `StreamConfig`: параметри завантажено; станція конфігурує бажані частоти повідомлень (`ATTITUDE`, `GLOBAL_POSITION_INT`, `SYS_STATUS`, `BATTERY_STATUS`) за допомогою команди `MAV_CMD_SET_MESSAGE_INTERVAL` і перевіряє отримання підтвердження `COMMAND_ACK`.
5. `MissionSync`: станція запитує збережену польотну місію (`MISSION_REQUEST_LIST`), отримує лічильник точок `MISSION_COUNT`, покроково вичитує кожну точку через `MISSION_REQUEST_INT` і завершує транзакцію відправкою кадру `MISSION_ACK`.
6. `Operational / Ready`: усі підсистеми ініціалізовано, екран станції переведено в активний польотний режим, фоновий таймер контролює життєздатність лінка (Liveness Watchdog).

---

### Модель потоків та інтеграція з графічним інтерфейсом

У реальних наземних станціях (наприклад, у QGroundControl чи Mission Planner) комунікаційний рушій ніколи не виконується в головному потоці інтерфейсу користувача (UI Thread). Якщо розбір сотень пакетів на секунду або вивантаження 1000 параметрів помістити в потік малювання віджетів, інтерфейс зависатиме, створюючи неприпустиму для польотного оператора затримку реакції.

Професійна архітектура розділяє застосунок на два ізольовані контури:
1. **Комунікаційний потік введення-виведення (I/O & Protocol Thread)**: відкриває сокети або послідовні порти, утилізує парсер `mavlink_parse_char()`, підтримує черги повторів і крутить кінцевий автомат рукостискання.
2. **Потік інтерфейсу користувача (UI Thread / Event Loop)**: отримує вже повністю зібрані структури даних (наприклад, готовий вектор точок місії чи оновлену таблицю параметрів) через потокобезпечні безблокувальні черги (Lock-free Ring Buffer) або механізм сигналів і слотів у Qt (через `Qt::QueuedConnection`).

Таке розділення гарантує стабільні 60 FPS малювання карти та штучного горизонту навіть у моменти пікового навантаження на радіоканал.

---

### Детальний розбір реалізації на C++ (Modern C++20)

У реалізації на C++ використано стандарт C++20. Клас `GcsHandshakeEngine` інкапсулює стан з'єднання, бітову маску отриманих параметрів, чергу конфігурації потоків та транзакційну вичитку місії.

Ключові архітектурні рішення реалізації на C++:
* **Ізоляція від фізичного транспорту**: метод `sendPacket()` оголошено віртуальним. Це дозволяє використовувати один і той самий код FSM для роботи через послідовний порт UART (libserialport), UDP-сокети (POSIX або Boost.Asio) та віртуальні канали симулятора.
* **Безпечне керування пам'яттю**: використання динамічних структур STL (`std::vector<bool>`, `std::unordered_map<std::string, float>`) усуває ризики переповнення фіксованих буферів, властиві чистому коду C.
* **Таймери на базі `std::chrono::steady_clock`**: монотонний годинник гарантує коректний відлік таймаутів навіть у випадках, коли системний час ОС змінюється через NTP або ручне коригування.

```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <span>

// Підключення офіційних згенерованих C-заголовків MAVLink v2
#include <mavlink/v2.0/common/mavlink.h>

enum class HandshakeState {
    Disconnected,
    WaitHeartbeat,
    ParamSync,
    StreamConfig,
    MissionSync,
    Operational,
    Failed
};

struct VehicleIdentity {
    uint8_t sysid{0};
    uint8_t compid{0};
    uint8_t type{0};
    uint8_t autopilot{0};
    uint32_t custom_mode{0};
    bool is_armed{false};
};

struct MissionItem {
    uint16_t seq{0};
    uint16_t command{0};
    int32_t lat{0};
    int32_t lon{0};
    float alt{0.0f};
};

class GcsHandshakeEngine {
public:
    explicit GcsHandshakeEngine(uint8_t gcs_sysid = 255, uint8_t gcs_compid = 190)
        : m_gcs_sysid(gcs_sysid), m_gcs_compid(gcs_compid) {}

    virtual ~GcsHandshakeEngine() = default;

    void start() {
        m_state = HandshakeState::WaitHeartbeat;
        m_last_state_change = std::chrono::steady_clock::now();
        std::cout << "[GCS] Очікування першого HEARTBEAT від автопілота...\n";
    }

    // Головний диспетчер вхідних пакетів MAVLink
    void onMavlinkMessage(const mavlink_message_t& msg) {
        m_last_packet_time = std::chrono::steady_clock::now();

        switch (msg.msgid) {
            case MAVLINK_MSG_ID_HEARTBEAT:
                handleHeartbeat(msg);
                break;
            case MAVLINK_MSG_ID_PARAM_VALUE:
                handleParamValue(msg);
                break;
            case MAVLINK_MSG_ID_COMMAND_ACK:
                handleCommandAck(msg);
                break;
            case MAVLINK_MSG_ID_MISSION_COUNT:
                handleMissionCount(msg);
                break;
            case MAVLINK_MSG_ID_MISSION_ITEM_INT:
                handleMissionItem(msg);
                break;
            default:
                break;
        }
    }

    // Періодичний таймерний тік автомата станів (викликати кожні 10-20 мс)
    void tick() {
        const auto now = std::chrono::steady_clock::now();

        switch (m_state) {
            case HandshakeState::WaitHeartbeat:
                if (elapsedMs(m_last_state_change, now) > 10000) {
                    std::cerr << "[GCS ERR] Таймаут виявлення серцебиття (>10 c)!\n";
                    m_state = HandshakeState::Failed;
                }
                break;

            case HandshakeState::ParamSync:
                checkParamSyncProgress(now);
                break;

            case HandshakeState::StreamConfig:
                checkStreamConfigProgress(now);
                break;

            case HandshakeState::MissionSync:
                checkMissionSyncProgress(now);
                break;

            case HandshakeState::Operational:
                // Контроль втрати зв'язку (Liveness Watchdog)
                if (elapsedMs(m_last_packet_time, now) > 3500) {
                    std::cerr << "[GCS WARN] Втрата зв'язку з апаратом (LINK_LOST)!\n";
                    m_state = HandshakeState::WaitHeartbeat;
                    m_last_state_change = now;
                }
                break;

            default:
                break;
        }
    }

    [[nodiscard]] HandshakeState state() const noexcept { return m_state; }
    [[nodiscard]] const VehicleIdentity& vehicle() const noexcept { return m_vehicle; }
    [[nodiscard]] const std::unordered_map<std::string, float>& params() const noexcept { return m_params; }
    [[nodiscard]] const std::vector<MissionItem>& mission() const noexcept { return m_mission_items; }

    // Віртуальний метод запису байтів у драйвер порту
    virtual void sendPacket(const mavlink_message_t& msg) {
        uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
        uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
        (void)len;
    }

private:
    void handleHeartbeat(const mavlink_message_t& msg) {
        if (msg.sysid == m_gcs_sysid) return;

        mavlink_heartbeat_t hb;
        mavlink_msg_heartbeat_decode(&msg, &hb);

        if (m_state == HandshakeState::WaitHeartbeat) {
            m_vehicle.sysid = msg.sysid;
            m_vehicle.compid = msg.compid;
            m_vehicle.type = hb.type;
            m_vehicle.autopilot = hb.autopilot;
            m_vehicle.custom_mode = hb.custom_mode;
            m_vehicle.is_armed = (hb.base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0;

            std::cout << "[GCS] Знайдено апарат! SysID=" << static_cast<int>(m_vehicle.sysid)
                      << " CompID=" << static_cast<int>(m_vehicle.compid)
                      << " Type=" << static_cast<int>(m_vehicle.type)
                      << " Autopilot=" << static_cast<int>(m_vehicle.autopilot) << "\n";

            startParamSync();
        }
    }

    void startParamSync() {
        m_state = HandshakeState::ParamSync;
        m_last_state_change = std::chrono::steady_clock::now();
        m_params.clear();
        m_param_received_mask.clear();
        m_expected_param_count = 0;
        m_retry_count = 0;

        std::cout << "[GCS] Запит повного списку параметрів (PARAM_REQUEST_LIST)...\n";
        mavlink_message_t msg;
        mavlink_msg_param_request_list_pack(
            m_gcs_sysid, m_gcs_compid, &msg,
            m_vehicle.sysid, m_vehicle.compid
        );
        sendPacket(msg);
        m_last_req_time = std::chrono::steady_clock::now();
    }

    void handleParamValue(const mavlink_message_t& msg) {
        if (m_state != HandshakeState::ParamSync) return;

        mavlink_param_value_t pv;
        mavlink_msg_param_value_decode(&msg, &pv);

        if (m_expected_param_count == 0 && pv.param_count > 0) {
            m_expected_param_count = pv.param_count;
            m_param_received_mask.assign(m_expected_param_count, false);
            std::cout << "[GCS] Очікується параметрів: " << m_expected_param_count << "\n";
        }

        char name[17] = {0};
        std::memcpy(name, pv.param_id, 16);

        if (pv.param_index < m_param_received_mask.size()) {
            if (!m_param_received_mask[pv.param_index]) {
                m_param_received_mask[pv.param_index] = true;
                m_params[std::string(name)] = pv.param_value;
            }
        }
        m_last_packet_time = std::chrono::steady_clock::now();
    }

    void checkParamSyncProgress(std::chrono::steady_clock::time_point now) {
        if (m_expected_param_count == 0) {
            if (elapsedMs(m_last_req_time, now) > 2000) {
                if (++m_retry_count > 5) {
                    std::cerr << "[GCS ERR] Немає відповіді на PARAM_REQUEST_LIST!\n";
                    m_state = HandshakeState::Failed;
                    return;
                }
                std::cout << "[GCS] Повторний запит списку параметрів (" << m_retry_count << ")...\n";
                startParamSync();
            }
            return;
        }

        const size_t received = std::count(m_param_received_mask.begin(), m_param_received_mask.end(), true);
        if (received == m_expected_param_count) {
            std::cout << "[GCS OK] Усі " << m_expected_param_count << " параметрів успішно завантажено!\n";
            startStreamConfig();
            return;
        }

        // Якщо потік призупинився (тиша > 800 мс), надсилаємо точкові запити на відсутні індекси
        if (elapsedMs(m_last_packet_time, now) > 800) {
            for (size_t i = 0; i < m_param_received_mask.size(); ++i) {
                if (!m_param_received_mask[i]) {
                    mavlink_message_t msg;
                    mavlink_msg_param_request_read_pack(
                        m_gcs_sysid, m_gcs_compid, &msg,
                        m_vehicle.sysid, m_vehicle.compid,
                        "", static_cast<int16_t>(i)
                    );
                    sendPacket(msg);
                    m_last_packet_time = now;
                    break;
                }
            }
        }
    }

    void startStreamConfig() {
        m_state = HandshakeState::StreamConfig;
        m_last_state_change = std::chrono::steady_clock::now();
        m_stream_queue = {
            {MAVLINK_MSG_ID_ATTITUDE, 50000},            // 20 Гц
            {MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 200000},// 5 Гц
            {MAVLINK_MSG_ID_SYS_STATUS, 1000000},        // 1 Гц
            {MAVLINK_MSG_ID_BATTERY_STATUS, 1000000}     // 1 Гц
        };
        m_current_stream_idx = 0;
        m_retry_count = 0;
        std::cout << "[GCS] Налаштування інтервалів телеметрії (MAV_CMD_SET_MESSAGE_INTERVAL)...\n";
        sendNextStreamConfig();
    }

    void sendNextStreamConfig() {
        if (m_current_stream_idx >= m_stream_queue.size()) {
            std::cout << "[GCS OK] Усі телеметричні потоки налаштовано!\n";
            startMissionSync();
            return;
        }

        const auto& [msg_id, interval_us] = m_stream_queue[m_current_stream_idx];
        mavlink_message_t msg;
        mavlink_msg_command_long_pack(
            m_gcs_sysid, m_gcs_compid, &msg,
            m_vehicle.sysid, m_vehicle.compid,
            MAV_CMD_SET_MESSAGE_INTERVAL,
            m_retry_count,
            static_cast<float>(msg_id),
            static_cast<float>(interval_us),
            0.0f, 0.0f, 0.0f, 0.0f, 0.0f
        );
        sendPacket(msg);
        m_last_req_time = std::chrono::steady_clock::now();
    }

    void handleCommandAck(const mavlink_message_t& msg) {
        if (m_state != HandshakeState::StreamConfig) return;

        mavlink_command_ack_t ack;
        mavlink_msg_command_ack_decode(&msg, &ack);

        if (ack.command == MAV_CMD_SET_MESSAGE_INTERVAL) {
            if (ack.result == MAV_RESULT_ACCEPTED) {
                m_current_stream_idx++;
                m_retry_count = 0;
                sendNextStreamConfig();
            } else {
                std::cerr << "[GCS WARN] Команда відхилена (" << static_cast<int>(ack.result) << "), повтор...\n";
            }
        }
    }

    void checkStreamConfigProgress(std::chrono::steady_clock::time_point now) {
        if (elapsedMs(m_last_req_time, now) > 700) {
            if (++m_retry_count > 4) {
                std::cerr << "[GCS WARN] Немає відповіді на налаштування потоку, пропускаємо...\n";
                m_current_stream_idx++;
                m_retry_count = 0;
                sendNextStreamConfig();
                return;
            }
            sendNextStreamConfig();
        }
    }

    void startMissionSync() {
        m_state = HandshakeState::MissionSync;
        m_last_state_change = std::chrono::steady_clock::now();
        m_mission_items.clear();
        m_expected_mission_count = 0;
        m_current_mission_seq = 0;
        m_retry_count = 0;

        std::cout << "[GCS] Запит списку навігаційних точок місії...\n";
        mavlink_message_t msg;
        mavlink_msg_mission_request_list_pack(
            m_gcs_sysid, m_gcs_compid, &msg,
            m_vehicle.sysid, m_vehicle.compid,
            MAV_MISSION_TYPE_MISSION
        );
        sendPacket(msg);
        m_last_req_time = std::chrono::steady_clock::now();
    }

    void handleMissionCount(const mavlink_message_t& msg) {
        if (m_state != HandshakeState::MissionSync) return;

        mavlink_mission_count_t mc;
        mavlink_msg_mission_count_decode(&msg, &mc);

        m_expected_mission_count = mc.count;
        std::cout << "[GCS] На борту збережено точок місії: " << m_expected_mission_count << "\n";

        if (m_expected_mission_count == 0) {
            finalizeMissionSync();
            return;
        }

        m_current_mission_seq = 0;
        requestNextMissionItem();
    }

    void requestNextMissionItem() {
        mavlink_message_t msg;
        mavlink_msg_mission_request_int_pack(
            m_gcs_sysid, m_gcs_compid, &msg,
            m_vehicle.sysid, m_vehicle.compid,
            m_current_mission_seq,
            MAV_MISSION_TYPE_MISSION
        );
        sendPacket(msg);
        m_last_req_time = std::chrono::steady_clock::now();
    }

    void handleMissionItem(const mavlink_message_t& msg) {
        if (m_state != HandshakeState::MissionSync) return;

        mavlink_mission_item_int_t item;
        mavlink_msg_mission_item_int_decode(&msg, &item);

        if (item.seq == m_current_mission_seq) {
            m_mission_items.push_back({item.seq, item.command, item.x, item.y, item.z});
            std::cout << "  [WP #" << item.seq << "] Lat=" << item.x / 1e7
                      << " Lon=" << item.y / 1e7 << " Alt=" << item.z << "m\n";

            m_current_mission_seq++;
            m_retry_count = 0;

            if (m_current_mission_seq >= m_expected_mission_count) {
                finalizeMissionSync();
            } else {
                requestNextMissionItem();
            }
        }
    }

    void finalizeMissionSync() {
        std::cout << "[GCS] Відправка фінального підтвердження MISSION_ACK...\n";
        mavlink_message_t msg;
        mavlink_msg_mission_ack_pack(
            m_gcs_sysid, m_gcs_compid, &msg,
            m_vehicle.sysid, m_vehicle.compid,
            MAV_MISSION_ACCEPTED,
            MAV_MISSION_TYPE_MISSION
        );
        sendPacket(msg);

        m_state = HandshakeState::Operational;
        std::cout << "\n======================================================\n";
        std::cout << ">>> [GCS ГОТОВА ДО РОБОТИ] Зв'язок узгоджено повністю! <<<\n";
        std::cout << "======================================================\n";
    }

    void checkMissionSyncProgress(std::chrono::steady_clock::time_point now) {
        if (elapsedMs(m_last_req_time, now) > 1500) {
            if (++m_retry_count > 5) {
                std::cerr << "[GCS ERR] Перевищено таймаут завантаження місії!\n";
                m_state = HandshakeState::Failed;
                return;
            }
            std::cout << "[GCS] Повторний запит точки #" << m_current_mission_seq << "...\n";
            requestNextMissionItem();
        }
    }

    static int64_t elapsedMs(std::chrono::steady_clock::time_point start, std::chrono::steady_clock::time_point end) {
        return std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    }

    uint8_t m_gcs_sysid;
    uint8_t m_gcs_compid;
    HandshakeState m_state{HandshakeState::Disconnected};
    VehicleIdentity m_vehicle;

    std::chrono::steady_clock::time_point m_last_state_change;
    std::chrono::steady_clock::time_point m_last_packet_time;
    std::chrono::steady_clock::time_point m_last_req_time;

    uint16_t m_expected_param_count{0};
    std::vector<bool> m_param_received_mask;
    std::unordered_map<std::string, float> m_params;

    std::vector<std::pair<uint16_t, uint32_t>> m_stream_queue;
    size_t m_current_stream_idx{0};

    uint16_t m_expected_mission_count{0};
    uint16_t m_current_mission_seq{0};
    std::vector<MissionItem> m_mission_items;

    int m_retry_count{0};
};
```

---

### Детальний розбір реалізації на Python (pymavlink)

Версія на Python забезпечує швидку інтеграцію в скрипти автоматизації тестування, автономні наземні термінали та діагностичні утиліти розробника. Вона побудована на базі об'єкта `mavutil.mavlink_connection`, який самостійно керує потоком байтів та обчисленням контрольних сум CRC.

Особливості реалізації на Python:
* **Неблокувальний цикл обробки (`blocking=False`)**: метод `recv_match()` викликається в короткому циклі з затримкою `time.sleep(0.01)`, що дозволяє одночасно приймати пакети та відслідковувати часові пороги таймаутів.
* **Пакетний дозапит дірок**: якщо потік відповідей переривається, скрипт формує адресні запити пачками по 5 штук, щоб збалансувати навантаження на чергу UART-порту автопілота.
* **Автоматичне перетворення рядків**: обробка ASCII-ідентифікаторів параметрів із врахуванням байтових рядків Python 3 та видаленням завершальних нульових символів `\x00`.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автономний рушій первинного рукостискання наземної станції на pymavlink."""

import time
import sys
from pymavlink import mavutil


class GcsHandshakeClient:
    def __init__(self, connection_string: str, baud: int = 57600):
        print(f"[GCS] Відкриття з'єднання: {connection_string} ({baud} бод)...")
        self.master = mavutil.mavlink_connection(
            connection_string,
            baud=baud,
            source_system=255,
            source_component=190
        )
        self.target_sys = None
        self.target_comp = None
        self.params = {}
        self.mission_items = []

    def run(self) -> bool:
        """Виконує повний конвеєр рукостискання."""
        if not self.step1_wait_heartbeat():
            return False
        if not self.step2_fetch_parameters():
            return False
        if not self.step3_configure_telemetry():
            return False
        if not self.step4_download_mission():
            return False

        print("\n" + "=" * 55)
        print(">>> [GCS READY] Усі підсистеми ініціалізовано! <<<")
        print("=" * 55)
        return True

    def step1_wait_heartbeat(self) -> bool:
        print("[1/4] Очікування першого пакета HEARTBEAT...")
        msg = self.master.recv_match(type='HEARTBEAT', blocking=True, timeout=10.0)
        if not msg:
            print("[ERR] Немає серцебиття від апарата (таймаут 10 с)!")
            return False

        self.target_sys = msg.get_srcSystem()
        self.target_comp = msg.get_srcComponent()
        is_armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)

        print(f"[OK] Апарат знайдено: SysID={self.target_sys}, CompID={self.target_comp}, "
              f"Type={msg.type}, Autopilot={msg.autopilot}, Armed={is_armed}")
        return True

    def step2_fetch_parameters(self) -> bool:
        print("\n[2/4] Завантаження параметрів (PARAM_REQUEST_LIST)...")
        self.master.mav.param_request_list_send(self.target_sys, self.target_comp)

        expected_count = None
        received_mask = []
        last_rx_time = time.time()

        while True:
            msg = self.master.recv_match(type='PARAM_VALUE', blocking=False)
            if msg:
                last_rx_time = time.time()
                if expected_count is None:
                    expected_count = msg.param_count
                    received_mask = [False] * expected_count
                    print(f"  Очікується параметрів: {expected_count}")

                idx = msg.param_index
                if idx < len(received_mask) and not received_mask[idx]:
                    received_mask[idx] = True
                    p_name = msg.param_id
                    if isinstance(p_name, bytes):
                        p_name = p_name.decode('ascii', errors='ignore').strip('\x00')
                    self.params[p_name] = msg.param_value

                # Перевірка завершення вичитки
                if expected_count and sum(received_mask) == expected_count:
                    print(f"[OK] Усі {expected_count} параметрів успішно завантажено!")
                    return True
            else:
                time.sleep(0.01)

            # Перевірка дірок і затримки прийому
            if expected_count and (time.time() - last_rx_time > 0.8):
                missing_indices = [i for i, ok in enumerate(received_mask) if not ok]
                if not missing_indices:
                    break
                print(f"  Дозапит {len(missing_indices)} пропущених параметрів...")
                for missing_idx in missing_indices[:5]:  # дозапитуємо пачками
                    self.master.mav.param_request_read_send(
                        self.target_sys, self.target_comp, b"", missing_idx
                    )
                last_rx_time = time.time()

            if time.time() - last_rx_time > 15.0:
                print(f"[ERR] Таймаут завантаження параметрів (отримано {sum(received_mask)}/{expected_count})")
                return False

        return True

    def step3_configure_telemetry(self) -> bool:
        print("\n[3/4] Налаштування інтервалів повідомлень (MAV_CMD_SET_MESSAGE_INTERVAL)...")
        streams = [
            (mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 50000),             # 20 Гц
            (mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 200000), # 5 Гц
            (mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 1000000),         # 1 Гц
            (mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS, 1000000)      # 1 Гц
        ]

        for msg_id, interval_us in streams:
            self.master.mav.command_long_send(
                self.target_sys, self.target_comp,
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                0, float(msg_id), float(interval_us), 0, 0, 0, 0, 0
            )
            # Чекаємо підтвердження COMMAND_ACK
            ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1.0)
            if ack and ack.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL:
                print(f"  Потік MsgID={msg_id} (інтервал {interval_us} мкс) -> ACK={ack.result}")
            else:
                print(f"  Потік MsgID={msg_id} -> немає явного ACK (приймаємо за замовчуванням)")

        print("[OK] Потоки телеметрії сконфігуровано.")
        return True

    def step4_download_mission(self) -> bool:
        print("\n[4/4] Завантаження польотної місії (Mission Protocol)...")
        self.master.mav.mission_request_list_send(
            self.target_sys, self.target_comp,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )

        msg_count = self.master.recv_match(type='MISSION_COUNT', blocking=True, timeout=3.0)
        if not msg_count:
            print("  Місія відсутня або немає відповіді на запит кількості.")
            return True

        total_items = msg_count.count
        print(f"  Кількість елементів місії на борту: {total_items}")

        for seq in range(total_items):
            retries = 0
            while retries < 4:
                self.master.mav.mission_request_int_send(
                    self.target_sys, self.target_comp, seq,
                    mavutil.mavlink.MAV_MISSION_TYPE_MISSION
                )
                item = self.master.recv_match(type='MISSION_ITEM_INT', blocking=True, timeout=1.5)
                if item and item.seq == seq:
                    self.mission_items.append(item)
                    print(f"    Точка #{seq}: Cmd={item.command}, Lat={item.x/1e7:.6f}, Lon={item.y/1e7:.6f}, Alt={item.z}m")
                    break
                retries += 1
                print(f"    [WARN] Повтор запиту точки #{seq} (спроба {retries})...")

            if retries >= 4:
                print(f"[ERR] Не вдалося завантажити точку місії #{seq}!")
                return False

        # Фінальне квитування всієї місії
        self.master.mav.mission_ack_send(
            self.target_sys, self.target_comp,
            mavutil.mavlink.MAV_MISSION_ACCEPTED,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )
        print("[OK] Місію завантажено та підтверджено.")
        return True


if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else 'udpin:127.0.0.1:14550'
    client = GcsHandshakeClient(port)
    client.run()
```

---

### Методика стендового тестування та валідація надійності

Для перевірки стійкості рушія до відмов використовується симулятор Software-In-The-Loop (SITL) у поєднанні з емулятором мережевих завад.

#### Інструкція з запуску симулятора SITL

1. Запустіть програмний емулятор апарата на ArduPilot (квадрокоптер):
   ```bash
   sim_vehicle.py -v ArduCopter -f quad --out=127.0.0.1:14550
   ```
2. У паралельному терміналі запустіть клієнт рукостискання:
   ```bash
   python gcs_handshake_client.py udpin:127.0.0.1:14550
   ```

#### Сценарії верифікації крайових випадків

* **Імітація втрати пакетів у каналі зв'язку**: за допомогою мережевого інструменту `tc` (Traffic Control під Linux) або проміжного проксі введіть штучну втрату 20% UDP-пакетів:
  ```bash
  sudo tc qdisc add dev lo root netem loss 20%
  ```
  *Критерій успіху*: рушій повинен зафіксувати дірки в бітовій масці, виконати адресні запити `PARAM_REQUEST_READ` та завантажити 100% параметрів без зависання.
* **Аварійний перезапуск автопілота під час завантаження**: вимкніть процес `sim_vehicle.py` під час вивантаження параметрів і запустіть його знову через 5 секунд.
  *Критерій успіху*: рушій фіксує перевищення таймауту, повертається в стан `WaitHeartbeat` і автоматично перезапускає цикл ініціалізації при отриманні нового серцебиття.
* **Перевірка порожньої місії**: очистіть польотний план на борту (`wp clear`). Рушій отримує `MISSION_COUNT = 0` і миттєво переходить у стан `Operational`, уникаючи нескінченного очікування точок.
