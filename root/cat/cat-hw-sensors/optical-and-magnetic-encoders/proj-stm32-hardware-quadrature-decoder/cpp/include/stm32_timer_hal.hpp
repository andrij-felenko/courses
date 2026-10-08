#ifndef STM32_TIMER_HAL_HPP
#define STM32_TIMER_HAL_HPP

#include <cstdint>

/**
 * @brief Структура прямого відображення регістрів периферійного таймера STM32.
 * Відповідає апаратній пам'яті таймерів загального призначення (TIM2–TIM5) та розширених (TIM1, TIM8).
 */
struct TIM_RegisterMap {
    volatile uint32_t CR1;   //!< Control register 1 (керування режимом, напрямком, увімкненням)
    volatile uint32_t CR2;   //!< Control register 2 (керування магістраллю та тригерами)
    volatile uint32_t SMCR;  //!< Slave mode control register (вибір режиму квадратурного декодера)
    volatile uint32_t DIER;  //!< DMA/Interrupt enable register (дозвіл переривань оновлення/захоплення)
    volatile uint32_t SR;    //!< Status register (прапорці подій та переповнення)
    volatile uint32_t EGR;   //!< Event generation register (програмне генерування подій)
    volatile uint32_t CCMR1; //!< Capture/Compare mode register 1 (налаштування вхідних каналів CH1/CH2 та ICF)
    volatile uint32_t CCMR2; //!< Capture/Compare mode register 2 (налаштування вхідних каналів CH3/CH4)
    volatile uint32_t CCER;  //!< Capture/Compare enable register (полярність вхідних сигналів A/B)
    volatile uint32_t CNT;   //!< Counter register (16-бітний або 32-бітний апаратний лічильник)
    volatile uint32_t PSC;   //!< Prescaler register (дільник тактової частоти)
    volatile uint32_t ARR;   //!< Auto-reload register (верхня межа лічильника, 0xFFFF)
    volatile uint32_t RCR;   //!< Repetition counter register
    volatile uint32_t CCR1;  //!< Capture/compare register 1
    volatile uint32_t CCR2;  //!< Capture/compare register 2
    volatile uint32_t CCR3;  //!< Capture/compare register 3
    volatile uint32_t CCR4;  //!< Capture/compare register 4
    volatile uint32_t BDTR;  //!< Break and dead-time register
    volatile uint32_t DCR;   //!< DMA control register
    volatile uint32_t DMAR;  //!< DMA address for full transfer
};

// Бітові маски регістрів таймера STM32
namespace Stm32TimerRegs {
    constexpr uint32_t CR1_CEN       = (1U << 0);  //!< Counter Enable
    constexpr uint32_t CR1_DIR       = (1U << 4);  //!< Direction: 0 = Up, 1 = Down
    
    constexpr uint32_t SMCR_SMS_ENC3 = (0x3U << 0); //!< Encoder Mode 3: лічильник рахує по обох ребрах TI1 та TI2
    
    constexpr uint32_t CCMR1_CC1S_TI1 = (0x1U << 0); //!< Канал 1 сконфіговано як вхід TI1
    constexpr uint32_t CCMR1_CC2S_TI2 = (0x1U << 8); //!< Канал 2 сконфіговано як вхід TI2
    constexpr uint32_t CCMR1_IC1F_POS = 4;           //!< Зсув бітів фільтра завад IC1F
    constexpr uint32_t CCMR1_IC2F_POS = 12;          //!< Зсув бітів фільтра завад IC2F
    
    constexpr uint32_t CCER_CC1P     = (1U << 1);  //!< Полярність TI1 (0 = неінвертований)
    constexpr uint32_t CCER_CC2P     = (1U << 5);  //!< Полярність TI2 (0 = неінвертований)
    
    constexpr uint32_t DIER_UIE      = (1U << 0);  //!< Update Interrupt Enable
    constexpr uint32_t SR_UIF        = (1U << 0);  //!< Update Interrupt Flag
}

/**
 * @brief Чисто віртуальний абстрактний C++ інтерфейс периферійного таймера МК.
 * Забезпечує декуполювання драйвера енкодера від конкретної апаратної реалізації,
 * що дозволяє створювати Mock-об'єкти для модульного тестування (Unit Testing).
 */
class ITimerPeripheral {
public:
    virtual ~ITimerPeripheral() = default;

    /**
     * @brief Конфігурація таймера в режим квадратурного декодера x4 із цифровою фільтрацією.
     * @param filter_icf Значення коефіцієнта цифрового фільтра завад (ICF, 0..15).
     */
    virtual void initEncoderMode(uint8_t filter_icf) = 0;

    /**
     * @brief Отримання поточного значення апаратного лічильника CNT.
     * @return 16-бітне значення лічильника.
     */
    [[nodiscard]] virtual uint16_t getCounter() const = 0;

    /**
     * @brief Запис значення в апаратний лічильник CNT.
     * @param value Нове значення.
     */
    virtual void setCounter(uint16_t value) = 0;

    /**
     * @brief Перевірка напрямку лічби апаратного таймера.
     * @return true — лічба вниз (underflow/зворотний рух), false — лічба вгору (overflow/прямий рух).
     */
    [[nodiscard]] virtual bool isCountingDown() const = 0;

    /**
     * @brief Дозвіл переривання оновлення (Update Interrupt) при переповненні/підповненні.
     */
    virtual void enableUpdateInterrupt() = 0;

    /**
     * @brief Заборона переривання оновлення (Update Interrupt).
     */
    virtual void disableUpdateInterrupt() = 0;

    /**
     * @brief Перевірка та автоматичне очищення прапорця переривання оновлення (UIF).
     * @return true якщо переривання відбулося.
     */
    virtual bool getAndClearUpdateFlag() = 0;

    /**
     * @brief Перевірка прапорця переривання оновлення без очищення.
     * @return true якщо прапорець UIF встановлено.
     */
    [[nodiscard]] virtual bool getUpdateFlag() const = 0;

    /**
     * @brief Налаштування лінії переривання EXTI для обробки індексної мітки Z енкодера.
     */
    virtual void configureExtiZPin() = 0;
};

/**
 * @brief Конкретна реалізація C++ апаратного інтерфейсу для таймерів STM32.
 */
class Stm32Timer final : public ITimerPeripheral {
public:
    /**
     * @brief Конструктор апаратного таймера STM32.
     * @param timer_regs Вказівник на блок регістрів периферійного таймера (наприклад, TIM2, TIM3).
     */
    explicit Stm32Timer(TIM_RegisterMap* timer_regs) noexcept;

    ~Stm32Timer() override = default;

    void initEncoderMode(uint8_t filter_icf) override;
    [[nodiscard]] uint16_t getCounter() const override;
    void setCounter(uint16_t value) override;
    [[nodiscard]] bool isCountingDown() const override;
    void enableUpdateInterrupt() override;
    void disableUpdateInterrupt() override;
    bool getAndClearUpdateFlag() override;
    [[nodiscard]] bool getUpdateFlag() const override;
    void configureExtiZPin() override;

private:
    TIM_RegisterMap* regs_;
    bool exti_configured_{false};
};

#endif // STM32_TIMER_HAL_HPP
