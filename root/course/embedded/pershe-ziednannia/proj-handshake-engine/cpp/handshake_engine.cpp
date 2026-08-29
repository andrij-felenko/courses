#include "handshake_engine.h"

#include <utility>

namespace {

using Clock = std::chrono::steady_clock;

constexpr int kFirstHeartbeatMs   = 10000;  // скільки чекаємо на ПЕРШЕ серцебиття
constexpr int kLinkLostMs         = 3500;   // тиша в ефірі = лінк втрачено
constexpr int kGcsHeartbeatMs     = 1000;   // власне серцебиття станції
constexpr int kWaitLogMs          = 5000;
constexpr int kParamListRetryMs   = 2000;
constexpr int kParamQuietMs       = 800;    // пауза в потоці PARAM_VALUE = є дірки
constexpr int kParamBatch         = 5;      // дозапит пачкою, щоб не залити чергу UART
constexpr int kParamListRetries   = 5;
constexpr int kParamRoundLimit    = 60;     // стільки пачок дозапиту — і здаємось
constexpr int kStreamAckMs        = 700;
constexpr int kStreamRetries      = 4;
constexpr int kMissionRetryMs     = 1500;
constexpr int kMissionRetries     = 5;

std::int64_t elapsedMs(Clock::time_point from, Clock::time_point to) {
    return std::chrono::duration_cast<std::chrono::milliseconds>(to - from).count();
}

// param_id у кадрі — рівно 16 байтів і НЕ обов'язково з нулем у кінці.
std::string paramName(const char (&raw)[16]) {
    std::size_t len = 0;
    while (len < sizeof(raw) && raw[len] != '\0') {
        ++len;
    }
    return std::string(raw, len);
}

} // namespace

const char* stateName(HandshakeState state) noexcept {
    switch (state) {
        case HandshakeState::Disconnected:  return "DISCONNECTED";
        case HandshakeState::WaitHeartbeat: return "WAIT_HEARTBEAT";
        case HandshakeState::ParamSync:     return "PARAM_SYNC";
        case HandshakeState::StreamConfig:  return "STREAM_CONFIG";
        case HandshakeState::MissionSync:   return "MISSION_SYNC";
        case HandshakeState::Operational:   return "OPERATIONAL";
        case HandshakeState::Failed:        return "FAILED";
    }
    return "UNKNOWN";
}

GcsHandshakeEngine::GcsHandshakeEngine(std::uint8_t gcs_sysid, std::uint8_t gcs_compid)
    : m_gcs_sysid(gcs_sysid), m_gcs_compid(gcs_compid) {}

void GcsHandshakeEngine::setEventSink(std::function<void(EngineEvent)> sink) {
    m_sink = std::move(sink);
}

void GcsHandshakeEngine::emit(EngineEvent event) {
    if (m_sink) {
        m_sink(std::move(event));
    }
}

void GcsHandshakeEngine::log(std::string text) {
    EngineEvent ev;
    ev.kind = EngineEvent::Kind::Log;
    ev.state = m_state;
    ev.text = std::move(text);
    emit(std::move(ev));
}

void GcsHandshakeEngine::enterState(HandshakeState next) {
    m_state = next;
    m_state_since = Clock::now();

    EngineEvent ev;
    ev.kind = EngineEvent::Kind::StateChanged;
    ev.state = next;
    ev.text = stateName(next);
    emit(std::move(ev));
}

void GcsHandshakeEngine::fail(std::string reason) {
    log("ПОМИЛКА: " + reason);
    enterState(HandshakeState::Failed);
}

// Апарат зник посеред роботи: скидаємо все зібране й вертаємось у режим
// слухання. Нове серцебиття (наприклад, після перезавантаження автопілота)
// само перезапустить весь цикл ініціалізації.
void GcsHandshakeEngine::dropLink(std::string reason) {
    log("ЛІНК: " + reason);
    resetSession();
    m_last_wait_log = Clock::now();
    enterState(HandshakeState::WaitHeartbeat);
}

void GcsHandshakeEngine::resetSession() {
    m_params.clear();
    m_param_mask.clear();
    m_param_total = 0;
    m_param_have = 0;
    m_param_cursor = 0;
    m_param_rounds = 0;
    m_list_retries = 0;

    m_streams.clear();
    m_stream_idx = 0;

    m_mission.clear();
    m_mission_total = 0;
    m_mission_seq = 0;
    m_mission_counted = false;

    m_retry = 0;
}

