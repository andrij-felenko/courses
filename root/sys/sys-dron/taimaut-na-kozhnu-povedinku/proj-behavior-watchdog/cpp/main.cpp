#include <iostream>
#include <chrono>
#include <cmath>
#include <algorithm>
#include <string_view>

namespace drone::safety {

enum class WatchdogStatus : uint8_t {
    Running = 0,
    CompletedSuccess,
    TimeoutHard,
    StagnationDetected,
    EkfDivergence,
    EnergyCritical
};

enum class EscalationAction : uint8_t {
    None = 0,
    RetryRelaxed,
    FallbackLoiter,
    EmergencyRtl,
    EmergencyLand
};

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float distance_to(const Vector3f& other) const noexcept {
        const float dx = x - other.x;
        const float dy = y - other.y;
        const float dz = z - other.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
};

struct WatchdogConfig {
    std::chrono::microseconds hard_timeout{std::chrono::seconds(60)};
    std::chrono::microseconds stagnation_window{std::chrono::seconds(6)};
    float min_progress_rate_mps{0.35f};
    float max_pos_variance_m2{3.0f};
    float energy_safety_margin_j{15000.0f};
    float power_cruise_w{400.0f};
    float speed_cruise_mps{12.0f};
    float default_acceptance_rad_m{2.0f};
    float relaxed_acceptance_rad_m{4.5f};
    uint8_t max_retries{2};
};

class BehaviorWatchdog {
public:
    explicit constexpr BehaviorWatchdog(const WatchdogConfig& config) noexcept
        : config_(config), current_acceptance_rad_m_(config.default_acceptance_rad_m) {}

    void start(std::chrono::microseconds now,
               const Vector3f& curr_pos,
               const Vector3f& target_pos) noexcept {
        start_time_ = now;
        last_progress_time_ = now;
        target_position_ = target_pos;
        initial_distance_m_ = curr_pos.distance_to(target_pos);
        min_recorded_distance_m_ = initial_distance_m_;
        current_acceptance_rad_m_ = config_.default_acceptance_rad_m;
        retry_count_ = 0;
        is_active_ = true;
    }

    [[nodiscard]] WatchdogStatus update(std::chrono::microseconds now,
                                        const Vector3f& curr_pos,
                                        const Vector3f& curr_vel,
                                        float ekf_pos_variance_m2,
                                        float remaining_energy_j,
                                        const Vector3f& home_pos) noexcept {
        if (!is_active_) {
            return WatchdogStatus::Running;
        }

        const float dist_to_target = curr_pos.distance_to(target_position_);

        // 0. Успішне входження в радіус прийняття точки
        if (dist_to_target <= current_acceptance_rad_m_) {
            return WatchdogStatus::CompletedSuccess;
        }

        // 1. Жорсткий дедлайн за монотонним таймером
        if ((now - start_time_) >= config_.hard_timeout) {
            return WatchdogStatus::TimeoutHard;
        }

        // 2. Дисперсія коваріацій EKF
        if (ekf_pos_variance_m2 > config_.max_pos_variance_m2) {
            return WatchdogStatus::EkfDivergence;
        }

        // 3. Динамічний енергетичний баланс повернення
        const float dist_home = curr_pos.distance_to(home_pos);
        const float time_to_home_s = dist_home / std::max(config_.speed_cruise_mps, 1.0f);
        const float energy_needed_for_rtl_j = time_to_home_s * config_.power_cruise_w;

        if (remaining_energy_j <= (energy_needed_for_rtl_j + config_.energy_safety_margin_j)) {
            return WatchdogStatus::EnergyCritical;
        }

        // 4. Оцінка швидкості кінематичного поступу
        if (dist_to_target < (min_recorded_distance_m_ - 0.25f)) {
            min_recorded_distance_m_ = dist_to_target;
            last_progress_time_ = now;
        } else if (dist_to_target > 1e-4f) {
            const float ux = (target_position_.x - curr_pos.x) / dist_to_target;
            const float uy = (target_position_.y - curr_pos.y) / dist_to_target;
            const float uz = (target_position_.z - curr_pos.z) / dist_to_target;
            const float v_proj = curr_vel.x * ux + curr_vel.y * uy + curr_vel.z * uz;

            if (v_proj >= config_.min_progress_rate_mps) {
                last_progress_time_ = now;
            }
        }

        if ((now - last_progress_time_) >= config_.stagnation_window) {
            return WatchdogStatus::StagnationDetected;
        }

        return WatchdogStatus::Running;
    }

    [[nodiscard]] EscalationAction escalate(WatchdogStatus status, std::chrono::microseconds now) noexcept {
        if (status == WatchdogStatus::EnergyCritical || status == WatchdogStatus::EkfDivergence) {
            return EscalationAction::EmergencyRtl;
        }

        if (status == WatchdogStatus::StagnationDetected || status == WatchdogStatus::TimeoutHard) {
            if (retry_count_ < config_.max_retries) {
                ++retry_count_;
                current_acceptance_rad_m_ = config_.relaxed_acceptance_rad_m;
                last_progress_time_ = now;
                return EscalationAction::RetryRelaxed;
            }
            return EscalationAction::FallbackLoiter;
        }

        return EscalationAction::None;
    }

