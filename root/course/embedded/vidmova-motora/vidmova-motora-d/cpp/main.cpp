#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <optional>
#include <span>
#include <numbers>

namespace flight::control {

constexpr size_t kMaxRotors = 8;
constexpr uint16_t kFdiConfirmTicks = 20;

enum class FrameType : uint8_t {
    QuadX = 4,
    HexaX = 6,
    OctoX = 8
};

enum class RotorHealth : uint8_t {
    Ok = 0,
    Suspected = 1,
    Failed = 2
};

struct ControlDemand {
    float roll{0.0f};
    float pitch{0.0f};
    float yaw{0.0f};
    float thrust{0.0f};
};

struct TelemetrySample {
    float erpm{0.0f};
    float current_amps{0.0f};
    float voltage_volts{0.0f};
};

class FaultTolerantMixer {
public:
    FaultTolerantMixer(FrameType type, float arm_length, float c_tau)
        : rotor_count_(static_cast<size_t>(type)) {
        init_geometry(arm_length, c_tau);
        recalculate_wls();
    }

    void update_fdi(std::span<const float> cmd_outputs,
                    std::span<const TelemetrySample> telemetry) {
        for (size_t i = 0; i < rotor_count_; ++i) {
            bool fault_detected = false;

            if (cmd_outputs[i] > 0.15f && telemetry[i].erpm < 100.0f) {
                fault_detected = true;
            }
            if (cmd_outputs[i] > 0.40f && telemetry[i].erpm > 15000.0f &&
                telemetry[i].current_amps < 1.0f) {
                fault_detected = true;
            }

            if (fault_detected) {
                if (fault_counters_[i] < kFdiConfirmTicks) {
                    ++fault_counters_[i];
                    health_[i] = RotorHealth::Suspected;
                } else if (health_[i] != RotorHealth::Failed) {
                    health_[i] = RotorHealth::Failed;
                    w_inv_[i] = 0.0f;

                    if (rotor_count_ == static_cast<size_t>(FrameType::QuadX)) {
                        spin_recovery_active_ = true;
                    } else {
                        recalculate_wls();
                    }
                }
            } else {
                if (fault_counters_[i] > 0 && health_[i] != RotorHealth::Failed) {
                    --fault_counters_[i];
                    if (fault_counters_[i] == 0) {
                        health_[i] = RotorHealth::Ok;
                    }
                }
            }
        }
    }

    void compute_outputs(const ControlDemand& demand,
                         float current_yaw_rad,
                         float target_heading_rad,
                         std::span<float> out_motors) const {
        if (spin_recovery_active_ && rotor_count_ == 4) {
            compute_spin_recovery(demand.thrust, current_yaw_rad, target_heading_rad, out_motors);
        } else {
            compute_wls_mixing(demand, out_motors);
        }
    }

    [[nodiscard]] bool is_spin_recovery() const noexcept {
        return spin_recovery_active_;
    }

    [[nodiscard]] RotorHealth rotor_health(size_t index) const noexcept {
        return (index < kMaxRotors) ? health_[index] : RotorHealth::Failed;
    }

private:
    size_t rotor_count_{4};
    bool spin_recovery_active_{false};
    std::array<RotorHealth, kMaxRotors> health_{RotorHealth::Ok};
    std::array<uint16_t, kMaxRotors> fault_counters_{0};
    std::array<float, kMaxRotors> w_inv_{1.0f};
    std::array<std::array<float, kMaxRotors>, 4> B_{};
    std::array<std::array<float, 4>, kMaxRotors> M_alloc_{};

    void init_geometry(float arm_length, float c_tau) {
        const float d_angle = 2.0f * std::numbers::pi_v<float> / static_cast<float>(rotor_count_);
        const float start_angle = d_angle * 0.5f;

        for (size_t i = 0; i < rotor_count_; ++i) {
            float angle = start_angle + static_cast<float>(i) * d_angle;
            float rx = arm_length * std::cos(angle);
            float ry = arm_length * std::sin(angle);
            float rdir = (i % 2 == 0) ? 1.0f : -1.0f;

            B_[0][i] = -ry;
            B_[1][i] = rx;
            B_[2][i] = rdir * c_tau;
            B_[3][i] = 1.0f;
            w_inv_[i] = 1.0f;
            health_[i] = RotorHealth::Ok;
        }
    }

