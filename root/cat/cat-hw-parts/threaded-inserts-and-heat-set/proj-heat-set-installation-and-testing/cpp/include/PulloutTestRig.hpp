#pragma once

#include "LoadCell.hpp"
#include <chrono>
#include <deque>
#include <string_view>

struct TelemetryPoint {
    double timestamp_s;
    double force_n;
};

/**
 * @brief Контролер процесу механічних випробувань нарізних втулок на виривання.
 */
class PulloutTestRig {
public:
    enum class State {
        Idle,
        ElasticLoading,
        PlasticYield,
        PulloutFailure,
        Complete
    };

    explicit PulloutTestRig(LoadCell& sensor, std::size_t buffer_size = 64);

    /**
     * @brief Запускає нову сесію тестування з очищенням історії та скиданням станів.
     */
    void startSession();

    /**
     * @brief Виконує один вимірювальний крок стенда: зчитує тензодатчик, оновлює кільцевий буфер та аналізує стан.
     */
    void update();

    /**
     * @brief Перевіряє, чи завершено тест (після зриву втулки або таймауту).
     */
    [[nodiscard]] bool isTestFinished() const noexcept;

    [[nodiscard]] double getCurrentForce() const noexcept { return current_force_n_; }
    [[nodiscard]] double getPeakForce() const noexcept { return peak_force_n_; }
    [[nodiscard]] double getYieldForce() const noexcept { return yield_force_n_; }
    [[nodiscard]] State getState() const noexcept { return state_; }
    [[nodiscard]] std::string_view getStateName() const noexcept;

    /**
     * @brief Розраховує оцінку запасу міцності з'єднання відносно цільового стандарту.
     */
    [[nodiscard]] bool passesSpecification(double required_min_force_n = 500.0) const noexcept;

    /**
     * @brief Виводить підсумковий інженерний протокол сертифікації кріплення.
     */
    void printReport() const;

private:
    LoadCell& sensor_;
    std::size_t buffer_capacity_;
    std::deque<TelemetryPoint> ring_buffer_;
    std::chrono::steady_clock::time_point start_time_;

    double current_force_n_{0.0};
    double peak_force_n_{0.0};
    double yield_force_n_{0.0};
    double initial_stiffness_{0.0};
    State state_{State::Idle};
    bool test_finished_{false};

    void analyzeDynamics(double elapsed_s, double force);
};
