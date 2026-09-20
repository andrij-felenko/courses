#ifndef BLDC_CALIBRATOR_HPP_
#define BLDC_CALIBRATOR_HPP_

#include <cstdint>
#include <cstddef>
#include <array>
#include <algorithm>
#include <cmath>

namespace bldc_servo {

/**
 * @brief Апаратний низькорівневий інтерфейс трифазного силового інвертора BLDC-привода.
 */
class IInverter {
public:
    virtual ~IInverter() = default;

    /** @brief Активація вихідних силових ключів (ШІМ драйвера напівмостів). */
    virtual void enable() noexcept = 0;

    /** @brief Переведення ключів у високоімпедансний стан (безпечне знеструмлення обмоток). */
    virtual void disable() noexcept = 0;

    /**
     * @brief Подача статичного струму прямої осі Id для фазового вирівнювання ротора.
     * @param id_amps Струм вирівнювання в амперах (вектор фіксується вздовж осі фази A).
     */
    virtual void apply_id_vector(float id_amps) noexcept = 0;

    /**
     * @brief Подача векторного квадратурного струму моменту Iq під заданим електричним кутом.
     * @param iq_amps Цільовий квадратурний струм моменту (А).
     * @param electrical_angle_rad Миттєвий електричний кут поля статора (рад).
     */
    virtual void apply_torque_current(float iq_amps, float electrical_angle_rad) noexcept = 0;

    /** @brief Перевірка апаратного прапорця аварії (перевантаження по струму, перегрів, збій драйвера). */
    virtual bool is_fault() const noexcept = 0;
};

/**
 * @brief Апаратний інтерфейс датчика положення ротора (магнітний/оптичний енкодер).
 */
class IEncoder {
public:
    virtual ~IEncoder() = default;

    /** @brief Зчитування поточного сирого значення лічильника тіків енкодера. */
    virtual uint32_t read_raw_ticks() const noexcept = 0;

    /** @brief Кількість дискретних відліків на один повний механічний оберт (CPR). */
    virtual uint32_t counts_per_rev() const noexcept = 0;

    /** @brief Зчитування поточного абсолютного механічного кута ротора в радіанах [0..2*PI). */
    virtual float read_mechanical_angle_rad() const noexcept = 0;

    /** @brief Перевірка готовності та валідності даних енкодера (наявність зв'язку по шині SPI/SSI/ABZ). */
    virtual bool is_ready() const noexcept = 0;
};

/**
 * @brief Абстракція енергонезалежної пам'яті (EEPROM, Data Flash, FRAM).
 */
class INVMemory {
public:
    virtual ~INVMemory() = default;

    /** @brief Запис масиву байтів за вказаною адресою. */
    virtual bool write(uint32_t address, const uint8_t* data, size_t size) noexcept = 0;

    /** @brief Читання масиву байтів за вказаною адресою. */
    virtual bool read(uint32_t address, uint8_t* data, size_t size) const noexcept = 0;
};

/**
 * @brief Структура бінарного збереження калібрувальних параметрів привода.
 * Фіксоване вирівнювання гарантує переносність дампу пам'яті між різними архітектурами.
 */
#pragma pack(push, 1)
struct CalibrationData {
    uint32_t magic{0x43444C42};  // Сигнатура цілісності "BLDC" у Little Endian
    uint16_t version{1};          // Версія формату бінарної структури
    uint16_t pole_pairs{7};       // Кількість пар полюсів ротора
    float zero_offset_rad{0.0f};  // Визначене зміщення електричного нуля енкодера (рад)
    float pos_kp{20.0f};          // Пропорційний коефіцієнт контуру позиції (1/с)
    float pos_ki{0.0f};           // Інтегральний коефіцієнт контуру позиції (1/с^2)
    float vel_kp{0.15f};          // Пропорційний коефіцієнт контуру швидкості (А*с/рад)
    float vel_ki{3.0f};           // Інтегральний коефіцієнт контуру швидкості (А/рад)
    uint32_t crc32{0};            // Контрольна сума CRC32 корисного навантаження
};
#pragma pack(pop)

/**
 * @brief Клас безпечного збереження, верифікації та відновлення калібрувальних параметрів.
 */
class CalibrationStorage {
public:
    explicit CalibrationStorage(INVMemory& memory, uint32_t base_address = 0x0000) noexcept
        : memory_(memory), base_address_(base_address) {}

