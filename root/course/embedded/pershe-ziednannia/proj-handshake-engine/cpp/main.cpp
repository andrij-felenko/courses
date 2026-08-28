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
