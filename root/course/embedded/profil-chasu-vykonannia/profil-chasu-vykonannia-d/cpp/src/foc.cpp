#include "foc.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>

namespace foc {
namespace {

constexpr float kInvSqrt3 = 0.57735026918962576451f;
constexpr float kSqrt3Half = 0.86602540378443864676f;

// std::clamp розгортається у два VCMP з умовним виконанням — це не перехід,
// тож обидві гілки коштують однаково.
[[nodiscard]] inline float clamp(float v, float lo, float hi) noexcept
{
    return std::clamp(v, lo, hi);
}

}  // namespace

void SineTable::build() noexcept
{
    // Єдине місце, де взагалі викликається бібліотечний синус: старт системи.
    for (std::size_t i = 0U; i <= kSineSize; ++i) {
        const double angle = 2.0 * std::numbers::pi_v<double> *
                             static_cast<double>(i) / static_cast<double>(kSineSize);
        table_[i] = static_cast<float>(std::sin(angle));
    }
}

std::array<float, 2> SineTable::sin_cos(Phase phase) const noexcept
{
    const std::uint32_t raw = phase.raw();
    const std::uint32_t idx = raw >> (32U - kSineBits);
    const std::uint32_t frac = (raw >> (32U - kSineBits - 16U)) & 0xFFFFU;
    const float f = static_cast<float>(frac) * (1.0f / 65536.0f);
    const std::uint32_t cdx = (idx + kSineSize / 4U) & (kSineSize - 1U);   // +90 градусів

    return {table_[idx] + (table_[idx + 1U] - table_[idx]) * f,
            table_[cdx] + (table_[cdx + 1U] - table_[cdx]) * f};
}

float PiRegulator::step(float error) noexcept
{
    integral_ += ki_ * error;
    // Антивіндап: інтегратор затиснуто тією самою межею, що й вихід.
    integral_ = clamp(integral_, -limit_, limit_);
    return clamp(kp_ * error + integral_, -limit_, limit_);
}

void CurrentLoop::build_tables() noexcept
{
    sine_.build();
}

void CurrentLoop::reset() noexcept
{
    d_.reset();
    q_.reset();
    reference_ = Dq{};
}

Duties CurrentLoop::update(float ia, float ib, Phase theta, float vdc) noexcept
{
    // Кларк: третя фаза не вимірюється, бо ic = -(ia + ib).
    const float i_alpha = ia;
    const float i_beta = (ia + 2.0f * ib) * kInvSqrt3;

    // Структурне зв'язування розкладає std::array<float,2> просто в регістри.
    const auto [sn, cs] = sine_.sin_cos(theta);

    // Парк: струми в системі координат ротора.
    const float id = i_alpha * cs + i_beta * sn;
    const float iq = -i_alpha * sn + i_beta * cs;

    float vd = d_.step(reference_.d - id);
    float vq = q_.step(reference_.q - iq);

    // Кругове обмеження вектора напруги. std::sqrt — це VSQRT.F32 (14 тактів)
    // за умови складання з -fno-math-errno; гілка спрацьовує рідко, але її
    // час однаково входить у WCET.
    const float v_max = vdc * kInvSqrt3;
    const float v_sq = vd * vd + vq * vq;
    if (v_sq > v_max * v_max) {
        const float scale = v_max / std::sqrt(v_sq);
        vd *= scale;
        vq *= scale;
        d_.scale_integral(scale);   // не копити те, що не вийшло на міст
        q_.scale_integral(scale);
    }

    // Зворотний Парк і зворотний Кларк.
    const float v_alpha = vd * cs - vq * sn;
    const float v_beta = vd * sn + vq * cs;

    const float va = v_alpha;
    const float vb = -0.5f * v_alpha + kSqrt3Half * v_beta;
    const float vc = -0.5f * v_alpha - kSqrt3Half * v_beta;

    // Інжекція середньої точки дає той самий результат, що й SVPWM,
    // але без пошуку сектора — отже, без розгалуження за даними.
    const float hi = std::max({va, vb, vc});
    const float lo = std::min({va, vb, vc});
    const float mid = 0.5f * (hi + lo);
    const float k = 1.0f / vdc;

    return Duties{clamp(0.5f + (va - mid) * k, kDutyMin, kDutyMax),
                  clamp(0.5f + (vb - mid) * k, kDutyMin, kDutyMax),
                  clamp(0.5f + (vc - mid) * k, kDutyMin, kDutyMax)};
}

}  // namespace foc