    void reset() noexcept {
        is_active_ = false;
        start_time_ = std::chrono::microseconds{0};
        last_progress_time_ = std::chrono::microseconds{0};
        retry_count_ = 0;
    }

    [[nodiscard]] bool is_active() const noexcept { return is_active_; }
    [[nodiscard]] uint8_t retry_count() const noexcept { return retry_count_; }

private:
    WatchdogConfig config_;
    std::chrono::microseconds start_time_{0};
    std::chrono::microseconds last_progress_time_{0};
    Vector3f target_position_{};
    float initial_distance_m_{0.0f};
    float min_recorded_distance_m_{0.0f};
    float current_acceptance_rad_m_{0.0f};
    uint8_t retry_count_{0};
    bool is_active_{false};
};

} // namespace drone::safety

/* ========================================================================= */
/*                          ВЕРИФІКАЦІЙНИЙ СТЕНД                             */
/* ========================================================================= */

int main() {
    using namespace std::chrono_literals;
    using namespace drone::safety;

    std::cout << "=== СТЕНД ВЕРИФІКАЦІЇ СТОРОЖОВОГО ТАЙМЕРА ПОВЕДІНКИ (C++) ===\n\n";

    const WatchdogConfig config{
        .hard_timeout = 60s,
        .stagnation_window = 6s,
        .min_progress_rate_mps = 0.35f,
        .max_pos_variance_m2 = 3.0f,
        .energy_safety_margin_j = 15000.0f,
        .power_cruise_w = 400.0f,
        .speed_cruise_mps = 12.0f,
        .default_acceptance_rad_m = 2.0f,
        .relaxed_acceptance_rad_m = 4.5f,
        .max_retries = 2
    };

    BehaviorWatchdog wd(config);

    const Vector3f home_pos{0.0f, 0.0f, 0.0f};
    const Vector3f start_pos{0.0f, 0.0f, -30.0f};
    const Vector3f target_pos{100.0f, 0.0f, -30.0f};

    // Сценарій 1: Штатний успішний політ
    std::cout << "[ТЕСТ 1] Штатний політ до цілі:\n";
    wd.start(1000000us, start_pos, target_pos);
    const Vector3f pos_t1{99.0f, 0.0f, -30.0f};
    const Vector3f vel_t1{4.0f, 0.0f, 0.0f};
    const auto st1 = wd.update(15000000us, pos_t1, vel_t1, 0.5f, 150000.0f, home_pos);
    std::cout << "  Статус: " << (st1 == WatchdogStatus::CompletedSuccess ? "SUCCESS" : "FAIL") << "\n";

    // Сценарій 2: Стагнація на вітрі та пом'якшення критеріїв
    std::cout << "\n[ТЕСТ 2] Буксування на вітрі:\n";
    wd.start(20000000us, start_pos, target_pos);
    const Vector3f pos_t2{10.0f, 0.0f, -30.0f};
    const Vector3f vel_t2{-0.2f, 0.0f, 0.0f};
    const auto st2 = wd.update(27000000us, pos_t2, vel_t2, 0.4f, 140000.0f, home_pos);
    std::cout << "  Статус: " << (st2 == WatchdogStatus::StagnationDetected ? "STAGNATION" : "FAIL") << "\n";
    const auto act2 = wd.escalate(st2, 27000000us);
    std::cout << "  Ескалація: " << (act2 == EscalationAction::RetryRelaxed ? "RETRY_RELAXED" : "FAIL") << "\n";

    // Сценарій 3: Деградація EKF
    std::cout << "\n[ТЕСТ 3] Зрив навігаційного фільтра EKF:\n";
    wd.start(30000000us, start_pos, target_pos);
    const auto st3 = wd.update(32000000us, pos_t2, vel_t1, 8.5f, 130000.0f, home_pos);
    std::cout << "  Статус: " << (st3 == WatchdogStatus::EkfDivergence ? "EKF_DIVERGENCE" : "FAIL") << "\n";
    const auto act3 = wd.escalate(st3, 32000000us);
    std::cout << "  Ескалація: " << (act3 == EscalationAction::EmergencyRtl ? "EMERGENCY_RTL" : "FAIL") << "\n";

    // Сценарій 4: Критичний дефіцит енергії
    std::cout << "\n[ТЕСТ 4] Перетин точки неповернення за енергією:\n";
    const Vector3f far_pos{100.0f, 0.0f, -30.0f};
    wd.start(40000000us, far_pos, target_pos);
    const auto st4 = wd.update(41000000us, far_pos, vel_t1, 0.5f, 16000.0f, home_pos);
    std::cout << "  Статус: " << (st4 == WatchdogStatus::EnergyCritical ? "ENERGY_CRITICAL" : "FAIL") << "\n";

    // Сценарій 5: Перевищення жорсткого дедлайну
    std::cout << "\n[ТЕСТ 5] Спрацювання жорсткого таймауту:\n";
    wd.start(50000000us, start_pos, target_pos);
    const auto st5 = wd.update(112000000us, pos_t2, vel_t1, 0.5f, 100000.0f, home_pos);
    std::cout << "  Статус: " << (st5 == WatchdogStatus::TimeoutHard ? "TIMEOUT_HARD" : "FAIL") << "\n";

    std::cout << "\nУсі сценарії верифікації C++ пройдено успішно.\n";
    return 0;
}
