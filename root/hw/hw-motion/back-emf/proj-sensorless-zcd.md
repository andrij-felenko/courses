# ⚙️ Драйвер безсенсорного детектування переходу протиЕРС через нуль (ZCD)

<preknowlist>
- [ПротиЕРС (back-EMF)](root:hw-motion/back-emf) — виникнення протидіючої напруги на вільній фазі мотора.
- [Стратегії комутації BLDC-мотора](root:hw-motion/bldc-commutation) — таблиця шести кроків та перемикання інвертора.
- [АЦП](root:hw-analog/adc) — перетворення аналогової напруги в цифровий код.
- [Компаратор](root:hw-analog/comparator) — апаратне порівняння двох напруг з формуванням логічного рівня.
</preknowlist>

У безсенсорному приводі безколекторного двигуна (Sensorless BLDC) мікроконтролер виконує роль електронного колектора: він вимірює напругу вільної фази, знаходить мить проходження протиЕРС через половину напруги живлення (`Vbus / 2`, подія ZCD), відраховує 30 електричних градусів і перемикає ключі інвертора на наступний крок шестикрокової послідовності.

Цей процес вимагає суворо детермінованої роботи в реальному часі. На високих обертах тривалість кроку комутації вимірюється десятками мікросекунд, тому будь-яка затримка в обробці переривань або похибка фільтрації призводить до випадання мотора з синхронізму.

---

### Архітектура безсенсорного драйвера

Життєвий цикл одного 60-градусного сектора комутації складається з чотирьох послідовних фаз:

```
[Комутація ключів]  →  [Вікно маскування t_blank]  →  [Очікування події ZCD]  →  [Затримка 30° t_delay]  →  [Наступна комутація]
```

1. **Комутація ключів:** Інвертор відкриває нову пару силових транзисторів (один верхній, один нижній) і залишає третю фазу у високоімпедансному стані. Одночасно аналоговий мультиплексор перемикає вхід компаратора на нову вільну фазу;
2. **Вікно маскування демагнетизації (Blanking Window):** У перші мікросекунди після комутації індуктивність відключеної фази скидає накопичений струм через зворотний діод протилежного ключа (індуктивний викид). Протягом цього часу напруга притиснута до живлення або землі, що створює хибний сигнал перетину нуля. Прошивка примусово блокує обробку переривань компаратора на час `t_blank ≈ t_step / 5`;
3. **Очікування переходу через нуль (ZCD Detection):** Щойно вікно маскування закінчується, компаратор переходить у режим очікування фронту протиЕРС (наростаючого або спадного залежно від парності кроку). Момент спрацьовування компаратора відповідає проходженню ротором середини сектора (30° електричних);
4. **Розрахунок затримки 30° та фазове випередження:** Контролер вимірює час від початку кроку до події ZCD і програмує апаратний таймер на затримку `t_delay = t_zcd_elapsed − t_filter_lag − t_advance`. Після спрацьовування таймера цикл повторюється для наступного кроку.

---

### Апаратне та програмне детектування: порівняння підходів

Існує дві основні стратегії детектування ZCD у вбудованих системах:

1. **Апаратний компаратор з перериванням (EXTI / Timer Input Capture):**
Сигнал із виходу дільника вільної фази порівнюється з віртуальною середньою точкою безпосередньо у внутрішньому аналоговому компараторі мікроконтролера. Вихід компаратора апаратно прив'язаний до тригера таймера захоплення.
- *Переваги:* Нульове навантаження на ядро процесора, миттєва реакція в межах десятків наносекунд.
- *Недоліки:* Чутливість до високочастотного аналогового бруду ШІМ, вимагає якісних RC-фільтрів.

2. **Синхронна вибірка швидкісним АЦП (ADC Triggered by PWM):**
АЦП налаштовується на запуск строго по центру періоду ШІМ (коли верхній або нижній ключ стабільно відкритий і комутаційні шуми мінімальні). Відліки зчитуються через DMA.
- *Переваги:* Можливість програмного цифрового фільтрування, динамічне обчислення віртуальної нейтралі без додаткових резисторів.
- *Недоліки:* Вимагає швидкісного АЦП (не менше 1–2 MSPS) та додаткових обчислень.

---

### Випередження фази комутації (Phase Advance)

На високих електричних частотах (`> 1500 Гц`) фазний струм відстає від напруги через індуктивність обмотки `L/R`. Якщо комутувати ключі строго на куті 60°, наростання струму запізнюється, і вектор магнітного поля статора відстає від ротора, що спричиняє падіння корисного моменту на 10–25%.

