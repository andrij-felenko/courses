#pragma once

#include <cstdint>
#include <string_view>
#include <chrono>
#include <optional>
#include <span>

namespace isa18_2 {

using namespace std::chrono_literals;

inline constexpr size_t MaxAlarms = 64;
inline constexpr std::chrono::milliseconds AlarmRateWindow = 10min;
inline constexpr size_t AlarmFloodThreshold = 10;

/**
 * @brief Стани життєвого циклу тривоги за стандартом ANSI/ISA-18.2 та IEC 62682.
 */
enum class AlarmState : uint8_t {
    Normal = 0,             ///< Сигнал у межах норми, сигналізація пасивна
    UnacknowledgedAlarm,    ///< Вихід за межі норми, вимагає квитування оператором
    AcknowledgedAlarm,      ///< Активна тривога, підтверджена оператором
    ReturnToNormalUnack,    ///< Сигнал нормалізувався до підтвердження оператором
    Shelved,                ///< Тимчасово відкладена оператором на заданий час
    SuppressedByDesign,     ///< Пригнічена логікою режиму або батьківською тривогою
    OutOfService            ///< Виведена з експлуатації для технічного обслуговування
};

/**
 * @brief Пріоритети тривог згідно з ISA-18.2.
 */
enum class AlarmPriority : uint8_t {
    Diagnostic = 0,         ///< Діагностична інформація, без термінової загрози
    Low,                    ///< Низький: час реакції > 30 хв
    Medium,                 ///< Середній: час реакції 5..30 хв
    High,                   ///< Високий: час реакції 1..5 хв
    Critical                ///< Критичний: негайна реакція < 1 хв, загроза життю/катастрофи
};

/**
 * @brief Категорія виникнення тривоги.
 */
enum class AlarmCategory : uint8_t {
    Process = 0,
    Safety,
    SensorHealth,
    ActuatorFault,
    Communication
};

/**
 * @brief Експлуатаційні режими системи для динамічного пригнічення (State-based suppression).
 */
enum class SystemStateMask : uint32_t {
    ColdBoot    = (1U << 0),
    Standby     = (1U << 1),
    Armed       = (1U << 2),
    Mission     = (1U << 3),
    Failsafe    = (1U << 4),
    Maintenance = (1U << 5)
};

constexpr SystemStateMask operator|(SystemStateMask a, SystemStateMask b) noexcept {
    return static_cast<SystemStateMask>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr bool operator&(SystemStateMask a, SystemStateMask b) noexcept {
    return (static_cast<uint32_t>(a) & static_cast<uint32_t>(b)) != 0;
}

/**
 * @brief Специфікація та налаштування раціоналізованої тривоги.
 */
struct AlarmConfig {
    uint16_t id{};
    std::string_view tag{};
    std::string_view action_text{};
    std::string_view consequence{};
    AlarmPriority priority{AlarmPriority::Low};
    AlarmCategory category{AlarmCategory::Process};
    std::chrono::milliseconds response_time_limit{30000ms};

    /* Параметри гістерезису та усунення брязкоту */
    float trip_threshold{0.0f};
    float clear_threshold{0.0f};
    bool is_high_alarm{true};
    std::chrono::milliseconds on_delay{0ms};
    std::chrono::milliseconds off_delay{0ms};
    uint16_t chatter_limit{3};
    std::chrono::milliseconds chatter_window{5000ms};

    /* Логіка динамічного пригнічення */
    SystemStateMask suppression_mask{SystemStateMask::ColdBoot};
    std::optional<uint16_t> parent_alarm_id{std::nullopt};
};

/**
 * @brief Стан тривоги в пам'яті під час виконання.
 */
struct AlarmRuntime {
    AlarmState state{AlarmState::Normal};
    AlarmState prev_state{AlarmState::Normal};
    float current_value{0.0f};
    bool raw_trip_condition{false};

    std::chrono::milliseconds trip_start_time{0ms};
    std::chrono::milliseconds clear_start_time{0ms};
    std::chrono::milliseconds state_change_time{0ms};
    std::chrono::milliseconds shelved_until_time{0ms};

    uint16_t transitions_in_window{0};
    std::chrono::milliseconds first_transition_in_window{0ms};
    bool is_chattering{false};

    bool is_suppressed_by_state{false};
    bool is_suppressed_by_parent{false};
};

} // namespace isa18_2
