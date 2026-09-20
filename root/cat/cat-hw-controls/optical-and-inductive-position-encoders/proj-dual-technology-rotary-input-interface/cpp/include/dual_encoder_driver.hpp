#pragma once

#include "position_sensor.hpp"
#include <memory>
#include <vector>
#include <functional>

namespace controls::encoders {

using DiscrepancyCallback = std::function<void(const DiagnosticReport&)>;

/**
 * @brief Головний інкапсульований драйвер дубльованого поворотного давача.
 */
class DualEncoderDriver {
public:
    /**
     * @brief Конструктор драйвера. Приймає володіння двома каналами давачів.
     */
    DualEncoderDriver(std::unique_ptr<IPositionSensor> optical_sensor,
                      std::unique_ptr<IPositionSensor> rvdt_sensor,
                      DriverConfig config = DriverConfig{});

    ~DualEncoderDriver() = default;

    // Заборона копіювання через унікальне володіння ресурсами
    DualEncoderDriver(const DualEncoderDriver&) = delete;
    DualEncoderDriver& operator=(const DualEncoderDriver&) = delete;

    /**
     * @brief Синхронне зчитування обох каналів та новий цикл обробки даних.
     */
    DiagnosticReport update();

    /**
     * @brief Ініціалізувати процедуру автоматичного калібрування нульової точки.
     */
    bool start_auto_zero_calibration();

    /**
     * @brief Отримати останній сформований діагностичний звіт.
     */
    DiagnosticReport get_last_report() const;

    /**
     * @brief Оновити конфігураційні параметри драйвера.
     */
    void set_config(const DriverConfig& config);

    /**
     * @brief Отримати поточну конфігурацію драйвера.
     */
    DriverConfig get_config() const;

    /**
     * @brief Зареєструвати зворотний виклик (callback) при виявленні події розбіжності.
     */
    void register_discrepancy_callback(DiscrepancyCallback callback);

private:
    double filter_outliers(double current_val, double prev_val, double max_step);
    DiscrepancyStatus evaluate_discrepancy(double diff_deg);
    void process_calibration_sample(double optical_angle, double rvdt_angle);
    void finalize_calibration();

    std::unique_ptr<IPositionSensor> optical_;
    std::unique_ptr<IPositionSensor> rvdt_;
    DriverConfig config_;
    DiagnosticReport last_report_;
    CalibrationState calibration_state_{CalibrationState::UNCALIBRATED};

    std::vector<double> calibration_samples_optical_;
    std::vector<double> calibration_samples_rvdt_;

    DiscrepancyCallback callback_{nullptr};
    uint64_t discrepancy_start_time_ms_{0};
    uint64_t system_tick_ms_{0};
    double prev_fused_angle_{0.0};
    bool first_update_{true};
};

} // namespace controls::encoders