void GcsHandshakeEngine::send(const mavlink_message_t& msg) {
    std::uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
    const std::uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
    sendPacket(std::span<const std::uint8_t>(buffer, len));
}

void GcsHandshakeEngine::sendGcsHeartbeat() {
    // Без нього ArduPilot за кілька секунд вважає станцію втраченою і вмикає
    // GCS-failsafe — станція мусить «дихати» весь час, а не лише в роботі.
    mavlink_message_t msg;
    mavlink_msg_heartbeat_pack(m_gcs_sysid, m_gcs_compid, &msg,
                               MAV_TYPE_GCS, MAV_AUTOPILOT_INVALID, 0, 0, MAV_STATE_ACTIVE);
    send(msg);
}

void GcsHandshakeEngine::start() {
    const auto now = Clock::now();
    resetSession();
    m_last_rx = now;
    m_last_gcs_hb = now - std::chrono::milliseconds(kGcsHeartbeatMs);
    m_last_wait_log = now;
    enterState(HandshakeState::WaitHeartbeat);
    log("Канал відкрито, слухаю ефір — жодних запитів до першого HEARTBEAT");
}

void GcsHandshakeEngine::onMavlinkMessage(const mavlink_message_t& msg) {
    if (msg.sysid == m_gcs_sysid) {
        return;  // власне відлуння в спільному UDP-каналі
    }
    if (m_vehicle.sysid != 0 && msg.sysid != m_vehicle.sysid) {
        return;  // чужий апарат у тому самому ефірі
    }

    m_last_rx = Clock::now();

    switch (msg.msgid) {
        case MAVLINK_MSG_ID_HEARTBEAT:         handleHeartbeat(msg);   break;
        case MAVLINK_MSG_ID_PARAM_VALUE:       handleParamValue(msg);  break;
        case MAVLINK_MSG_ID_COMMAND_ACK:       handleCommandAck(msg);  break;
        case MAVLINK_MSG_ID_MISSION_COUNT:     handleMissionCount(msg); break;
        case MAVLINK_MSG_ID_MISSION_ITEM_INT:  handleMissionItem(msg); break;
        default: break;
    }
}

void GcsHandshakeEngine::tick() {
    if (m_state == HandshakeState::Disconnected || m_state == HandshakeState::Failed) {
        return;
    }

    const auto now = Clock::now();

    if (elapsedMs(m_last_gcs_hb, now) >= kGcsHeartbeatMs) {
        m_last_gcs_hb = now;
        sendGcsHeartbeat();
    }

    // Один сторожовий таймер на всі робочі стани: апарат шле HEARTBEAT раз на
    // секунду, тож тиша довша за 3.5 с означає обрив, а не зайнятість.
    if (m_state != HandshakeState::WaitHeartbeat && elapsedMs(m_last_rx, now) > kLinkLostMs) {
        dropLink("тиша в ефірі > 3.5 с, повертаюсь до очікування серцебиття");
        return;
    }

    switch (m_state) {
        case HandshakeState::WaitHeartbeat: pollWaitHeartbeat(now); break;
        case HandshakeState::ParamSync:     pollParamSync(now);     break;
        case HandshakeState::StreamConfig:  pollStreamConfig(now);  break;
        case HandshakeState::MissionSync:   pollMissionSync(now);   break;
        default: break;
    }
}

void GcsHandshakeEngine::pollWaitHeartbeat(Clock::time_point now) {
    if (!m_seen_vehicle) {
        if (elapsedMs(m_state_since, now) > kFirstHeartbeatMs) {
            fail("жодного HEARTBEAT за 10 с — перевір порт, швидкість і живлення модема");
        }
        return;
    }

    // Апарата ми вже бачили: не здаємось, а чекаємо, доки він повернеться.
    if (elapsedMs(m_last_wait_log, now) > kWaitLogMs) {
        m_last_wait_log = now;
        log("апарат мовчить — чекаю повернення серцебиття");
    }
}

