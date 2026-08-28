// Розміщення критичного методу в SRAM на C++20
#pragma once
#include <cstdint>
#include <concepts>

namespace embedded::foc {

#define RAM_FUNC __attribute__((section(".ramfunc"), noinline))

class FastPidController {
public:
    struct Output {
        float d{0.0f};
        float q{0.0f};
    };

    RAM_FUNC Output update(float err_d, float err_q) noexcept {
        m_integrator_d += m_ki * err_d;
        m_integrator_q += m_ki * err_q;

        return Output{
            .d = (m_kp * err_d) + m_integrator_d,
            .q = (m_kp * err_q) + m_integrator_q
        };
    }

private:
    float m_integrator_d{0.0f};
    float m_integrator_q{0.0f};
    float m_kp{2.5f};
    float m_ki{0.08f};
};

} // namespace embedded::foc