    /** @brief Обчислення контрольної суми CRC32 за алгоритмом IEEE 802.3. */
    [[nodiscard]] static uint32_t calculate_crc32(const uint8_t* data, size_t length) noexcept;

    /** @brief Валідація структури за магічним числом, версією та контрольною сумою. */
    [[nodiscard]] static bool validate(const CalibrationData& data) noexcept;

    /** @brief Збереження структури з обчисленням CRC32 та верифікацією зворотного читання. */
    bool save(const CalibrationData& data) noexcept;

    /** @brief Завантаження калібрування з енергонезалежної пам'яті з перевіркою цілісності. */
    bool load(CalibrationData& out_data) const noexcept;

    [[nodiscard]] uint32_t base_address() const noexcept { return base_address_; }

private:
    INVMemory& memory_;
    uint32_t base_address_{0};
};

/**
 * @brief Параметри коефіцієнтів та обмежень каскадного регулятора.
 */
struct ControllerGains {
    float pos_kp{20.0f};             // Контур положення: Kp (1/с)
    float pos_ki{0.0f};              // Контур положення: Ki (1/с^2)
    float vel_kp{0.15f};             // Контур швидкості: Kp (А*с/рад)
    float vel_ki{3.0f};              // Контур швидкості: Ki (А/рад)
    float max_velocity_rad_s{60.0f}; // Максимальна дозволена швидкість (рад/с)
    float max_current_amps{6.0f};    // Максимальний струм моменту Iq (А)
};

/**
 * @brief Каскадний регулятор (Положення -> Швидкість -> Струм Iq) із захистом Anti-Windup.
 */
class CascadeController {
public:
    explicit CascadeController(const ControllerGains& gains = {}) noexcept
        : gains_(gains) {}

    /**
     * @brief Розрахунок одного кроку каскадного контуру регулювання.
     * @param target_pos_rad Цільове положення ротора (рад).
     * @param actual_pos_rad Виміряне фактичне положення ротора (рад).
     * @param dt_seconds Час між викликами контуру (с).
     * @return Цільовий квадратурний струм моменту Iq (А).
     */
    float update(float target_pos_rad, float actual_pos_rad, float dt_seconds) noexcept;

    /**
     * @brief Аналітичний розрахунок коефіцієнтів під динамічні параметри механічного навантаження.
     * @param inertia_kg_m2 Сумарний момент інерції ротора та приєднаного навантаження (кг*м^2).
     * @param target_bw_rad_s Бажана смуга пропускання контуру швидкості (рад/с).
     * @param kt_nm_a Коефіцієнт електромеханічного моменту двигуна (Н*м/А).
     */
    void tune_for_load(float inertia_kg_m2, float target_bw_rad_s, float kt_nm_a) noexcept;

    /** @brief Скидання інтеграторів та внутрішнього фільтра швидкості. */
    void reset() noexcept;

    void set_gains(const ControllerGains& gains) noexcept { gains_ = gains; }
    [[nodiscard]] const ControllerGains& gains() const noexcept { return gains_; }
    [[nodiscard]] float target_velocity() const noexcept { return target_vel_rad_s_; }
    [[nodiscard]] float actual_velocity() const noexcept { return actual_vel_rad_s_; }

private:
    ControllerGains gains_{};
    float pos_integral_{0.0f};
    float vel_integral_{0.0f};
    float last_pos_rad_{0.0f};
    float target_vel_rad_s_{0.0f};
    float actual_vel_rad_s_{0.0f};
    bool is_first_update_{true};
};

/**
 * @brief Точка збереження телеметрії перехідної характеристики.
 */
struct TelemetryPoint {
    uint32_t timestamp_ms{0};
    float target_pos_rad{0.0f};
    float actual_pos_rad{0.0f};
    float target_vel_rad_s{0.0f};
    float actual_vel_rad_s{0.0f};
    float current_iq_amps{0.0f};
};

/**
 * @brief Показники якості перехідного процесу під час стрибкового збурення.
 */
struct StepMetrics {
    float rise_time_ms{0.0f};          // Час наростання (10% -> 90% від стрибка)
    float settling_time_ms{0.0f};      // Час заспокоєння в зону допуску +-5%
    float overshoot_percent{0.0f};     // Максимальне динамічне перерегулювання (%)
    float steady_state_error_rad{0.0f};// Залишкова статична похибка в кінці тесту (рад)
    bool is_stable{false};             // Ознака відповідності процесу критеріям стійкості
};

/** @brief Фіксований обсяг буфера точок телеметрії (виключає динамічну пам'ять у реальному часі). */
inline constexpr size_t kMaxTelemetryPoints = 80;

/**
 * @brief Стан скінченного автомата автоналагодження сервопривода.
 */
enum class CalibrationState : uint8_t {
    Idle = 0,
    AligningPhases,     // Подача вектора Id для вирівнювання ротора за фазою A
    DetectingZero,      // Зчитування енкодера та визначення електричного нуля
    TuningGains,        // Аналітичний розрахунок параметрів регуляторів
    RunningStepTest,    // Виконання тестового стрибка та збір телеметрії
    EvaluatingMetrics,  // Розрахунок показників перехідної характеристики
    SavingCalibration,  // Запис зміщення та коефіцієнтів у пам'ять із CRC32
    Completed,          // Автоналагодження успішно виконано
    Fault               // Аварійний стан помилки калібрування
};

/**
 * @brief Код причини аварійного завершення автоналагодження.
 */
enum class CalibrationError : uint8_t {
    None = 0,
    InverterHardwareFault,
    EncoderHardwareFault,
    RotorMotionTimeout,
    StepResponseUnstable,
    StorageWriteFailed,
    StorageCrcMismatch
};

/**
 * @brief Головний клас-калібратор та автоналагоджувач BLDC сервоконтролера.
 */
class BldcCalibrator {
public:
    BldcCalibrator(IInverter& inverter,
                   IEncoder& encoder,
                   CascadeController& controller,
                   CalibrationStorage& storage,
                   uint16_t pole_pairs = 7,
                   float motor_kt_nm_a = 0.08f) noexcept;

