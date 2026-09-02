#include "telemetry_budget.h"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>

namespace {

// Те, без чого польотний інтерфейс не працює. Усе інше борт нехай не шле взагалі.
const std::vector<StreamSpec> kDefaultPlan = {
    {"ATTITUDE",            MAVLINK_MSG_ID_ATTITUDE,            MAV_DATA_STREAM_EXTRA1,          20.0f, 40, true},
    {"GLOBAL_POSITION_INT", MAVLINK_MSG_ID_GLOBAL_POSITION_INT, MAV_DATA_STREAM_POSITION,         5.0f, 38, true},
    {"VFR_HUD",             MAVLINK_MSG_ID_VFR_HUD,             MAV_DATA_STREAM_EXTRA2,           5.0f, 30, true},
    {"SYS_STATUS",          MAVLINK_MSG_ID_SYS_STATUS,          MAV_DATA_STREAM_EXTENDED_STATUS,  1.0f, 41, false},
    {"BATTERY_STATUS",      MAVLINK_MSG_ID_BATTERY_STATUS,      MAV_DATA_STREAM_EXTENDED_STATUS,  1.0f, 46, false},
    {"GPS_RAW_INT",         MAVLINK_MSG_ID_GPS_RAW_INT,         MAV_DATA_STREAM_EXTENDED_STATUS,  2.0f, 40, false},
};

constexpr double kHeartbeatBytesPerSecond = 28.0;  // борт шле його сам, 1 Гц

}  // namespace

TelemetrySetup::TelemetrySetup(SerialLink& link, std::uint8_t gcs_sysid, std::uint8_t gcs_compid)
    : link_(link), gcs_sysid_(gcs_sysid), gcs_compid_(gcs_compid) {}

void TelemetrySetup::start(std::uint8_t tsys, std::uint8_t tcomp, bool supports_set_interval,
                           Clock::time_point now) {
    tsys_ = tsys;
    tcomp_ = tcomp;
    plan_ = kDefaultPlan;
    index_ = 0;
    attempts_ = 0;

    fitToBudget();
    printBudget();

    if (!supports_set_interval) {
        // Старий борт не вміє #511 — лишається груба нарізка категоріями.
        legacyFallback();
        state_ = State::Done;
        return;
    }
    state_ = State::Sending;
    sendCurrent(now);
}

void TelemetrySetup::fitToBudget() {
    const double limit = kAirBytesPerSecond * kMaxShare;
    for (;;) {
        double total = kHeartbeatBytesPerSecond;
        for (const auto& s : plan_) total += s.bytesPerSecond();
        if (total <= limit) return;

        // Ріжемо найдорожчий потік із тих, які взагалі можна різати.
        auto worst = plan_.end();
        for (auto it = plan_.begin(); it != plan_.end(); ++it) {
            if (!it->reducible || it->hz <= 1.0f) continue;
            if (worst == plan_.end() || it->bytesPerSecond() > worst->bytesPerSecond()) worst = it;
        }
        if (worst == plan_.end()) {
            std::cout << "[!] план телеметрії не вміщується в канал навіть після урізань\n";
            return;
        }
        worst->hz /= 2.0f;
        std::cout << "[3/5] бюджет перевищено: " << worst->name << " знижено до " << worst->hz
                  << " Гц\n";
    }
}

void TelemetrySetup::printBudget() const {
    double total = kHeartbeatBytesPerSecond;
    double packets = 1.0;
    std::cout << "[3/5] бюджет телеметрії для 57600 бод:\n" << std::fixed << std::setprecision(0);
    for (const auto& s : plan_) {
        const long interval_us = std::lround(1e6 / s.hz);
        total += s.bytesPerSecond();
        packets += s.hz;
        std::cout << "      " << std::setw(20) << std::left << s.name << std::right << std::setw(5)
                  << s.hz << " Гц  інтервал " << std::setw(8) << interval_us << " мкс  "
                  << std::setw(6) << s.bytesPerSecond() << " Б/с\n";
    }
    std::cout << "      разом " << packets << " пак/с, " << total << " Б/с — вільно "
              << std::setprecision(1) << (100.0 * (1.0 - total / kAirBytesPerSecond)) << "% каналу\n"
              << std::defaultfloat;
}