void GcsHandshakeEngine::handleHeartbeat(const mavlink_message_t& msg) {
    mavlink_heartbeat_t hb{};
    mavlink_msg_heartbeat_decode(&msg, &hb);

    if (hb.type == MAV_TYPE_GCS) {
        return;  // сусідня станція в ефірі, а не апарат
    }
    if (msg.compid != MAV_COMP_ID_AUTOPILOT1) {
        return;  // серцебиття компаньйона чи камери — не автопілот
    }

    m_vehicle.sysid = msg.sysid;
    m_vehicle.compid = msg.compid;
    m_vehicle.type = hb.type;
    m_vehicle.autopilot = hb.autopilot;
    m_vehicle.custom_mode = hb.custom_mode;
    m_vehicle.armed = (hb.base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0;

    if (m_state != HandshakeState::WaitHeartbeat) {
        return;  // у роботі серцебиття лише оновлює режим і зводить сторожа
    }

    m_seen_vehicle = true;

    EngineEvent ev;
    ev.kind = EngineEvent::Kind::VehicleFound;
    ev.state = m_state;
    ev.vehicle = m_vehicle;
    ev.text = "апарат упізнано";
    emit(std::move(ev));

    startParamSync();
}

void GcsHandshakeEngine::startParamSync() {
    m_params.clear();
    m_param_mask.clear();
    m_param_total = 0;
    m_param_have = 0;
    m_param_cursor = 0;
    m_param_rounds = 0;
    m_list_retries = 0;

    enterState(HandshakeState::ParamSync);
    log("PARAM_REQUEST_LIST — прошу повну таблицю параметрів");
    sendParamRequestList();
}

void GcsHandshakeEngine::sendParamRequestList() {
    mavlink_message_t msg;
    mavlink_msg_param_request_list_pack(m_gcs_sysid, m_gcs_compid, &msg,
                                        m_vehicle.sysid, m_vehicle.compid);
    send(msg);
    const auto now = Clock::now();
    m_last_req = now;
    m_last_param_rx = now;
}

void GcsHandshakeEngine::handleParamValue(const mavlink_message_t& msg) {
    if (m_state != HandshakeState::ParamSync) {
        return;
    }

    mavlink_param_value_t pv{};
    mavlink_msg_param_value_decode(&msg, &pv);
    m_last_param_rx = Clock::now();

    if (m_param_total == 0 && pv.param_count > 0) {
        m_param_total = pv.param_count;
        m_param_mask.assign(m_param_total, false);
        log("апарат оголосив параметрів: " + std::to_string(m_param_total));
    }

    m_params[paramName(pv.param_id)] = pv.param_value;

    // На читання за іменем прошивка відповідає індексом 0xFFFF — такий кадр
    // дає значення, але дірку в масці не закриває.
    if (pv.param_index < m_param_mask.size() && !m_param_mask[pv.param_index]) {
        m_param_mask[pv.param_index] = true;
        ++m_param_have;
    }
}

void GcsHandshakeEngine::pollParamSync(Clock::time_point now) {
    if (m_param_total == 0) {
        if (elapsedMs(m_last_req, now) > kParamListRetryMs) {
            if (++m_list_retries > kParamListRetries) {
                fail("апарат не відповідає на PARAM_REQUEST_LIST");
                return;
            }
            log("повтор PARAM_REQUEST_LIST (спроба " + std::to_string(m_list_retries) + ")");
            sendParamRequestList();
        }
        return;
    }

    if (m_param_have == m_param_total) {
        log("усі " + std::to_string(m_param_total) + " параметрів на місці");

        EngineEvent ev;
        ev.kind = EngineEvent::Kind::ParamsReady;
        ev.state = m_state;
        ev.params = m_params;  // копія: далі таблицю читає вже інший потік
        emit(std::move(ev));

        startStreamConfig();
        return;
    }

    if (elapsedMs(m_last_param_rx, now) > kParamQuietMs) {
        requestMissingParams(now);
    }
}

void GcsHandshakeEngine::requestMissingParams(Clock::time_point now) {
    if (++m_param_rounds > kParamRoundLimit) {
        fail("дірки в таблиці параметрів не закриваються: маємо " +
             std::to_string(m_param_have) + " з " + std::to_string(m_param_total));
        return;
    }

    int sent = 0;
    std::size_t scanned = 0;
    const std::size_t size = m_param_mask.size();

    while (sent < kParamBatch && scanned < size) {
        if (m_param_cursor >= size) {
            m_param_cursor = 0;
        }
        const std::size_t idx = m_param_cursor++;
        ++scanned;
        if (m_param_mask[idx]) {
            continue;
        }

        // Упаковник копіює рівно 16 байтів імені, тож коротший літерал сюди
        // передавати не можна — тільки занулений буфер.
        char param_id[16]{};
        mavlink_message_t msg;
        mavlink_msg_param_request_read_pack(m_gcs_sysid, m_gcs_compid, &msg,
                                            m_vehicle.sysid, m_vehicle.compid,
                                            param_id, static_cast<std::int16_t>(idx));
        send(msg);
        ++sent;
    }

    m_last_param_rx = now;
    m_last_req = now;
    log("дозапит дірок: " + std::to_string(sent) + " PARAM_REQUEST_READ, бракує " +
        std::to_string(m_param_total - m_param_have) + " з " + std::to_string(m_param_total));
}

void GcsHandshakeEngine::startStreamConfig() {
    m_streams = {
        {MAVLINK_MSG_ID_ATTITUDE,             50000},   // 20 Гц
        {MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 200000},   // 5 Гц
        {MAVLINK_MSG_ID_SYS_STATUS,         1000000},   // 1 Гц
        {MAVLINK_MSG_ID_BATTERY_STATUS,     1000000}    // 1 Гц
    };
    m_stream_idx = 0;
    m_retry = 0;

    enterState(HandshakeState::StreamConfig);
    log("MAV_CMD_SET_MESSAGE_INTERVAL — замовляю частоти телеметрії");
    sendStreamRequest();
}

void GcsHandshakeEngine::sendStreamRequest() {
    if (m_stream_idx >= m_streams.size()) {
        log("потоки телеметрії узгоджено");
        startMissionSync();
        return;
    }

    const auto [msg_id, interval_us] = m_streams[m_stream_idx];
    mavlink_message_t msg;
    mavlink_msg_command_long_pack(m_gcs_sysid, m_gcs_compid, &msg,
                                  m_vehicle.sysid, m_vehicle.compid,
                                  MAV_CMD_SET_MESSAGE_INTERVAL,
                                  static_cast<std::uint8_t>(m_retry),  // поле confirmation
                                  static_cast<float>(msg_id),
                                  static_cast<float>(interval_us),
                                  0.0f, 0.0f, 0.0f, 0.0f, 0.0f);
    send(msg);
    m_last_req = Clock::now();
}

void GcsHandshakeEngine::handleCommandAck(const mavlink_message_t& msg) {
    if (m_state != HandshakeState::StreamConfig) {
        return;
    }

    mavlink_command_ack_t ack{};
    mavlink_msg_command_ack_decode(&msg, &ack);
    if (ack.command != MAV_CMD_SET_MESSAGE_INTERVAL) {
        return;  // підтвердження на чужу команду
    }

    switch (ack.result) {
        case MAV_RESULT_ACCEPTED:
            ++m_stream_idx;
            m_retry = 0;
            sendStreamRequest();
            break;

        case MAV_RESULT_IN_PROGRESS:
            m_last_req = Clock::now();  // прошивка взялася — даємо ще часу
            break;

        case MAV_RESULT_UNSUPPORTED:
        case MAV_RESULT_DENIED:
            log("прошивка не приймає SET_MESSAGE_INTERVAL (result=" +
                std::to_string(static_cast<int>(ack.result)) + "), потік пропущено");
            ++m_stream_idx;
            m_retry = 0;
            sendStreamRequest();
            break;

        default:
            log("команду відхилено тимчасово (result=" +
                std::to_string(static_cast<int>(ack.result)) + "), повторю");
            break;
    }
}

void GcsHandshakeEngine::pollStreamConfig(Clock::time_point now) {
    if (elapsedMs(m_last_req, now) <= kStreamAckMs) {
        return;
    }

    if (++m_retry > kStreamRetries) {
        // Телеметрія — не привід валити рукостискання: старі прошивки просто
        // мовчать на цю команду, а потоки лишаються на типових частотах.
        log("немає COMMAND_ACK на потік, іду далі без підтвердження");
        ++m_stream_idx;
        m_retry = 0;
    }
    sendStreamRequest();
}

void GcsHandshakeEngine::startMissionSync() {
    m_mission.clear();
    m_mission_total = 0;
    m_mission_seq = 0;
    m_mission_counted = false;
    m_retry = 0;

    enterState(HandshakeState::MissionSync);
    log("MISSION_REQUEST_LIST — прошу збережений польотний план");
    sendMissionRequestList();
}

void GcsHandshakeEngine::sendMissionRequestList() {
    mavlink_message_t msg;
    mavlink_msg_mission_request_list_pack(m_gcs_sysid, m_gcs_compid, &msg,
                                          m_vehicle.sysid, m_vehicle.compid,
                                          MAV_MISSION_TYPE_MISSION);
    send(msg);
    m_last_req = Clock::now();
}

void GcsHandshakeEngine::handleMissionCount(const mavlink_message_t& msg) {
    if (m_state != HandshakeState::MissionSync || m_mission_counted) {
        return;
    }

    mavlink_mission_count_t mc{};
    mavlink_msg_mission_count_decode(&msg, &mc);
    if (mc.mission_type != MAV_MISSION_TYPE_MISSION) {
        return;  // геозона чи точки повернення — не наша транзакція
    }

    m_mission_counted = true;
    m_mission_total = mc.count;
    m_mission_seq = 0;
    m_retry = 0;
    m_mission.reserve(m_mission_total);
    log("точок на борту: " + std::to_string(m_mission_total));

    if (m_mission_total == 0) {
        finishMissionSync();  // порожній план — теж повноцінна транзакція
        return;
    }
    requestMissionItem();
}

void GcsHandshakeEngine::requestMissionItem() {
    mavlink_message_t msg;
    mavlink_msg_mission_request_int_pack(m_gcs_sysid, m_gcs_compid, &msg,
                                         m_vehicle.sysid, m_vehicle.compid,
                                         m_mission_seq, MAV_MISSION_TYPE_MISSION);
    send(msg);
    m_last_req = Clock::now();
}

void GcsHandshakeEngine::handleMissionItem(const mavlink_message_t& msg) {
    if (m_state != HandshakeState::MissionSync || !m_mission_counted) {
        return;
    }

    mavlink_mission_item_int_t item{};
    mavlink_msg_mission_item_int_decode(&msg, &item);

    if (item.seq != m_mission_seq) {
        return;  // спізніла відповідь на попередній повтор — мовчки викидаємо
    }

    m_mission.push_back(MissionItem{item.seq, item.command, item.x, item.y, item.z});
    m_retry = 0;
    ++m_mission_seq;

    if (m_mission_seq >= m_mission_total) {
        finishMissionSync();
    } else {
        requestMissionItem();
    }
}

void GcsHandshakeEngine::finishMissionSync() {
    // MISSION_ACK закриває транзакцію: без нього автопілот вважає вичитку
    // незавершеною й блокує наступні операції з планом.
    mavlink_message_t msg;
    mavlink_msg_mission_ack_pack(m_gcs_sysid, m_gcs_compid, &msg,
                                 m_vehicle.sysid, m_vehicle.compid,
                                 MAV_MISSION_ACCEPTED, MAV_MISSION_TYPE_MISSION);
    send(msg);
    log("MISSION_ACK відправлено, план прийнято");

    EngineEvent ev;
    ev.kind = EngineEvent::Kind::MissionReady;
    ev.state = m_state;
    ev.mission = m_mission;  // копія для потоку інтерфейсу
    emit(std::move(ev));

    enterState(HandshakeState::Operational);
}

void GcsHandshakeEngine::pollMissionSync(Clock::time_point now) {
    if (elapsedMs(m_last_req, now) <= kMissionRetryMs) {
        return;
    }

    if (++m_retry > kMissionRetries) {
        fail("польотний план не вичитується (зупинились на точці #" +
             std::to_string(m_mission_seq) + ")");
        return;
    }

    if (!m_mission_counted) {
        log("повтор MISSION_REQUEST_LIST (спроба " + std::to_string(m_retry) + ")");
        sendMissionRequestList();
    } else {
        log("повтор запиту точки #" + std::to_string(m_mission_seq) +
            " (спроба " + std::to_string(m_retry) + ")");
        requestMissionItem();
    }
}
