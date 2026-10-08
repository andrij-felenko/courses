#ifndef RS360SH_PUMP_DRIVER_HPP
#define RS360SH_PUMP_DRIVER_HPP

#include "mosfet_pwm_hal.hpp"
#include <cstdint>

/**
 * @brief Перелічення можливих станів скінченного автомата помпи.
 */
enum class PumpState {
    Idle,         ///< Помпа зупинена, очікує команду
    RampUp,       ///< Фаза плавного розгону (Soft Start)
    Dosing,       ///< Фаза стабільного дозування
    RampDown,     ///< Фаза плавного гальмування (Soft Stop)
    FaultDryRun   ///< Аварійний стан: виявлено сухий хід
};

/**
 * @brief Перелічення кодових помилок роботи дозатора.
 */
enum class PumpError {
    None,            ///< Помилок немає
    DryRun,          ///< Відсутня рідина в магістралі під час роботи
    Timeout,         ///< Перевищено максимальний час дозування
    InvalidConfig    ///< Некоректні параметри конфігурації
};

/**
 * @brief Конфігураційні параметри помпи RS-360SH та алгоритму дозування.
 */
struct PumpConfig {
    float max_flow_rate_ml_per_sec{15.0f};   ///< Номінальна витрата при 100% ШІМ (мл/с)
    std::uint32_t ramp_up_duration_ms{500};   ///< Тривалість плавного розгону (мс)
    std::uint32_t ramp_down_duration_ms{500}; ///< Тривалість плавного гальмування (мс)
    float min_operating_duty{0.25f};           ///< Мінімальна робоча свердловина ШІМ для подолання тертя
    float max_operating_duty{1.00f};           ///< Максимальна робоча свердловина ШІМ
    std::uint32_t dry_run_timeout_ms{1200};   ///< Таймаут відсутності потоку для виявлення сухого ходу (мс)
};

/**
 * @brief Показання датчика витрати рідини (Flow Sensor).
 */
struct FlowSensorData {
    bool sensor_present{false};           ///< Чи підключений фізичний датчик витрати
    float current_flow_ml_per_sec{0.0f};  ///< Виміряна поточна витрата (мл/с)
    std::uint32_t pulse_count{0};         ///< Загальна кількість імпульсів лічильника
};

/**
 * @brief Показання датчика наявності рідини в магістралі (Dry Run Sensor).
 */
struct DryRunSensorData {
    bool fluid_detected{true};                    ///< Прапорець наявності рідини в трубці
    std::uint32_t last_detection_timestamp_ms{0}; ///< Часова позначка останнього фіксування рідини
};

class RS360SHPumpDriver;

/**
 * @brief RAII-обгортка для гарантованого аварійного вимкнення силового MOSFET-ключа
 * при виході об'єкта з області видимості або виникненні винятків.
 */
class DosingGuard {
public:
    /**
     * @brief Конструктор захисного RAII-контролера.
     * @param driver Посилання на об'єкт драйвера помпи.
     */
    explicit DosingGuard(RS360SHPumpDriver& driver);

    /**
     * @brief Деструктор, який безпечно зупиняє помпу, якщо дозування не було підтверджено.
     */
    ~DosingGuard();

    DosingGuard(const DosingGuard&) = delete;
    DosingGuard& operator=(const DosingGuard&) = delete;

    DosingGuard(DosingGuard&& other) noexcept;
    DosingGuard& operator=(DosingGuard&& other) noexcept;

    /**
     * @brief Явне підтвердження успішного завершення дозування (деактивація захисного вимкнення).
     */
    void dismiss();

private:
    RS360SHPumpDriver* driver_{nullptr};
    bool armed_{true};
};

/**
 * @brief Завадостійкий C++ клас-драйвер водяної помпи RS-360SH з невикликаючим таймінгом.
 */
class RS360SHPumpDriver {
public:
    /**
     * @brief Конструктор драйвера помпи.
     * @param pwm_hal Низькорівневий модуль ШІМ-драйвера MOSFET.
     * @param config Конфігураційні параметри помпи.
     */
    explicit RS360SHPumpDriver(MosfetPwmHal& pwm_hal, const PumpConfig& config = PumpConfig());

    /**
     * @brief Ініціалізація драйвера помпи.
     * @return true у разі успішної ініціалізації периферії.
     */
    bool init();

    /**
     * @brief Запуск дозування заданого об'єму рідини у мілілітрах.
     * @param target_volume_ml Заданий об'єм у мл.
     * @param target_duty Цільова свердловина ШІМ [0.0..1.0].
     * @return true, якщо команду прийнято.
     */
    bool startDosingVolume(float target_volume_ml, float target_duty = 1.0f);

    /**
     * @brief Запуск дозування на фіксований проміжок часу.
     * @param target_duration_ms Заданий час прокачування у мілісекундах.
     * @param target_duty Цільова свердловина ШІМ [0.0..1.0].
     * @return true, якщо команду прийнято.
     */
    bool startDosingTime(std::uint32_t target_duration_ms, float target_duty = 1.0f);

    /**
     * @brief Примусова зупинка помпи з виконуванням плавного або негайного вимкнення.
     */
    void stop();

    /**
     * @brief Головна невикликаюча (non-blocking) функція оновлення стану дозатора.
     * @param current_time_ms Поточний системний час у мілісекундах (millis()).
     * @param flow_data Показання датчика витрати рідини.
     * @param dry_run_data Показання датчика сухого ходу.
     */
    void update(std::uint32_t current_time_ms,
                 const FlowSensorData& flow_data = FlowSensorData{},
                 const DryRunSensorData& dry_run_data = DryRunSensorData{});

    /**
     * @brief Отримання поточного стану скінченного автомата.
     */
    PumpState getState() const;

    /**
     * @brief Отримання останньої зафіксованої помилки.
     */
    PumpError getLastError() const;

    /**
     * @brief Отримання обчисленого об'єму рідини, поданого за поточний сеанс (мл).
     */
    float getDosedVolumeMl() const;

    /**
     * @brief Перевірка фіксації аварійного стану сухого ходу.
     */
    bool isDryRunDetected() const;

    /**
     * @brief Онлайн-калібрування об'ємної витрати рідини.
     * @param ml_per_sec_at_max_duty Об'ємна витрата (мл/с) при 100% ШІМ.
     */
    void setFlowRateCalibration(float ml_per_sec_at_max_duty);

    /**
     * @brief Скидання аварійного стану FaultDryRun та очищення помилок.
     */
    void clearFault();

private:
    void transitionTo(PumpState new_state, std::uint32_t current_time_ms);
    void handleDryRunCheck(std::uint32_t current_time_ms,
                            const FlowSensorData& flow_data,
                            const DryRunSensorData& dry_run_data);

    MosfetPwmHal& pwm_hal_;
    PumpConfig config_;
    PumpState state_{PumpState::Idle};
    PumpError last_error_{PumpError::None};

    std::uint32_t state_start_time_ms_{0};
    std::uint32_t dosing_start_time_ms_{0};
    std::uint32_t last_update_time_ms_{0};
    std::uint32_t total_target_duration_ms_{0};

    float target_pwm_duty_{1.0f};
    float current_pwm_duty_{0.0f};
    float target_volume_ml_{0.0f};
    float dosed_volume_ml_{0.0f};

    bool is_volume_mode_{false};
    bool first_update_in_session_{true};
    bool dry_run_detected_{false};
    std::uint32_t dry_run_timer_ms_{0};
};

#endif // RS360SH_PUMP_DRIVER_HPP
