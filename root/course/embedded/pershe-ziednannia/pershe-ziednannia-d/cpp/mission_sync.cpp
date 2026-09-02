#include "mission_sync.h"

#include <iomanip>
#include <iostream>

const char* frameName(std::uint8_t frame) {
    switch (frame) {
        case MAV_FRAME_GLOBAL:              return "AMSL";
        case MAV_FRAME_GLOBAL_RELATIVE_ALT: return "від точки зльоту";
        case MAV_FRAME_GLOBAL_TERRAIN_ALT:  return "над рельєфом";
        default: return "інша система відліку";
    }
}

const char* navCommandName(std::uint16_t command) {
    switch (command) {
        case MAV_CMD_NAV_WAYPOINT:        return "WAYPOINT";
        case MAV_CMD_NAV_TAKEOFF:         return "TAKEOFF";
        case MAV_CMD_NAV_LAND:            return "LAND";
        case MAV_CMD_NAV_RETURN_TO_LAUNCH:return "RTL";
        case MAV_CMD_NAV_LOITER_TIME:     return "LOITER";
        default: return "інша команда";
    }
}

MissionSync::MissionSync(SerialLink& link, std::uint8_t gcs_sysid, std::uint8_t gcs_compid)
    : link_(link), gcs_sysid_(gcs_sysid), gcs_compid_(gcs_compid) {}

void MissionSync::start(std::uint8_t tsys, std::uint8_t tcomp, Clock::time_point now) {
    tsys_ = tsys;
    tcomp_ = tcomp;
    count_ = 0;
    expected_ = 0;
    retries_ = 0;
    items_.clear();
    state_ = State::WaitCount;
    sendRequestList(now);
}

void MissionSync::sendRequestList(Clock::time_point now) {
    mavlink_message_t m;
    mavlink_msg_mission_request_list_pack(gcs_sysid_, gcs_compid_, &m, tsys_, tcomp_,
                                          MAV_MISSION_TYPE_MISSION);
    link_.send(m);
    last_tx_ = now;
    std::cout << "[4/5] MISSION_REQUEST_LIST → скільки точок на борту?\n";
}

void MissionSync::sendRequestItem(Clock::time_point now) {
    mavlink_message_t m;
    mavlink_msg_mission_request_int_pack(gcs_sysid_, gcs_compid_, &m, tsys_, tcomp_, expected_,
                                         MAV_MISSION_TYPE_MISSION);
    link_.send(m);
    last_tx_ = now;
}

void MissionSync::sendAck(std::uint8_t type) {
    mavlink_message_t m;
    mavlink_msg_mission_ack_pack(gcs_sysid_, gcs_compid_, &m, tsys_, tcomp_, type,
                                 MAV_MISSION_TYPE_MISSION);
    link_.send(m);
}

void MissionSync::onMessage(const mavlink_message_t& msg, Clock::time_point now) {
    if (msg.sysid != tsys_ || msg.compid != tcomp_) return;

    if (state_ == State::WaitCount && msg.msgid == MAVLINK_MSG_ID_MISSION_COUNT) {
        mavlink_mission_count_t mc;
        mavlink_msg_mission_count_decode(&msg, &mc);
        if (mc.mission_type != MAV_MISSION_TYPE_MISSION) return;  // геозона чи rally-точки

        count_ = mc.count;
        std::cout << "[4/5] MISSION_COUNT = " << count_ << "\n";
        if (count_ == 0) {
            sendAck(MAV_MISSION_ACCEPTED);  // порожній план теж треба закрити квитанцією
            state_ = State::Done;
            return;
        }
        state_ = State::WaitItem;
        expected_ = 0;
        retries_ = 0;
        sendRequestItem(now);
        return;
    }

    if (state_ == State::WaitItem && msg.msgid == MAVLINK_MSG_ID_MISSION_ITEM_INT) {
        mavlink_mission_item_int_t mi;
        mavlink_msg_mission_item_int_decode(&msg, &mi);

        // Автопілот міг відповісти із запізненням на попередній запит: чужий
        // номер просто ігноруємо й далі чекаємо свій.
        if (mi.seq != expected_) return;

        MissionItem item;
        item.seq = mi.seq;
        item.command = mi.command;
        item.frame = mi.frame;
        item.lat_deg = mi.x * 1e-7;  // int32 у градуси
        item.lon_deg = mi.y * 1e-7;
        item.alt_m = mi.z;
        item.hold_s = mi.param1;
        item.accept_radius_m = mi.param2;
        items_.push_back(item);

        std::cout << "      #" << std::setw(2) << mi.seq << ' ' << navCommandName(mi.command) << ' '
                  << std::fixed << std::setprecision(7) << item.lat_deg << ", " << item.lon_deg
                  << std::setprecision(1) << "  h=" << item.alt_m << " м (" << frameName(mi.frame)
                  << ")\n" << std::defaultfloat;

        retries_ = 0;
        if (++expected_ >= count_) {
            sendAck(MAV_MISSION_ACCEPTED);  // транзакцію закрито, буфери узгоджені
            state_ = State::Done;
            std::cout << "[4/5] місію вичитано повністю, надіслано MISSION_ACK\n";
            return;
        }
        last_tx_ = now - pacing_;  // наступний запит — після паузи на розворот ефіру
        return;
    }
}

void MissionSync::tick(Clock::time_point now) {
    if (state_ != State::WaitCount && state_ != State::WaitItem) return;
    if (now - last_tx_ < kItemTimeout) return;

    if (retries_ >= kMaxRetries) {
        std::cout << "[!] точка #" << expected_ << " не прийшла за " << kMaxRetries
                  << " спроб — транзакцію скасовано\n";
        sendAck(MAV_MISSION_ERROR);
        state_ = State::Failed;
        return;
    }
    ++retries_;
    if (state_ == State::WaitCount) {
        sendRequestList(now);
    } else {
        sendRequestItem(now);
    }
}