Для компенсації цього ефекту в алгоритм вводять **кут випередження фази** (англ. *Phase Advance*): затримку після ZCD скорочують на кут `θ_adv = 5°..15° ел.`. Це дозволяє струму нарости завчасно до моменту, коли ротор входить у зону максимального магнітного перекриття.

---

### Реалізація драйвера на мовах C та C++

Нижче наведено повністю працездатний драйвер кінцевого автомата 6-крокової комутації та безсенсорного детектування ZCD.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define NUM_COMM_STEPS 6

typedef enum {
    MOTOR_STATE_IDLE = 0,
    MOTOR_STATE_ALIGN,
    MOTOR_STATE_OPEN_LOOP_RAMP,
    MOTOR_STATE_CLOSED_LOOP
} MotorState;

typedef enum {
    ZCD_EDGE_RISING = 0,
    ZCD_EDGE_FALLING
} ZcdEdge;

// Конфігурація 6 кроків комутації (який міст активний, яка фаза вільна)
typedef struct {
    uint8_t high_side_pin;   // Фаза, підтягнута до Vbus (ШІМ)
    uint8_t low_side_pin;    // Фаза, підтягнута до GND
    uint8_t floating_phase;  // Вільна фаза (0=U, 1=V, 2=W)
    ZcdEdge expected_edge;   // Очікуваний напрям перетину нуля
} StepConfig;

static const StepConfig SIX_STEP_TABLE[NUM_COMM_STEPS] = {
    {0, 1, 2, ZCD_EDGE_RISING},   // Крок 0: U+, V-, W вільна (наростання)
    {0, 2, 1, ZCD_EDGE_FALLING},  // Крок 1: U+, W-, V вільна (спад)
    {1, 2, 0, ZCD_EDGE_RISING},   // Крок 2: V+, W-, U вільна (наростання)
    {1, 0, 2, ZCD_EDGE_FALLING},  // Крок 3: V+, U-, W вільна (спад)
    {2, 0, 1, ZCD_EDGE_RISING},   // Крок 4: W+, U-, V вільна (наростання)
    {2, 1, 0, ZCD_EDGE_FALLING}   // Крок 5: W+, V-, U вільна (спад)
};

typedef struct {
    MotorState state;
    uint8_t current_step;
    uint32_t last_comm_time_us;     // Час останнього перемикання ключів
    uint32_t step_duration_us;       // Тривалість останнього кроку 60°
    uint32_t blanking_time_us;      // Час маскування викиду індуктивності
    bool zcd_detected;
    uint16_t zcd_valid_count;
    uint32_t open_loop_delay_us;
} BldcController;

// Апаратні заглушки під платформу (STM32 / ESP32)
void hw_set_inverter_step(uint8_t step);
void hw_set_pwm_duty(uint16_t duty);
void hw_select_comparator_phase(uint8_t phase_index);
void hw_schedule_timer_interrupt(uint32_t delay_us);
uint32_t hw_get_micros(void);

void bldc_init(BldcController *ctrl) {
    ctrl->state = MOTOR_STATE_IDLE;
    ctrl->current_step = 0;
    ctrl->last_comm_time_us = 0;
    ctrl->step_duration_us = 2000;
    ctrl->blanking_time_us = 400;
    ctrl->zcd_detected = false;
    ctrl->zcd_valid_count = 0;
    ctrl->open_loop_delay_us = 5000;
}

// Запуск розгону мотора
void bldc_start(BldcController *ctrl) {
    ctrl->state = MOTOR_STATE_ALIGN;
    ctrl->current_step = 0;
    hw_set_pwm_duty(300); // 30% струму для початкової фіксації
    hw_set_inverter_step(0);
    hw_schedule_timer_interrupt(50000); // 50 мс на вирівнювання ротора
}

// Перемикання на наступний сектор 60°
void bldc_advance_commutation(BldcController *ctrl) {
    uint32_t now = hw_get_micros();
    ctrl->step_duration_us = now - ctrl->last_comm_time_us;
    ctrl->last_comm_time_us = now;

    // Перехід на наступний крок таблиці
    ctrl->current_step = (ctrl->current_step + 1) % NUM_COMM_STEPS;
    hw_set_inverter_step(ctrl->current_step);

    // Маскування комутаційного викиду: перші 20% часу кроку
    ctrl->blanking_time_us = ctrl->step_duration_us / 5;
    if (ctrl->blanking_time_us < 20) {
        ctrl->blanking_time_us = 20; // Мінімум 20 мкс на спад струму діода
    }

    ctrl->zcd_detected = false;

    // Підключення компаратора до нової вільної фази
    uint8_t free_phase = SIX_STEP_TABLE[ctrl->current_step].floating_phase;
    hw_select_comparator_phase(free_phase);
}