    static bool invert_4x4(const std::array<std::array<float, 4>, 4>& in,
                           std::array<std::array<float, 4>, 4>& out) {
        std::array<float, 16> m{}, invOut{};
        for (size_t r = 0; r < 4; ++r) {
            for (size_t c = 0; c < 4; ++c) {
                m[r * 4 + c] = in[r][c];
            }
        }

        invOut[0] = m[5] * m[10] * m[15] - m[5] * m[11] * m[14] - m[9] * m[6] * m[15] +
                    m[9] * m[7] * m[14] + m[13] * m[6] * m[11] - m[13] * m[7] * m[10];
        invOut[4] = -m[4] * m[10] * m[15] + m[4] * m[11] * m[14] + m[8] * m[6] * m[15] -
                    m[8] * m[7] * m[14] - m[12] * m[6] * m[11] + m[12] * m[7] * m[10];
        invOut[8] = m[4] * m[9] * m[15] - m[4] * m[11] * m[13] - m[8] * m[5] * m[15] +
                    m[8] * m[7] * m[13] + m[12] * m[5] * m[11] - m[12] * m[7] * m[9];
        invOut[12] = -m[4] * m[9] * m[14] + m[4] * m[10] * m[13] + m[8] * m[5] * m[14] -
                     m[8] * m[6] * m[13] - m[12] * m[5] * m[10] + m[12] * m[6] * m[9];

        float det = m[0] * invOut[0] + m[1] * invOut[4] + m[2] * invOut[8] + m[3] * invOut[12];
        if (std::abs(det) < 1e-7f) {
            return false;
        }

        invOut[1] = -m[1] * m[10] * m[15] + m[1] * m[11] * m[14] + m[9] * m[2] * m[15] -
                    m[9] * m[3] * m[14] - m[13] * m[2] * m[11] + m[13] * m[3] * m[10];
        invOut[5] = m[0] * m[10] * m[15] - m[0] * m[11] * m[14] - m[8] * m[2] * m[15] +
                    m[8] * m[3] * m[14] + m[12] * m[2] * m[11] - m[12] * m[3] * m[10];
        invOut[9] = -m[0] * m[9] * m[15] + m[0] * m[11] * m[13] + m[8] * m[1] * m[15] -
                    m[8] * m[3] * m[13] - m[12] * m[1] * m[11] + m[12] * m[3] * m[9];
        invOut[13] = m[0] * m[9] * m[14] - m[0] * m[10] * m[13] - m[8] * m[1] * m[14] +
                     m[8] * m[2] * m[13] + m[12] * m[1] * m[10] - m[12] * m[2] * m[9];

        invOut[2] = m[1] * m[6] * m[15] - m[1] * m[7] * m[14] - m[5] * m[2] * m[15] +
                    m[5] * m[3] * m[14] + m[13] * m[2] * m[7] - m[13] * m[3] * m[6];
        invOut[6] = -m[0] * m[6] * m[15] + m[0] * m[7] * m[14] + m[4] * m[2] * m[15] -
                    m[4] * m[3] * m[14] - m[12] * m[2] * m[7] + m[12] * m[3] * m[6];
        invOut[10] = m[0] * m[5] * m[15] - m[0] * m[7] * m[13] - m[4] * m[1] * m[15] +
                     m[4] * m[3] * m[13] + m[12] * m[1] * m[7] - m[12] * m[3] * m[5];
        invOut[14] = -m[0] * m[5] * m[14] + m[0] * m[6] * m[13] + m[4] * m[1] * m[14] -
                     m[4] * m[2] * m[13] - m[12] * m[1] * m[6] + m[12] * m[2] * m[5];

        invOut[3] = -m[1] * m[6] * m[11] + m[1] * m[7] * m[10] + m[5] * m[2] * m[11] -
                    m[5] * m[3] * m[10] - m[9] * m[2] * m[7] + m[9] * m[3] * m[6];
        invOut[7] = m[0] * m[6] * m[11] - m[0] * m[7] * m[10] - m[4] * m[2] * m[11] +
                    m[4] * m[3] * m[10] + m[8] * m[2] * m[7] - m[8] * m[3] * m[6];
        invOut[11] = -m[0] * m[5] * m[11] + m[0] * m[7] * m[9] + m[4] * m[1] * m[11] -
                     m[4] * m[3] * m[9] - m[8] * m[1] * m[7] + m[8] * m[3] * m[5];
        invOut[15] = m[0] * m[5] * m[10] - m[0] * m[6] * m[9] - m[4] * m[1] * m[10] +
                     m[4] * m[2] * m[9] + m[8] * m[1] * m[6] - m[8] * m[2] * m[5];

        const float invDet = 1.0f / det;
        for (size_t i = 0; i < 16; ++i) {
            out[i / 4][i % 4] = invOut[i] * invDet;
        }
        return true;
    }

