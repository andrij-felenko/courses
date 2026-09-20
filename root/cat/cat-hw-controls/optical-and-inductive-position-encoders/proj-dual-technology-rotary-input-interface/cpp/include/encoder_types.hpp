#pragma once

#include <cstdint>
#include <string>

namespace controls::encoders {

/**
 * @brief Стан апаратного здоров'я первинного давача положення.
 */
enum class SensorHealth : uint8_t {
    OK = 0,             // Давач працює в межах норми
    SIGNAL_LOSS = 1,    // Обрив лінії або втрата сигналу
    OUT_OF_RANGE = 2,   // Значення виходить за допустимий фізичний діапазон
    HARDWARE_FAULT = 3  // Внутрішня апаратна несправність
};

/**
 * @brief Статус розбіжності між двома каналами вимірювання (Optical vs RVDT).
 */
enum class DiscrepancyStatus : uint8_t {
    OK = 0,                 // Розбіжність у межах допустимого допуску
    WARNING = 1,            // Попереджувальне розходження сигналів
    CRITICAL_FAULT = 2,     // Критична розбіжність каналів (Discrepancy Event)
    CALIBRATION_NEEDED = 3  // Потрібне калібрування нульової точки
};

/**
 * @brief Стан процедури автокалібрування нульової точки.
 */
enum class CalibrationState : uint8_t {
    UNCALIBRATED = 0,  // Система не відкалібрована
    IN_PROGRESS = 1,   // Триває вибірка відліків для обчислення зсуву
    CALIBRATED = 2,    // Автокалібрування успішно завершено
    FAILED = 3         // Калібрування не вдалося через високий рівень шуму
};

/**
 * @brief Структура виміряного положення окремого каналу.
 */
struct EncoderPosition {
    double angle_deg{0.0};              // Обчислений кут у градусах [-180.0, +180.0]
    double raw_value{0.0};              // Сирий відлік (імпульси або напруга АЦП)
    SensorHealth health{SensorHealth::OK}; // Стан здоров'я каналу
    uint64_t timestamp_us{0};           // Мітка часу вимірювання в мікросекундах
};

/**
 * @brief Конфігураційні параметри драйвера подвійного давача.
 */
struct DriverConfig {
    double max_allowed_discrepancy_deg{2.0};   // Поріг аварійної розбіжності між каналами (градуси)
    double warning_discrepancy_deg{1.0};       // Попереджувальний поріг розбіжності (градуси)
    double zero_offset_optical_deg{0.0};       // Початковий зсув нуля оптичного енкодера
    double zero_offset_rvdt_deg{0.0};          // Початковий зсув нуля індуктивного RVDT
    double max_single_step_spike_deg{15.0};    // Максимально припустимий стрибок за один цикл (фільтрація)
    uint32_t discrepancy_timeout_ms{200};      // Час тривання розбіжності перед викликом аварії (мс)
    uint32_t calibration_samples_count{50};    // Кількість відліків для усереднення при автокалібруванні
};

/**
 * @brief Підсумковий діагностичний звіт системи вимірювання положення.
 */
struct DiagnosticReport {
    double optical_angle_deg{0.0};      // Кут оптичного каналу
    double rvdt_angle_deg{0.0};         // Кут індуктивного каналу (RVDT)
    double fused_angle_deg{0.0};        // Скориговане зведене значення кута
    double current_discrepancy_deg{0.0}; // Поточна абсолютна розбіжність каналів
    DiscrepancyStatus status{DiscrepancyStatus::OK}; // Статус розбіжності
    CalibrationState calibration{CalibrationState::UNCALIBRATED}; // Стан калібрування
    bool system_valid{true};            // Загальний прапор довіри до вихідних даних
    std::string status_message;         // Текстове описове повідомлення діагностики
};

} // namespace controls::encoders