// Обробник переривання апаратного компаратора / детектора нуля
void bldc_on_comparator_event(BldcController *ctrl) {
    if (ctrl->state != MOTOR_STATE_CLOSED_LOOP) {
        return;
    }

    uint32_t elapsed = hw_get_micros() - ctrl->last_comm_time_us;

    // Захист: ігноруємо події всередині вікна маскування демагнетизації
    if (elapsed < ctrl->blanking_time_us) {
        return;
    }

    if (!ctrl->zcd_detected) {
        ctrl->zcd_detected = true;

        // Затримка 30° електричних: половина тривалості поточного сектора
        uint32_t delay_30deg_us = elapsed; // Час від початку кроку до ZCD і є ~30°
        if (delay_30deg_us > 10) {
            // Компенсація фазової затримки RC-фільтра (~15 мкс)
            uint32_t rc_filter_lag_us = 15;
            if (delay_30deg_us > rc_filter_lag_us) {
                delay_30deg_us -= rc_filter_lag_us;
            }
            hw_schedule_timer_interrupt(delay_30deg_us);
        } else {
            bldc_advance_commutation(ctrl);
        }
    }
}

// Періодичний таймер керування станом мотора
void bldc_on_timer_callback(BldcController *ctrl) {
    switch (ctrl->state) {
        case MOTOR_STATE_ALIGN:
            ctrl->state = MOTOR_STATE_OPEN_LOOP_RAMP;
            ctrl->open_loop_delay_us = 4000;
            bldc_advance_commutation(ctrl);
            hw_schedule_timer_interrupt(ctrl->open_loop_delay_us);
            break;

        case MOTOR_STATE_OPEN_LOOP_RAMP:
            bldc_advance_commutation(ctrl);
            // Прискорення розгону наосліп
            if (ctrl->open_loop_delay_us > 800) {
                ctrl->open_loop_delay_us -= 100;
                hw_schedule_timer_interrupt(ctrl->open_loop_delay_us);
            } else {
                // Перехід у замкнений контур
                ctrl->state = MOTOR_STATE_CLOSED_LOOP;
                ctrl->last_comm_time_us = hw_get_micros();
            }
            break;

        case MOTOR_STATE_CLOSED_LOOP:
            // Спрацював таймер 30° затримки після ZCD -> час комутації
            bldc_advance_commutation(ctrl);
            break;

        default:
            break;
    }
}
```
```cpp
#include <cstdint>
#include <array>
#include <algorithm>

enum class MotorState : uint8_t {
    Idle = 0,
    Align,
    OpenLoopRamp,
    ClosedLoop
};

enum class ZcdEdge : uint8_t {
    Rising = 0,
    Falling
};

struct StepConfig {
    uint8_t high_side_pin;
    uint8_t low_side_pin;
    uint8_t floating_phase;
    ZcdEdge expected_edge;
};

// Апаратний інтерфейс (ін'єкція залежностей)
struct IBldcHardware {
    virtual void setInverterStep(uint8_t step) = 0;
    virtual void setPwmDuty(uint16_t duty) = 0;
    virtual void selectComparatorPhase(uint8_t phaseIndex) = 0;
    virtual void scheduleTimerInterrupt(uint32_t delayUs) = 0;
    virtual uint32_t getMicros() const = 0;
    virtual ~IBldcHardware() = default;
};

class BldcSensorlessController {
public:
    static constexpr size_t kNumSteps = 6;

    explicit BldcSensorlessController(IBldcHardware& hardware)
        : hw_(hardware) {}

    void start(uint16_t alignDuty = 300) {
        state_ = MotorState::Align;
        currentStep_ = 0;
        hw_.setPwmDuty(alignDuty);
        hw_.setInverterStep(0);
        hw_.scheduleTimerInterrupt(50000); // 50 мс на вирівнювання
    }

    void stop() {
        state_ = MotorState::Idle;
        hw_.setPwmDuty(0);
    }

