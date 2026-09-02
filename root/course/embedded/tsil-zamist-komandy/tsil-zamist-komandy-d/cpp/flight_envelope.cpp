#include "flight_envelope.hpp"

namespace autonomy {
namespace {

[[nodiscard]] bool inside_fence(Vec3 p, const FlightEnvelope& env) noexcept
{
    if (p.x < env.min_x || p.x > env.max_x) {
        return false;
    }
    if (p.y < env.min_y || p.y > env.max_y) {
        return false;
    }
    // NED: z росте вниз, тож висота над домом — це від'ємна різниця.
    const float altitude = -(p.z - env.home.z);
    return altitude >= 0.0F && altitude <= env.max_altitude;
}

} // namespace

std::expected<Seconds, RejectReason> leg_time(Vec3 from, Vec3 to, float airspeed,
                                              Vec3 wind) noexcept
{
    const Vec3 d = to - from;
    const float dist = norm(d);
    if (dist < 0.01F) {
        return Seconds{0.0F}; // уже на місці
    }
    if (airspeed < 0.1F) {
        return std::unexpected(RejectReason::BadRequest);
    }

    const Vec3 u = d * (1.0F / dist);

    // Трикутник швидкостей: вітер розкладаємо на складову вздовж треку (вона
    // додається до колової швидкості) і поперечну — її доводиться компенсувати
    // кутом випередження, і на це витрачається тяга.
    const float along = dot(wind, u);
    const Vec3 cross = wind - u * along;
    const float cross_mag = norm(cross);

    if (cross_mag >= airspeed) {
        return std::unexpected(RejectReason::Headwind); // знесе з треку
    }

    const float ground = std::sqrt(airspeed * airspeed - cross_mag * cross_mag) + along;
    if (ground < 0.1F) {
        return std::unexpected(RejectReason::Headwind); // зустрічний сильніший за апарат
    }
    return Seconds{dist / ground};
}

std::expected<float, RejectReason> round_trip_energy(const Goal& g, const Vehicle& v,
                                                     const FlightEnvelope& env) noexcept
{
    const auto to_goal = leg_time(v.pos, g.target, g.cruise_airspeed, v.wind);
    if (!to_goal) {
        return std::unexpected(to_goal.error());
    }
    // Другий відрізок — повернення додому. Саме він найчастіше й ріже ціль:
    // туди за вітром швидко, назад проти вітру довго.
    const auto back_home = leg_time(g.target, env.home, env.rth_airspeed, v.wind);
    if (!back_home) {
        return std::unexpected(back_home.error());
    }

    const Seconds total = *to_goal + *back_home;
    return v.cruise_power_w * total / 3600.0F * env.energy_reserve;
}

std::expected<void, RejectReason> preflight(const Goal& g, const Vehicle& v,
                                            const FlightEnvelope& env) noexcept
{
    if (g.cruise_airspeed < 0.1F || g.acceptance_radius <= 0.0F) {
        return std::unexpected(RejectReason::BadRequest);
    }

    // Аварійну ціль не фільтруємо: вона і є реакцією на те, що вже зламалося.
    // Відмовити їй означає лишити апарат узагалі без плану дій.
    if (g.priority == Priority::Emergency) {
        return {};
    }

    if (!v.sensors_ok) {
        return std::unexpected(RejectReason::SensorFailure);
    }
    if (!v.motors_ok) {
        return std::unexpected(RejectReason::MotorFailure);
    }
    if (v.ekf_pos_variance > env.ekf_variance_limit) {
        return std::unexpected(RejectReason::EkfDiverged);
    }
    if (!inside_fence(g.target, env)) {
        return std::unexpected(RejectReason::OutsideGeofence);
    }
    if (v.battery_voltage < env.rth_voltage) {
        return std::unexpected(RejectReason::NoEnergy); // просіла банка: нових місій не беремо
    }

    const auto need_wh = round_trip_energy(g, v, env);
    if (!need_wh) {
        return std::unexpected(need_wh.error());
    }
    if (*need_wh > v.battery_energy_wh) {
        return std::unexpected(RejectReason::NoEnergy);
    }
    return {};
}

} // namespace autonomy
