#ifndef ENCODER_HPP
#define ENCODER_HPP

#include "stm32_timer_hal.hpp"
#include <cstdint>

/**
 * @brief Структура конфігураційних параметрів квадратурного енкодера.
 */
struct EncoderConfig {
    uint32_t pulses_per_revolution{1024}; //!< Кількість фізичних штрихів/імпульсів на один оберт (PPR)
    bool x4_encoding{true};               //!< Режим квадрокодування x4 (4 відліки на імпульс)
    uint8_t filter_icf{6};                //!< Коефіцієнт вхідного цифрового фільтра ICF (0..15)
    float speed_update_interval_sec{0.01f};//!< Номінальний інтервал дискретизації для швидкості (с)
    bool invert_direction{false};         //!< Прапорець реверсу напрямку відліків
};

/**
 * @brief Структура поточного обчисленого стану енкодера.
 */
struct EncoderState {
    int32_t raw_position_counts{0};    //!< Абсолютна 32-бітна позиція у тиках від старту/калібрування
    int32_t zero_offset_counts{0};     //!< Зсув відліку відносно апаратної Z-мітки
    float angle_radians{0.0f};         //!< Поточний кут повороту у радіанах
    float angle_degrees{0.0f};         //!< Поточний кут повороту у градусах
    float velocity_rad_per_sec{0.0f};  //!< Кутова швидкість обертання (рад/с)
    float velocity_rpm{0.0f};          //!< Швидкість обертання у RPM (об/хв)
    bool is_calibrated{false};         //!< Ознака завершення прив'язки до нуля по Z-мітці
};

/**
 * @brief C++ клас-драйвер квадратурного енкодера для мікроконтролерів STM32.
 * 
 * Клас інкапсулює низькорівневу роботу з периферійним таймером, забезпечує розширення
 * розрядності 16-бітного апаратного лічильника TIMx->CNT до 32-бітного знакового значення,
 * обробку Z-мітки (EXTI) та розрахунок кутової швидкості в реальному часі.
 */
class QuadratureEncoder {
public:
    /**
     * @brief Конструктор драйвера енкодера.
     * @param timer Посилання на апаратний об'єкт таймера.
     * @param config Структура конфігурації енкодера.
     */
    QuadratureEncoder(ITimerPeripheral& timer, const EncoderConfig& config);

    ~QuadratureEncoder() = default;

    // Заборона копіювання для запобігання дублюванню стану периферії
    QuadratureEncoder(const QuadratureEncoder&) = delete;
    QuadratureEncoder& operator=(const QuadratureEncoder&) = delete;

    // Дозвіл переміщення
    QuadratureEncoder(QuadratureEncoder&&) noexcept = default;
    QuadratureEncoder& operator=(QuadratureEncoder&&) noexcept = default;

    /**
     * @brief Ініціалізація апаратного таймера та внутрішніх змінних драйвера.
     */
    void init();

    /**
     * @brief Обробник переривання оновлення таймера (TIM Update Interrupt ISR).
     * Викликається з векторної таблиці ISR при переповненні (overflow) або підповненні (underflow).
     */
    void handleTimerOverflowISR();

    /**
     * @brief Обробник зовнішнього переривання індексної мітки Z (EXTI ISR).
     * Викликається при проходженні енкодером нульової позначки.
     */
    void handleIndexPulseISR();

    /**
     * @brief Періодичний метод оновлення стану та розрахунку кутової швидкості.
     * @param dt_seconds Фактичний квант часу від попереднього виклику у секундах.
     */
    void update(float dt_seconds);

    /**
     * @brief Отримання суцільної 32-бітної позиції у відліках.
     */
    [[nodiscard]] int32_t getPosition() const;

    /**
     * @brief Отримання кута у радіанах.
     */
    [[nodiscard]] float getAngleRad() const;

    /**
     * @brief Отримання кута у градусах.
     */
    [[nodiscard]] float getAngleDeg() const;

    /**
     * @brief Отримання кутової швидкості у рад/с.
     */
    [[nodiscard]] float getVelocityRadSec() const;

    /**
     * @brief Отримання кутової швидкості у RPM.
     */
    [[nodiscard]] float getVelocityRPM() const;

    /**
     * @brief Отримання повної структури стану енкодера.
     */
    [[nodiscard]] EncoderState getState() const;

    /**
     * @brief Перевірка стану калібрування по Z-мітці.
     */
    [[nodiscard]] bool isCalibrated() const;

    /**
     * @brief Програмне скидання або встановлення позиції.
     * @param new_position Нова позиція у відліках (за замовчуванням 0).
     */
    void resetPosition(int32_t new_position = 0);

    /**
     * @brief Отримання кількості відліків (тиків) на один повний оберт валу.
     */
    [[nodiscard]] uint32_t getCountsPerRev() const;

private:
    /**
     * @brief Обчислення атомарно-безпечного суцільного 32-бітного значення позиції.
     */
    [[nodiscard]] int32_t calculateContinuousPosition() const;

private:
    ITimerPeripheral& timer_;
    EncoderConfig config_;
    EncoderState state_{};

    volatile int32_t overflow_count_{0}; //!< Лічильник старших 16 біт (кількість переповнень таймера)
    int32_t last_sampled_position_{0};    //!< Позиція, збережена під час попереднього кванту часу
    uint32_t counts_per_rev_{4096};       //!< Розрахункова роздільна здатність: PPR * multiplier (4 або 2)
};

#endif // ENCODER_HPP