    // Викликається з ISR аналогового компаратора
    void onComparatorEdge() {
        if (state_ != MotorState::ClosedLoop) {
            return;
        }

        const uint32_t now = hw_.getMicros();
        const uint32_t elapsed = now - lastCommTimeUs_;

        // Фільтрація комутаційного викиду індуктивності
        if (elapsed < blankingTimeUs_) {
            return;
        }

        if (!zcdDetected_) {
            zcdDetected_ = true;

            // 30° затримка: тривалість від початку кроку до перетину нуля
            uint32_t delay30DegUs = elapsed;
            constexpr uint32_t kRcFilterLagUs = 15;

            if (delay30DegUs > kRcFilterLagUs) {
                delay30DegUs -= kRcFilterLagUs;
            }

            if (delay30DegUs > 10) {
                hw_.scheduleTimerInterrupt(delay30DegUs);
            } else {
                advanceCommutation();
            }
        }
    }

    // Викликається з ISR таймера
    void onTimerEvent() {
        switch (state_) {
            case MotorState::Align:
                state_ = MotorState::OpenLoopRamp;
                openLoopDelayUs_ = 4000;
                advanceCommutation();
                hw_.scheduleTimerInterrupt(openLoopDelayUs_);
                break;

            case MotorState::OpenLoopRamp:
                advanceCommutation();
                if (openLoopDelayUs_ > 800) {
                    openLoopDelayUs_ -= 100;
                    hw_.scheduleTimerInterrupt(openLoopDelayUs_);
                } else {
                    state_ = MotorState::ClosedLoop;
                    lastCommTimeUs_ = hw_.getMicros();
                }
                break;

            case MotorState::ClosedLoop:
                advanceCommutation();
                break;

            default:
                break;
        }
    }

    [[nodiscard]] MotorState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t stepDurationUs() const noexcept { return stepDurationUs_; }

private:
    void advanceCommutation() {
        const uint32_t now = hw_.getMicros();
        stepDurationUs_ = now - lastCommTimeUs_;
        lastCommTimeUs_ = now;

        currentStep_ = (currentStep_ + 1) % kNumSteps;
        hw_.setInverterStep(currentStep_);

        // Динамічне вікно маскування: 20% від тривалості сектора (мін. 20 мкс)
        blankingTimeUs_ = std::max<uint32_t>(20, stepDurationUs_ / 5);
        zcdDetected_ = false;

        const auto& cfg = kSixStepTable[currentStep_];
        hw_.selectComparatorPhase(cfg.floating_phase);
    }

    static constexpr std::array<StepConfig, kNumSteps> kSixStepTable = {{
        {0, 1, 2, ZcdEdge::Rising},   // 0: U+, V-, W floating
        {0, 2, 1, ZcdEdge::Falling},  // 1: U+, W-, V floating
        {1, 2, 0, ZcdEdge::Rising},   // 2: V+, W-, U floating
        {1, 0, 2, ZcdEdge::Falling},  // 3: V+, U-, W floating
        {2, 0, 1, ZcdEdge::Rising},   // 4: W+, U-, V floating
        {2, 1, 0, ZcdEdge::Falling}   // 5: W+, V-, U floating
    }};

    IBldcHardware& hw_;
    MotorState state_{MotorState::Idle};
    uint8_t currentStep_{0};
    uint32_t lastCommTimeUs_{0};
    uint32_t stepDurationUs_{2000};
    uint32_t blankingTimeUs_{400};
    uint32_t openLoopDelayUs_{5000};
    bool zcdDetected_{false};
};
```
:::

---

### Критичні пастки реалізації та захист від зриву

1. **Дрейф вікна маскування при різкому прискоренні:**
Під час різкого відкриття газу (`WOT — Wide Open Throttle`) швидкість зростає настільки стрімко, що тривалість поточного кроку може скоротитися вдвічі порівняно з попереднім. Якщо вікно маскування було обчислене за тривалістю попереднього кроку, воно може перевищити реальний момент ZCD, заблокувавши компаратор. Результат — пропуск комутації, миттєве заклинювання та коротке замикання через перехресне вмикання ключів.
*Рішення:* обмежувати максимальне вікно маскування жорсткою стелею у 25% від поточного очікуваного часу кроку.

2. **Детектування втрати синхронізму (Loss of Synchronization):**
Якщо таймер затримки не зафіксував перетин нуля протягом `1.5 · t_sector`, контролер повинен негайно вважати синхронізм зірваним: вимкнути всі 6 ключів (перевести інвертор у режим вільного вибігу), скинути накопичувальні регулятори та перезапустити процедуру пуску `Align -> Ramp`.

3. **Асиметрія плечей ШІМ:**
Якщо використовується асиметрична ШІМ (ШІМ модулюється лише на верхньому ключі, тоді як нижній ключ відкритий постійно), середня напруга нейтралі пульсує разом із тактовою частотою ШІМ. Для усунення помилок компаратора вибірку або спрацьовування стробують синхронно із серединою імпульсу ШІМ.
