// ===========================================================================
//  telemetry.cpp — пакування кадрів MAVLink
//
//  Використовується стандартна згенерована бібліотека C (mavlink v2,
//  діалект common); каталог заголовків підключається до збірки як
//  -Imodules/mavlink/generated. Обгортка над нею тонка навмисно: чужий
//  протокол зручніше читати в його власних термінах.
// ===========================================================================

#include "mag_cal/telemetry.hpp"

#include <common/mavlink.h>

#include <array>
#include <cmath>

namespace mag_cal {
namespace {

// Не частіше 5 Гц: на радіоканалі 57 600 бод прогрес конкурує з потоком
// положення, а оператору швидше однаково не треба.
constexpr std::uint32_t kProgressPeriodMs = 200;

[[nodiscard]] std::uint8_t to_mavlink(CalStatus status) noexcept {
    switch (status) {
        case CalStatus::Waiting:    return MAG_CAL_WAITING_TO_START;
        case CalStatus::Collecting: return MAG_CAL_RUNNING_STEP_ONE;
        case CalStatus::Solving:    return MAG_CAL_RUNNING_STEP_TWO;
        case CalStatus::Success:    return MAG_CAL_SUCCESS;
        case CalStatus::Failed:     return MAG_CAL_FAILED;
        case CalStatus::BadRadius:  return MAG_CAL_BAD_RADIUS;
        case CalStatus::NotStarted: break;
    }
    return MAG_CAL_NOT_STARTED;
}

[[nodiscard]] bool send(const mavlink_message_t& msg) noexcept {
    std::array<std::uint8_t, MAVLINK_MAX_PACKET_LEN> frame{};
    const std::uint16_t len = mavlink_msg_to_send_buffer(frame.data(), &msg);
    return link_port::write(std::as_bytes(std::span{frame}).first(len));
}

}  // namespace

void MavlinkReporter::next_attempt() noexcept {
    if (attempt_ < 255) {
        ++attempt_;
    }
}

bool MavlinkReporter::progress(const Collector& collector, CalStatus status,
                               std::uint32_t now_ms) noexcept {
    // Різниця беззнакових коректно переживає переповнення лічильника
    // мілісекунд, тому порівнюємо саме її, а не самі мітки часу.
    if (now_ms - last_progress_ms_ < kProgressPeriodMs) {
        return false;
    }

    const auto mask = collector.completion_mask();
    const Vec3 hint = collector.hint_direction();

    mavlink_message_t msg{};
    mavlink_msg_mag_cal_progress_pack(system_id_, component_id_, &msg, compass_id_,
                                      static_cast<std::uint8_t>(1U << (compass_id_ & 7U)),
                                      to_mavlink(status), attempt_,
                                      collector.completion_percent(), mask.data(),
                                      hint.x, hint.y, hint.z);

    last_progress_ms_ = now_ms;
    return send(msg);
}

void MavlinkReporter::report(const Calibration& cal, bool success,
                             bool autosaved) noexcept {
    // Масштаб сфери відносно очікуваного поля показує оператору, чи не
    // калібрували апарат поруч зі сталевим столом або динаміком.
    const float scale_factor =
        cal.earth_field > 1.0F ? cal.sphere_radius / cal.earth_field : 1.0F;

    mavlink_message_t msg{};
    mavlink_msg_mag_cal_report_pack(
        system_id_, component_id_, &msg, compass_id_,
        static_cast<std::uint8_t>(1U << (compass_id_ & 7U)),
        success ? MAG_CAL_SUCCESS : MAG_CAL_FAILED, autosaved ? 1U : 0U,
        cal.rms_residual, cal.offset.x, cal.offset.y, cal.offset.z,
        cal.soft_iron.at(0, 0), cal.soft_iron.at(1, 1), cal.soft_iron.at(2, 2),
        cal.soft_iron.at(0, 1), cal.soft_iron.at(0, 2), cal.soft_iron.at(1, 2),
        0.0F,                      // впевненість в орієнтації: її не оцінюємо
        MAV_SENSOR_ROTATION_NONE,  // монтажну орієнтацію не переглядаємо
        MAV_SENSOR_ROTATION_NONE, scale_factor);

    static_cast<void>(send(msg));
}

}  // namespace mag_cal