    /**
     * @brief Запуск повного циклу автоналагодження.
     * @param step_magnitude_rad Амплітуда тестового стрибка положення (рад).
     */
    void start_calibration(float step_magnitude_rad = 1.0f) noexcept;

    /**
     * @brief Періодичний крок скінченного автомата (викликається в диспетчері задач).
     * @param current_time_ms Поточний системний час у мілісекундах.
     */
    void step(uint32_t current_time_ms) noexcept;

    /** @brief Примусова зупинка калібрування з переведенням інвертора в безпечний стан. */
    void abort() noexcept;

    /** @brief Скидання стану автомата в Idle. */
    void reset() noexcept;

    [[nodiscard]] CalibrationState state() const noexcept { return state_; }
    [[nodiscard]] CalibrationError last_error() const noexcept { return last_error_; }
    [[nodiscard]] const char* state_name() const noexcept;
    [[nodiscard]] const char* error_name() const noexcept;
    [[nodiscard]] float zero_offset_rad() const noexcept { return zero_offset_rad_; }
    [[nodiscard]] const StepMetrics& step_metrics() const noexcept { return step_metrics_; }
    [[nodiscard]] size_t telemetry_count() const noexcept { return telemetry_count_; }
    [[nodiscard]] const std::array<TelemetryPoint, kMaxTelemetryPoints>& telemetry_buffer() const noexcept {
        return telemetry_buffer_;
    }
    [[nodiscard]] bool is_completed() const noexcept { return state_ == CalibrationState::Completed; }
    [[nodiscard]] bool has_fault() const noexcept { return state_ == CalibrationState::Fault; }

private:
    void transition_to(CalibrationState new_state, uint32_t now_ms) noexcept;
    void fail(CalibrationError error) noexcept;
    void process_aligning_phases(uint32_t now_ms) noexcept;
    void process_detecting_zero() noexcept;
    void process_tuning_gains() noexcept;
    void process_running_step(uint32_t now_ms) noexcept;
    void process_evaluating_metrics() noexcept;
    void process_saving_calibration() noexcept;

    IInverter& inverter_;
    IEncoder& encoder_;
    CascadeController& controller_;
    CalibrationStorage& storage_;

    uint16_t pole_pairs_{7};
    float motor_kt_nm_a_{0.08f};
    float align_current_amps_{1.5f};
    float step_magnitude_rad_{1.0f};

    CalibrationState state_{CalibrationState::Idle};
    CalibrationError last_error_{CalibrationError::None};

    uint32_t state_start_time_ms_{0};
    uint32_t last_step_time_ms_{0};
    float zero_offset_rad_{0.0f};
    float test_start_pos_rad_{0.0f};

    std::array<TelemetryPoint, kMaxTelemetryPoints> telemetry_buffer_{};
    size_t telemetry_count_{0};
    StepMetrics step_metrics_{};
};

} // namespace bldc_servo

#endif // BLDC_CALIBRATOR_HPP_
