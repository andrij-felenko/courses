#include <array>
#include <span>
#include <cmath>
#include <expected>
#include <algorithm>

namespace robotics::control {

inline constexpr size_t kDofCartesian = 6;
inline constexpr float kDtSec = 0.001f;
inline constexpr uint32_t kTareSamples = 500;

enum class AdmittanceMode : uint8_t {
    Idle = 0,
    Taring = 1,
    Active = 2,
    ForceExceeded = 3,
    Retract = 4,
    Fault = 5
};

struct AdmittanceConfig {
    std::array<float, kDofCartesian> m_d{};         // Віртуальна маса (кг, кг·м²)
    std::array<float, kDofCartesian> d_d{};         // Віртуальне демпфування (Н·с/м, Н·м·с/рад)
    std::array<float, kDofCartesian> k_d{};         // Віртуальна жорсткість (Н/м, Н·м/рад)
    float filter_alpha{0.1f};                      // Коефіцієнт згладжування фільтра
    std::array<float, kDofCartesian> deadband{};    // Зона нечутливості датчика (Н, Н·м)
    std::array<float, kDofCartesian> max_force{};   // Аварійний ліміт сили (Н, Н·м)
    std::array<float, kDofCartesian> max_disp{};    // Максимальне зміщення податливості (м, рад)
    float retract_speed{0.05f};                    // Швидкість аварійного відведення (м/с)
};

struct CompliantOutput {
    std::array<float, kDofCartesian> x_cmd{};
    std::array<float, kDofCartesian> v_cmd{};
};

class AdmittanceController {
public:
    explicit constexpr AdmittanceController(const AdmittanceConfig& config) noexcept
        : config_(config) {}

    void reset() noexcept {
        f_raw_offset_.fill(0.0f);
        f_filt_.fill(0.0f);
        disp_.fill(0.0f);
        vel_.fill(0.0f);
        tare_accum_.fill(0.0f);
        tare_counter_ = 0;
        mode_ = AdmittanceMode::Idle;
    }

    void start_tare() noexcept {
        tare_accum_.fill(0.0f);
        tare_counter_ = 0;
        mode_ = AdmittanceMode::Taring;
    }

    [[nodiscard]] auto step(
        std::span<const float, kDofCartesian> f_raw,
        std::span<const float, kDofCartesian> x_nominal,
        std::span<const float, kDofCartesian> v_nominal
    ) noexcept -> std::expected<CompliantOutput, AdmittanceMode> {
        CompliantOutput out{};

        // 1. Обробка тарування
        if (mode_ == AdmittanceMode::Taring) {
            for (size_t i = 0; i < kDofCartesian; ++i) {
                tare_accum_[i] += f_raw[i];
                out.x_cmd[i] = x_nominal[i];
                out.v_cmd[i] = v_nominal[i];
            }
            if (++tare_counter_ >= kTareSamples) {
                for (size_t i = 0; i < kDofCartesian; ++i) {
                    f_raw_offset_[i] = tare_accum_[i] / static_cast<float>(kTareSamples);
                    disp_[i] = 0.0f;
                    vel_[i] = 0.0f;
                    f_filt_[i] = 0.0f;
                }
                mode_ = AdmittanceMode::Active;
            }
            return out;
        }

        // 2. Обробка аварійного відведення
        if (mode_ == AdmittanceMode::ForceExceeded || mode_ == AdmittanceMode::Retract) {
            mode_ = AdmittanceMode::Retract;
            for (size_t i = 0; i < kDofCartesian; ++i) {
                if (disp_[i] > 0.0001f) {
                    disp_[i] -= config_.retract_speed * kDtSec;
                } else if (disp_[i] < -0.0001f) {
                    disp_[i] += config_.retract_speed * kDtSec;
                } else {
                    disp_[i] = 0.0f;
                }
                vel_[i] = 0.0f;
                out.x_cmd[i] = x_nominal[i] + disp_[i];
                out.v_cmd[i] = v_nominal[i];
            }
            return out;
        }

        // 3. Основний розрахунковий контур
        for (size_t i = 0; i < kDofCartesian; ++i) {
            const float f_unbiased = f_raw[i] - f_raw_offset_[i];
            f_filt_[i] = (1.0f - config_.filter_alpha) * f_filt_[i] +
                         config_.filter_alpha * f_unbiased;

            if (std::abs(f_filt_[i]) > config_.max_force[i]) {
                mode_ = AdmittanceMode::ForceExceeded;
                return std::unexpected(AdmittanceMode::ForceExceeded);
            }

            float f_active = 0.0f;
            if (f_filt_[i] > config_.deadband[i]) {
                f_active = f_filt_[i] - config_.deadband[i];
            } else if (f_filt_[i] < -config_.deadband[i]) {
                f_active = f_filt_[i] + config_.deadband[i];
            }

            const float accel = (-f_active - config_.d_d[i] * vel_[i] - config_.k_d[i] * disp_[i]) / config_.m_d[i];

            // Напівнеявне інтегрування
            vel_[i] += accel * kDtSec;
            disp_[i] += vel_[i] * kDtSec;

            // Захист від інтегрального розгону на межі робочого простору
            if (disp_[i] > config_.max_disp[i]) {
                disp_[i] = config_.max_disp[i];
                if (vel_[i] > 0.0f) vel_[i] = 0.0f;
            } else if (disp_[i] < -config_.max_disp[i]) {
                disp_[i] = -config_.max_disp[i];
                if (vel_[i] < 0.0f) vel_[i] = 0.0f;
            }

            out.x_cmd[i] = x_nominal[i] + disp_[i];
            out.v_cmd[i] = v_nominal[i] + vel_[i];
        }

        mode_ = AdmittanceMode::Active;
        return out;
    }

    [[nodiscard]] AdmittanceMode mode() const noexcept { return mode_; }
    [[nodiscard]] const auto& filtered_force() const noexcept { return f_filt_; }
    [[nodiscard]] const auto& displacement() const noexcept { return disp_; }

private:
    AdmittanceConfig config_;
    std::array<float, kDofCartesian> f_raw_offset_{};
    std::array<float, kDofCartesian> f_filt_{};
    std::array<float, kDofCartesian> disp_{};
    std::array<float, kDofCartesian> vel_{};
    std::array<float, kDofCartesian> tare_accum_{};
    uint32_t tare_counter_{0};
    AdmittanceMode mode_{AdmittanceMode::Idle};
};

} // namespace robotics::control
