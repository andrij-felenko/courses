#pragma once

// Побудова кадрів #84 і #83. Заголовкова: тут самі перетворення полів у
// повідомлення, без стану й без вводу-виводу.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <expected>
#include <optional>
#include <string_view>

#include <common/mavlink.h>

namespace sp {

/* Ідентифікатори обох кінців обміну. */
struct Ids {
    std::uint8_t self_sys{255};
    std::uint8_t self_comp{MAV_COMP_ID_ONBOARD_COMPUTER};
    std::uint8_t target_sys{1};
    std::uint8_t target_comp{MAV_COMP_ID_AUTOPILOT1};
};

/* Локальний NED: down зростає до землі, тож п'ять метрів висоти це down = -5. */
struct Vec3 {
    float north{};
    float east{};
    float down{};
};

struct BodyRates {
    float roll{};
    float pitch{};
    float yaw{};
};

struct Quaternion {
    float w{1.0f}, x{}, y{}, z{};

    [[nodiscard]] float norm() const noexcept
    {
        return std::sqrt(w * w + x * x + y * y + z * z);
    }

    /* Послідовність Z-Y-X, та сама, що в повідомленні ATTITUDE. */
    [[nodiscard]] static Quaternion from_euler(float roll, float pitch, float yaw) noexcept
    {
        const float cr = std::cos(roll * 0.5f), sr = std::sin(roll * 0.5f);
        const float cp = std::cos(pitch * 0.5f), sp = std::sin(pitch * 0.5f);
        const float cy = std::cos(yaw * 0.5f), sy = std::sin(yaw * 0.5f);
        return Quaternion{cr * cp * cy + sr * sp * sy,
                          sr * cp * cy - cr * sp * sy,
                          cr * sp * cy + sr * cp * sy,
                          cr * cp * sy - sr * sp * cy};
    }
};

enum class Error {
    NotFinite,
    EmptyTarget,
    YawConflict,
    DegenerateQuaternion,
    ThrustOutOfRange
};

[[nodiscard]] constexpr std::string_view describe(Error e) noexcept
{
    switch (e) {
    case Error::NotFinite:            return "у полях уставки нечислові значення";
    case Error::EmptyTarget:          return "уставка порожня: маска ігнорує всі поля";
    case Error::YawConflict:          return "задано і yaw, і yaw_rate — автопілот відкине один із них";
    case Error::DegenerateQuaternion: return "кватерніон нульової норми";
    case Error::ThrustOutOfRange:     return "тяга поза діапазоном 0..1";
    }
    return "невідома помилка";
}

/* Уставка в локальному NED. Порожнє поле означає «автопілот його не читає»:
   бітову маску #84 збираємо саме з того, що заповнене, — руками її ніде
   не набирають. */
struct LocalTarget {
    std::optional<Vec3>  position;      // м
    std::optional<Vec3>  velocity;      // м/с
    std::optional<Vec3>  acceleration;  // м/с², або Н при force = true
    bool                 force{false};
    std::optional<float> yaw;           // рад
    std::optional<float> yaw_rate;      // рад/с
};

struct AttitudeTarget {
    std::optional<Quaternion> attitude;
    std::optional<BodyRates>  rates;
    std::optional<float>      thrust;   // 0..1
};

namespace detail {

/* Біт 9 (0x0200) — не «ігнорувати», а перемикач сенсу afx/afy/afz,
   тому в стартовий набір «усе ігноруємо» він не входить. */
inline constexpr std::uint16_t kPosIgnoreAll = 0x0FFF & ~0x0200;
inline constexpr std::uint16_t kPosForce     = 0x0200;

[[nodiscard]] inline bool finite(const Vec3& v) noexcept
{
    return std::isfinite(v.north) && std::isfinite(v.east) && std::isfinite(v.down);
}

[[nodiscard]] inline bool finite(const BodyRates& r) noexcept
{
    return std::isfinite(r.roll) && std::isfinite(r.pitch) && std::isfinite(r.yaw);
}

}  // namespace detail

[[nodiscard]] inline std::expected<mavlink_message_t, Error>
local_ned(const Ids& ids, std::uint32_t boot_ms, const LocalTarget& t) noexcept
{
    if (!t.position && !t.velocity && !t.acceleration && !t.yaw && !t.yaw_rate)
        return std::unexpected(Error::EmptyTarget);
    /* Обидва кути курсу разом — неоднозначність: автопілот або віддасть перевагу
       yaw, або відкине кадр. Ловимо це тут, а не в польоті. */
    if (t.yaw && t.yaw_rate)
        return std::unexpected(Error::YawConflict);

    mavlink_set_position_target_local_ned_t sp{};
    sp.time_boot_ms = boot_ms;   // 0 = застосувати негайно, поки нема TIMESYNC
    sp.target_system = ids.target_sys;
    sp.target_component = ids.target_comp;
    sp.coordinate_frame = MAV_FRAME_LOCAL_NED;

    std::uint16_t mask = detail::kPosIgnoreAll;

    if (t.position) {
        if (!detail::finite(*t.position)) return std::unexpected(Error::NotFinite);
        sp.x = t.position->north;
        sp.y = t.position->east;
        sp.z = t.position->down;
        mask &= static_cast<std::uint16_t>(~0x0007);
    }
    if (t.velocity) {
        if (!detail::finite(*t.velocity)) return std::unexpected(Error::NotFinite);
        sp.vx = t.velocity->north;
        sp.vy = t.velocity->east;
        sp.vz = t.velocity->down;
        mask &= static_cast<std::uint16_t>(~0x0038);
    }
    if (t.acceleration) {
        if (!detail::finite(*t.acceleration)) return std::unexpected(Error::NotFinite);
        sp.afx = t.acceleration->north;
        sp.afy = t.acceleration->east;
        sp.afz = t.acceleration->down;
        mask &= static_cast<std::uint16_t>(~0x01C0);
        if (t.force) mask |= detail::kPosForce;
    }
    if (t.yaw) {
        if (!std::isfinite(*t.yaw)) return std::unexpected(Error::NotFinite);
        sp.yaw = *t.yaw;
        mask &= static_cast<std::uint16_t>(~0x0400);
    }
    if (t.yaw_rate) {
        if (!std::isfinite(*t.yaw_rate)) return std::unexpected(Error::NotFinite);
        sp.yaw_rate = *t.yaw_rate;
        mask &= static_cast<std::uint16_t>(~0x0800);
    }

    sp.type_mask = mask;

    mavlink_message_t msg{};
    mavlink_msg_set_position_target_local_ned_encode(ids.self_sys, ids.self_comp, &msg, &sp);
    return msg;
}

[[nodiscard]] inline std::expected<mavlink_message_t, Error>
attitude_target(const Ids& ids, std::uint32_t boot_ms, const AttitudeTarget& t) noexcept
{
    if (!t.attitude && !t.rates)
        return std::unexpected(Error::EmptyTarget);

    mavlink_set_attitude_target_t at{};
    at.time_boot_ms = boot_ms;
    at.target_system = ids.target_sys;
    at.target_component = ids.target_comp;
    at.q[0] = 1.0f;   // одиничний кватерніон навіть тоді, коли поле ігнорується

    std::uint8_t mask = 0x01 | 0x02 | 0x04 | 0x80;   // спершу ігноруємо все, крім тяги

    if (t.attitude) {
        const Quaternion& q = *t.attitude;
        if (!std::isfinite(q.w) || !std::isfinite(q.x) || !std::isfinite(q.y) || !std::isfinite(q.z))
            return std::unexpected(Error::NotFinite);
        const float n = q.norm();
        if (!(n > 1e-6f)) return std::unexpected(Error::DegenerateQuaternion);
        /* Норму зводимо до одиниці самі: відхилення понад 1% автопілот
           трактує як зіпсовану орієнтацію. */
        at.q[0] = q.w / n;
        at.q[1] = q.x / n;
        at.q[2] = q.y / n;
        at.q[3] = q.z / n;
        mask &= static_cast<std::uint8_t>(~0x80);
    }
    if (t.rates) {
        if (!detail::finite(*t.rates)) return std::unexpected(Error::NotFinite);
        at.body_roll_rate = t.rates->roll;
        at.body_pitch_rate = t.rates->pitch;
        at.body_yaw_rate = t.rates->yaw;
        mask &= static_cast<std::uint8_t>(~0x07);
    }
    if (t.thrust) {
        if (!std::isfinite(*t.thrust)) return std::unexpected(Error::NotFinite);
        /* Тягу не підрізаємо мовчки: 1.2 замість 0.35 — це помилка розрахунку,
           а не привід дати апарату повний газ. */
        if (*t.thrust < 0.0f || *t.thrust > 1.0f) return std::unexpected(Error::ThrustOutOfRange);
        at.thrust = *t.thrust;
    } else {
        mask |= 0x40;   // ATTITUDE_TARGET_TYPEMASK_THROTTLE_IGNORE
    }

    at.type_mask = mask;

    mavlink_message_t msg{};
    mavlink_msg_set_attitude_target_encode(ids.self_sys, ids.self_comp, &msg, &at);
    return msg;
}

}  // namespace sp