void TelemetrySetup::sendCurrent(Clock::time_point now) {
    const StreamSpec& s = plan_[index_];
    const float interval_us = std::round(1e6f / s.hz);

    mavlink_message_t m;
    mavlink_msg_command_long_pack(gcs_sysid_, gcs_compid_, &m, tsys_, tcomp_,
                                  MAV_CMD_SET_MESSAGE_INTERVAL,
                                  static_cast<std::uint8_t>(attempts_),  // confirmation
                                  static_cast<float>(s.msgid),           // param1: Message ID
                                  interval_us,                           // param2: інтервал, мкс
                                  0.0f, 0.0f, 0.0f, 0.0f, 0.0f);
    link_.send(m);
    last_tx_ = now;
    ++attempts_;
}

void TelemetrySetup::onMessage(const mavlink_message_t& msg, Clock::time_point now) {
    if (state_ != State::Sending) return;
    if (msg.msgid != MAVLINK_MSG_ID_COMMAND_ACK) return;

    mavlink_command_ack_t ack;
    mavlink_msg_command_ack_decode(&msg, &ack);
    if (ack.command != MAV_CMD_SET_MESSAGE_INTERVAL) return;  // квитанція на чужу команду

    const StreamSpec& s = plan_[index_];
    if (ack.result == MAV_RESULT_ACCEPTED) {
        std::cout << "      " << s.name << ": ACCEPTED\n";
    } else if (ack.result == MAV_RESULT_UNSUPPORTED) {
        std::cout << "[!] " << s.name << ": борт не підтримує #511 — переходимо на категорії\n";
        legacyFallback();
        state_ = State::Done;
        return;
    } else {
        std::cout << "[!] " << s.name << ": відмова, код MAV_RESULT=" << int(ack.result) << "\n";
    }

    if (++index_ >= plan_.size()) {
        state_ = State::Done;
        std::cout << "[3/5] потоки телеметрії налаштовано\n";
        return;
    }
    attempts_ = 0;
    sendCurrent(now);  // наступну команду шлемо лише після квитанції на попередню
}

void TelemetrySetup::tick(Clock::time_point now) {
    if (state_ != State::Sending) return;
    if (now - last_tx_ < kAckTimeout) return;

    if (attempts_ >= kMaxAttempts) {
        std::cout << "[!] " << plan_[index_].name << ": квитанції немає після " << kMaxAttempts
                  << " спроб, потік пропущено\n";
        if (++index_ >= plan_.size()) {
            state_ = State::Done;
            return;
        }
        attempts_ = 0;
    }
    // Повтор із зростаючим confirmation — борт відрізнить його від нової команди.
    sendCurrent(now);
}

void TelemetrySetup::legacyFallback() {
    // REQUEST_DATA_STREAM вмикає цілу категорію, тож для кожної беремо
    // найвищу з потрібних нам частот у ній.
    std::vector<std::pair<std::uint8_t, float>> groups;
    for (const auto& s : plan_) {
        auto it = std::find_if(groups.begin(), groups.end(),
                               [&](const auto& g) { return g.first == s.legacy_stream; });
        if (it == groups.end()) {
            groups.emplace_back(s.legacy_stream, s.hz);
        } else {
            it->second = std::max(it->second, s.hz);
        }
    }
    for (const auto& [stream_id, hz] : groups) {
        mavlink_message_t m;
        mavlink_msg_request_data_stream_pack(gcs_sysid_, gcs_compid_, &m, tsys_, tcomp_, stream_id,
                                             static_cast<std::uint16_t>(std::lround(hz)), 1);
        link_.send(m);
    }
    std::cout << "[3/5] увімкнено " << groups.size() << " категорій через REQUEST_DATA_STREAM\n";
}
