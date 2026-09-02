#include "handshake.h"

#include <iomanip>
#include <iostream>

const char* stateName(GcsState state) {
    switch (state) {
        case GcsState::WaitHeartbeat:    return "WAIT_HEARTBEAT";
        case GcsState::Capabilities:     return "CAPABILITIES";
        case GcsState::ParamDownload:    return "PARAM_DOWNLOAD";
        case GcsState::ConfigureStreams: return "CONFIGURE_STREAMS";
        case GcsState::MissionDownload:  return "MISSION_DOWNLOAD";
        case GcsState::Operational:      return "OPERATIONAL";
        case GcsState::LinkLost:         return "LINK_LOST";
    }
    return "?";
}

HandshakeEngine::HandshakeEngine(SerialLink& link, std::uint8_t gcs_sysid, std::uint8_t gcs_compid)
    : link_(link),
      gcs_sysid_(gcs_sysid),
      gcs_compid_(gcs_compid),
      params_(link, gcs_sysid, gcs_compid),
      telemetry_(link, gcs_sysid, gcs_compid),
      mission_(link, gcs_sysid, gcs_compid) {}

void HandshakeEngine::enter(GcsState state, Clock::time_point now) {
    if (state_ == state) return;
    std::cout << "[fsm] " << stateName(state_) << " → " << stateName(state) << "\n";
    state_ = state;
    (void)now;
}

void HandshakeEngine::onMessage(const mavlink_message_t& msg, Clock::time_point now) {
    // Серцебиття слухаємо в БУДЬ-якому стані: воно годує сторожовий таймер
    // і виявляє нові компоненти шини (підвіс, бортовий комп'ютер).
    if (msg.msgid == MAVLINK_MSG_ID_HEARTBEAT) {
        const bool from_autopilot = registry_.onHeartbeat(msg, now);
        if (from_autopilot && state_ == GcsState::WaitHeartbeat) {
            tsys_ = msg.sysid;
            tcomp_ = msg.compid;
            enter(GcsState::Capabilities, now);
            caps_attempts_ = 0;
            requestCapabilities(now);
        } else if (from_autopilot && state_ == GcsState::LinkLost && msg.sysid == tsys_) {
            enter(resume_, now);
        }
    }

    if (state_ == GcsState::LinkLost) return;

    switch (state_) {
        case GcsState::Capabilities:
            if (msg.msgid == MAVLINK_MSG_ID_AUTOPILOT_VERSION && msg.sysid == tsys_) {
                registry_.onAutopilotVersion(msg);
                beginParams(now);
            }
            break;

        case GcsState::ParamDownload:
            params_.onMessage(msg, now);
            break;

        case GcsState::ConfigureStreams:
            telemetry_.onMessage(msg, now);
            break;

        case GcsState::MissionDownload:
            mission_.onMessage(msg, now);
            break;

        case GcsState::Operational:
            showTelemetry(msg, now);
            break;

        default:
            break;
    }
}

void HandshakeEngine::tick(Clock::time_point now) {
    if (state_ != GcsState::WaitHeartbeat) sendGcsHeartbeat(now);

    if (registry_.tick(now) && state_ != GcsState::LinkLost &&
        state_ != GcsState::WaitHeartbeat) {
        resume_ = state_;  // повернемось саме туди, де нас обірвало
        enter(GcsState::LinkLost, now);
        return;
    }
    if (state_ == GcsState::LinkLost || state_ == GcsState::WaitHeartbeat) return;

    updatePacing(now);

    switch (state_) {
        case GcsState::Capabilities:
            if (now - caps_tx_ > std::chrono::seconds(1)) {
                if (caps_attempts_ >= 3) {
                    // Старий борт мовчить на #520: вважаємо, що можливостей немає,
                    // і далі працюємо через застарілі повідомлення.
                    std::cout << "[1/5] AUTOPILOT_VERSION не отримано — вважаємо стек застарілим\n";
                    beginParams(now);
                } else {
                    requestCapabilities(now);
                }
            }
            break;

        case GcsState::ParamDownload:
            params_.tick(now);
            if (params_.done() || params_.failed()) {
                // Навіть неповний список краще за зупинку: далі йдемо з тим, що є.
                enter(GcsState::ConfigureStreams, now);
                telemetry_.start(tsys_, tcomp_,
                                 registry_.supports(MAV_PROTOCOL_CAPABILITY_SET_MESSAGE_INTERVAL),
                                 now);
            }
            break;

        case GcsState::ConfigureStreams:
            telemetry_.tick(now);
            if (telemetry_.done()) {
                enter(GcsState::MissionDownload, now);
                mission_.start(tsys_, tcomp_, now);
            }
            break;

        case GcsState::MissionDownload:
            mission_.tick(now);
            if (mission_.done() || mission_.failed()) {
                enter(GcsState::Operational, now);
                std::cout << "[5/5] рукостискання завершено: параметрів "
                          << params_.values().size() << ", точок місії "
                          << mission_.items().size() << "\n";
            }
            break;

        default:
            break;
    }
}

