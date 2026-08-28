// migration_controller.cpp - Ідіоматична C++20 реалізація контролера відкату
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <expected>
#include <span>
#include <string_view>
#include <functional>

enum class MigrationState {
    Idle,
    SchemaExpanding,
    CanaryMonitoring,
    RollbackTraffic,
    RollbackSchema,
    SchemaContracting,
    Completed,
    Failed
};

struct SloConfig {
    double max_p99_latency_ms{150.0};
    double max_error_rate_pct{0.5};
    std::chrono::seconds monitoring_window{300};
};

struct TelemetryMetrics {
    double current_p99_ms{0.0};
    double current_error_rate_pct{0.0};
    uint64_t total_requests{0};
};

enum class ControllerError {
    SloBreachLatency,
    SloBreachErrors,
    SchemaExpandFailed,
    RollbackExecutionError
};

// RAII обгортка для безпечного відновлення стану при винятках чи відкаті
class RollbackGuard {
public:
    explicit RollbackGuard(std::function<void()> rollback_action)
        : action_(std::move(rollback_action)), active_(true) {}

    ~RollbackGuard() {
        if (active_ && action_) {
            std::cout << "[RAII GUARD] Спрацював автоматичний захисний тригер відкату!\n";
            action_();
        }
    }

    void dismiss() noexcept { active_ = false; }

    RollbackGuard(const RollbackGuard&) = delete;
    RollbackGuard& operator=(const RollbackGuard&) = delete;
    RollbackGuard(RollbackGuard&& other) noexcept
        : action_(std::move(other.action_)), active_(other.active_) {
        other.active_ = false;
    }

private:
    std::function<void()> action_;
    bool active_{true};
};

class ModernMigrationController {
public:
    ModernMigrationController(std::string_view v1, std::string_view v2, SloConfig slo)
        : version_v1_(v1), version_v2_(v2), slo_(slo), state_(MigrationState::Idle) {}

    [[nodiscard]] MigrationState state() const noexcept { return state_; }

    std::expected<void, ControllerError> execute_schema_expand() {
        std::cout << "[C++ DDL EXPAND] Додавання нових колонок у режимі Expand...\n";
        state_ = MigrationState::SchemaExpanding;
        schema_reversible_ = true;
        return {};
    }

    void perform_traffic_rollback() {
        state_ = MigrationState::RollbackTraffic;
        std::cout << "[C++ ROLLBACK] 🚨 Автоматичне перемикання 100% трафіку назад на: " << version_v1_ << "\n";
        std::cout << "[C++ ROLLBACK] Feature Flag `v2_enabled` встановлено у false.\n";
        
        if (schema_reversible_) {
            state_ = MigrationState::RollbackSchema;
            std::cout << "[C++ ROLLBACK] Схема даних у безпечному Expand-стані. Жодне поле не видалялося.\n";
        }
        state_ = MigrationState::Completed;
    }

    std::expected<void, ControllerError> run_canary_deployment(std::span<const TelemetryMetrics> samples) {
        auto expand_res = execute_schema_expand();
        if (!expand_res) return std::unexpected(expand_res.error());

        // Створюємо RAII guard: якщо функція завершиться з помилкою, guard автоматично виконає відкат
        RollbackGuard guard([this]() { this->perform_traffic_rollback(); });

        state_ = MigrationState::CanaryMonitoring;
        std::cout << "[C++ CANARY] Початок аналізу метрик для канарейки " << version_v2_ << "\n";

        for (size_t i = 0; i < samples.size(); ++i) {
            const auto& sample = samples[i];
            std::cout << "[C++ MONITORING] Замір #" << (i + 1)
                      << ": Latency=" << sample.current_p99_ms
                      << "ms, Errors=" << sample.current_error_rate_pct << "%\n";

            if (sample.current_p99_ms > slo_.max_p99_latency_ms) {
                std::cout << "[C++ SLO BREACH] P99 Latency деградувала!\n";
                return std::unexpected(ControllerError::SloBreachLatency);
            }
            if (sample.current_error_rate_pct > slo_.max_error_rate_pct) {
                std::cout << "[C++ SLO BREACH] Рівень помилок перевищено!\n";
                return std::unexpected(ControllerError::SloBreachErrors);
            }
        }

        // Метрики в нормі: деактивуємо guard відкату та завершуємо реліз
        guard.dismiss();
        state_ = MigrationState::SchemaContracting;
        std::cout << "[C++ CONTRACT] Реліз v2 успішний. Перехід до стабільної фази.\n";
        state_ = MigrationState::Completed;
        return {};
    }

private:
    std::string version_v1_;
    std::string version_v2_;
    SloConfig slo_;
    MigrationState state_{MigrationState::Idle};
    bool schema_reversible_{false};
};

int main() {
    SloConfig slo{.max_p99_latency_ms = 150.0, .max_error_rate_pct = 0.5};
    ModernMigrationController controller("v2.1.0", "v2.2.0", slo);

    std::vector<TelemetryMetrics> samples{
        {80.0, 0.02, 5000},
        {95.0, 0.04, 6000},
        {185.0, 1.20, 8000} // Збій Latency та Error Rate
    };

    std::cout << "=== СТАРТ C++20 АВТОМАТИЗОВАНОГО ВІДКАТУ ===\n";
    auto result = controller.run_canary_deployment(samples);

    if (!result) {
        std::cout << "=== ДЕПЛОЙ ЗУПИНЕНО ТА УСПІШНО ВІДКОЧЕНО ===\n";
    } else {
        std::cout << "=== ДЕПЛОЙ ЗАКІНЧЕНО УСПІШНО ===\n";
    }
    return 0;
}
