#include "optical_flow.hpp"

namespace nav {

std::expected<FlowMeasurement, FlowReject> OpticalFlow::measure(FlowFrame const& f) noexcept
{
    if (!(f.dt > 0.0f) || f.dt > 0.5f || !std::isfinite(f.rangeRaw) ||
        !isFinite(f.gyro) || !isRotation(f.Rwb, 1.0e-2f)) {
        ++counters_.numeric;
        return std::unexpected(FlowReject::Numeric);
    }

    if (f.squal < kSqualMin) {
        ++counters_.quality;
        return std::unexpected(FlowReject::Quality);
    }

    // Далекомір міряє вздовж осі тіла Z, а потрібна відстань по нормалі до
    // поверхні. R_wb[2][2] — косинус кута між віссю тіла Z і світовою
    // «вниз», тобто якраз потрібний множник.
    const float tiltCos = f.Rwb[2][2];
    if (!(tiltCos > kMinTiltCos)) {
        ++counters_.tilt;
        return std::unexpected(FlowReject::Tilt);
    }

    const float range = f.rangeRaw * tiltCos;
    if (!(range > kMinRange) || range > kMaxRange) {
        ++counters_.range;
        return std::unexpected(FlowReject::Range);
    }

    // Кутова швидкість потоку, рад/с.
    const float wx = static_cast<float>(f.dpx) * kRadPerPixel / f.dt;
    const float wy = static_cast<float>(f.dpy) * kRadPerPixel / f.dt;

    // ── Деротація ──
    // Сенсор дивиться вниз, осі його матриці збігаються з осями тіла X/Y.
    // Тангаж (обертання навколо осі тіла Y) зсуває кадр уздовж X так само,
    // як політ уперед; крен (навколо X) зсуває кадр уздовж Y, але з
    // протилежним знаком. Віднімання цих складових лишає в потоці саме
    // поступальний рух.
    const float linX = wx - f.gyro[1];
    const float linY = wy + f.gyro[0];

    if (std::fabs(linX) > kMaxRate || std::fabs(linY) > kMaxRate) {
        ++counters_.rate;
        return std::unexpected(FlowReject::Rate);
    }

    // Кутова швидкість × дальність = лінійна швидкість у системі тіла.
    // Вертикальну складову беремо нульовою: потік про неї нічого не знає.
    // Через це поворот у світ вносить похибку близько v_z·sin(нахилу) — на
    // малих кутах вона тоне в шумі сенсора, і саме тому строб Махаланобіса
    // потрібен навіть для «чистих» кадрів.
    const Vec3 vBody{linX * range, linY * range, 0.0f};
    const Vec3 vWorld = f.Rwb * vBody;

    // Дисперсія росте з дальністю (множник входить у швидкість) і з падінням
    // якості поверхні (шум пікселів росте швидше за лінійний закон).
    const float q = f.squal > 0 ? static_cast<float>(f.squal) : 1.0f;
    const float qualityFactor = (kSqualRef / q) * (kSqualRef / q);

    FlowMeasurement m{.vx = vWorld[0],
                      .vy = vWorld[1],
                      .r = kRbase * (1.0f + range * range) * qualityFactor,
                      .range = range};

    if (!std::isfinite(m.vx) || !std::isfinite(m.vy) || !std::isfinite(m.r)) {
        ++counters_.numeric;
        return std::unexpected(FlowReject::Numeric);
    }
    return m;
}

}  // namespace nav