    bool recalculate_wls() {
        std::array<std::array<float, kMaxRotors>, 4> BW{};
        for (size_t r = 0; r < 4; ++r) {
            for (size_t c = 0; c < rotor_count_; ++c) {
                BW[r][c] = B_[r][c] * w_inv_[c];
            }
        }

        std::array<std::array<float, 4>, 4> BWB_T{};
        for (size_t r = 0; r < 4; ++r) {
            for (size_t c = 0; c < 4; ++c) {
                float acc = 0.0f;
                for (size_t k = 0; k < rotor_count_; ++k) {
                    acc += BW[r][k] * B_[c][k];
                }
                BWB_T[r][c] = acc;
            }
        }

        std::array<std::array<float, 4>, 4> inv_BWB_T{};
        if (!invert_4x4(BWB_T, inv_BWB_T)) {
            return false;
        }

        for (size_t i = 0; i < rotor_count_; ++i) {
            for (size_t j = 0; j < 4; ++j) {
                float acc = 0.0f;
                for (size_t k = 0; k < 4; ++k) {
                    acc += BW[k][i] * inv_BWB_T[k][j];
                }
                M_alloc_[i][j] = acc;
            }
        }
        return true;
    }

    void compute_spin_recovery(float target_thrust,
                               float current_yaw_rad,
                               float target_heading_rad,
                               std::span<float> out_motors) const {
        constexpr float kCyclicAmp = 0.15f;
        const float base_thrust = std::clamp(target_thrust, 0.0f, 0.65f);

        for (size_t i = 0; i < rotor_count_; ++i) {
            if (health_[i] == RotorHealth::Failed) {
                out_motors[i] = 0.0f;
            } else {
                const float rotor_azimuth = static_cast<float>(i) * std::numbers::pi_v<float> * 0.5f;
                const float phase = current_yaw_rad - target_heading_rad + rotor_azimuth;
                const float cyclic = kCyclicAmp * std::cos(phase);
                out_motors[i] = std::clamp(base_thrust + cyclic, 0.05f, 1.0f);
            }
        }
    }

    void compute_wls_mixing(const ControlDemand& demand,
                            std::span<float> out_motors) const {
        const std::array<float, 4> v{demand.roll, demand.pitch, demand.yaw, demand.thrust};

        for (size_t i = 0; i < rotor_count_; ++i) {
            if (health_[i] == RotorHealth::Failed) {
                out_motors[i] = 0.0f;
                continue;
            }
            float sum = 0.0f;
            for (size_t k = 0; k < 4; ++k) {
                sum += M_alloc_[i][k] * v[k];
            }
            out_motors[i] = std::clamp(sum, 0.0f, 1.0f);
        }
    }
};

} // namespace flight::control