void HandshakeEngine::requestCapabilities(Clock::time_point now) {
    mavlink_message_t m;
    mavlink_msg_command_long_pack(gcs_sysid_, gcs_compid_, &m, tsys_, tcomp_,
                                  MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES,
                                  static_cast<std::uint8_t>(caps_attempts_),
                                  1.0f,  // param1 = 1: надішли AUTOPILOT_VERSION
                                  0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f);
    link_.send(m);
    caps_tx_ = now;
    ++caps_attempts_;
}

void HandshakeEngine::beginParams(Clock::time_point now) {
    enter(GcsState::ParamDownload, now);
    params_.start(tsys_, tcomp_, now);
}

void HandshakeEngine::sendGcsHeartbeat(Clock::time_point now) {
    // До першого почутого серцебиття станція в ефір не лізе взагалі; після —
    // сама шле 1 Гц, щоб борт бачив оператора й не спрацював failsafe.
    if (now - last_gcs_hb_ < std::chrono::seconds(1)) return;
    mavlink_message_t m;
    mavlink_msg_heartbeat_pack(gcs_sysid_, gcs_compid_, &m, MAV_TYPE_GCS, MAV_AUTOPILOT_INVALID, 0,
                               0, MAV_STATE_ACTIVE);
    link_.send(m);
    last_gcs_hb_ = now;
}

void HandshakeEngine::updatePacing(Clock::time_point now) {
    if (now - last_pacing_ < std::chrono::seconds(5)) return;
    last_pacing_ = now;

    const double loss = link_.stats().lossPercent();
    const auto gap = loss > 30.0 ? std::chrono::milliseconds(400) : std::chrono::milliseconds(100);
    params_.setPacing(gap);
    mission_.setPacing(gap);

    if (loss > 30.0) {
        std::cout << "[!] втрати " << std::fixed << std::setprecision(1) << loss
                  << "% — сповільнюємо дозапити до " << gap.count() << " мс\n"
                  << std::defaultfloat;
    }
    if (link_.stats().received == 0 && link_.stats().parse_errors > 100) {
        // Валідних кадрів немає, а сміття сиплеться — класична розбіжність швидкості UART.
        std::cout << "[!] " << link_.stats().parse_errors
                  << " помилок парсера без жодного кадру: перевірте швидкість порту\n";
    }
    link_.resetStatsWindow();
}

void HandshakeEngine::showTelemetry(const mavlink_message_t& msg, Clock::time_point now) {
    if (msg.msgid != MAVLINK_MSG_ID_GLOBAL_POSITION_INT) return;
    if (now - last_hud_ < std::chrono::seconds(1)) return;
    last_hud_ = now;

    mavlink_global_position_int_t pos;
    mavlink_msg_global_position_int_decode(&msg, &pos);
    std::cout << std::fixed << std::setprecision(7) << "[hud] " << pos.lat * 1e-7 << ", "
              << pos.lon * 1e-7 << std::setprecision(1) << "  h=" << pos.relative_alt / 1000.0
              << " м  курс=" << pos.hdg / 100.0 << "°  втрати "
              << link_.stats().lossPercent() << "%\n"
              << std::defaultfloat;
}
