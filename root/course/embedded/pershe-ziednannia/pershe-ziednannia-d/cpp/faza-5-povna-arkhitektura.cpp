// Приклад неблокувального конвеєра обробки рукостискання на C++20
#include <iostream>
#include <vector>
#include <chrono>
#include <mavlink/v2.0/common/mavlink.h>

enum class GcsState {
    WaitHeartbeat,
    ParamDownload,
    ConfigureStreams,
    MissionDownload,
    OperationalReady
};

class ConnectionFSM {
public:
    void onPacket(const mavlink_message_t& msg) {
        m_last_rx = std::chrono::steady_clock::now();

        switch (m_state) {
            case GcsState::WaitHeartbeat:
                if (msg.msgid == MAVLINK_MSG_ID_HEARTBEAT && msg.sysid != 255) {
                    m_target_sysid = msg.sysid;
                    m_target_compid = msg.compid;
                    std::cout << "[1/4] HEARTBEAT отримано від SysID=" << (int)m_target_sysid << "\n";
                    m_state = GcsState::ParamDownload;
                    requestParameters();
                }
                break;

            case GcsState::ParamDownload:
                if (msg.msgid == MAVLINK_MSG_ID_PARAM_VALUE) {
                    handleParam(msg);
                }
                break;

            case GcsState::ConfigureStreams:
                if (msg.msgid == MAVLINK_MSG_ID_COMMAND_ACK) {
                    std::cout << "[3/4] Телеметрію налаштовано (COMMAND_ACK)\n";
                    m_state = GcsState::MissionDownload;
                    requestMission();
                }
                break;

            case GcsState::MissionDownload:
                if (msg.msgid == MAVLINK_MSG_ID_MISSION_COUNT ||
                    msg.msgid == MAVLINK_MSG_ID_MISSION_ITEM_INT) {
                    handleMission(msg);
                }
                break;

            case GcsState::OperationalReady:
                // Обробка штатної телеметрії польоту (ATTITUDE, GLOBAL_POSITION_INT)
                break;
        }
    }

private:
    void requestParameters() {
        std::cout << "[2/4] Відправка PARAM_REQUEST_LIST...\n";
        // mavlink_msg_param_request_list_pack(...)
    }

    void handleParam(const mavlink_message_t& msg) {
        mavlink_param_value_t pv;
        mavlink_msg_param_value_decode(&msg, &pv);
        // Фіксація в бітовій масці та перевірка повноти списку...
    }

    void requestMission() {
        std::cout << "[4/4] Відправка MISSION_REQUEST_LIST...\n";
        // mavlink_msg_mission_request_list_pack(...)
    }

    void handleMission(const mavlink_message_t& msg) {
        // Покрокова вичитка точок та відправка фінального MISSION_ACK...
    }

    GcsState m_state{GcsState::WaitHeartbeat};
    uint8_t m_target_sysid{1};
    uint8_t m_target_compid{1};
    std::chrono::steady_clock::time_point m_last_rx;
};
