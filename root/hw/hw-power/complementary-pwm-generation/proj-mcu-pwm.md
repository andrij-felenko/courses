# ⚙️ Налаштування комплементарної ШІМ, генератора мертвого часу та захисту Break у мікроконтролерах

Надійне керування силовими транзисторами вимагає апаратного формування взаємно інверсних сигналів керування з гарантованою паузою між ними, яку неможливо порушити програмними затримками чи зависанням операційної системи. Нижче наведено практичні алгоритми, детальний розбір регістрової архітектури та структури коду для ініціалізації апаратних таймерів моторного класу (STM32 Advanced Timers TIM1/TIM8 та ESP32 MCPWM) з увімкненням генератора мертвого часу (DTG) та аварійного асинхронного відключення виходів через вхід Break (BKIN).

---

### 1. Архітектура розширених таймерів STM32 (TIM1 / TIM8 / TIM20)

Розширені таймери керування (Advanced-control timers) мікроконтролерів STM32 спроєктовані спеціально для симетричного керування трифазними інверторами та синхронними перетворювачами напруги. На відміну від звичайних таймерів загального призначення, вони містять повний апаратний конвеєр перетворення базового лічильника на пару комплементарних виходів із захистом від перекриття.

#### Конвеєр формування вихідного сигналу

1. **Базовий лічильник CNT і регістр автоперезавантаження ARR:** У силових приводах лічильник налаштовується в режим двонаправленого симетричного рахунку (Center-Aligned Mode 1, 2 або 3). Лічильник рахує від 0 до `ARR`, генерує подію переповнення на вершині, а потім рахує вниз від `ARR` до 0. Це створює симетричні трикутні імпульси ШІМ, що вдвічі знижує рівень електромагнітного шуму та гармонік струму в обмотках двигуна порівняно з пилкоподібним вирівнюванням по краю.
2. **Тіньові регістри порівняння (Shadow Registers):** При зміні коефіцієнта заповнення нове значення спочатку записується в буферний регістр `Preload`. Його перенесення в активний тіньовий регістр `Shadow` відбувається строго апаратно в момент проходження лічильника через нуль або вершину (подія `Update Event`). Це усуває небезпеку появи укорочених «голкоподібних» імпульсів посеред періоду ШІМ.
3. **Розгалужувач комплементарних каналів (CHx та CHxN):** Одноканальний результат порівняння розгалужується на прямий вихід `OCx` та інверсний `OCxN`.
4. **Блок впровадження мертвого часу (DTG):** Внутрішній лічильник мертвого часу перехоплює фронт наростання кожного з каналів і затримує його на запрограмовану кількість тактів, залишаючи фронти спадання миттєвими.
5. **Блок головного вихідного дозволу (MOE) та логіка Break:** Перед виходом на фізичні піни мікроконтролера обидва сигнали проходять через апаратний мультиплексор аварійного стану, підпорядкований біту `MOE` в регістрі `TIMx_BDTR`.

---

### 2. Розрахунок та встановлення регістра DTG у мікроконтролерах STM32

У розширених таймерах STM32 тривалість мертвого часу налаштовується 8-бітним полем `DTG[7:0]` у регістрі `TIMx_BDTR` (Break and Dead-Time Register). Перетворення бажаного часу `t_dead` у значення `DTG` реалізовано за нелінійною багатодіапазонною схемою, яка забезпечує субнаносекундну точність на малих значеннях і широкий діапазон для повільних модулів IGBT.

Формула кодування залежно від старших бітів:

```
Діапазон 1 (DTG[7] = 0):
  t_dead = DTG[6:0] · T_dts                       (крок 1·T_dts, від 0 до 127·T_dts)

Діапазон 2 (DTG[7:6] = 10):
  t_dead = (64 + DTG[5:0]) · 2 · T_dts           (крок 2·T_dts, від 128 до 254·T_dts)

Діапазон 3 (DTG[7:5] = 110):
  t_dead = (32 + DTG[4:0]) · 8 · T_dts           (крок 8·T_dts, від 256 до 504·T_dts)

Діапазон 4 (DTG[7:5] = 111):
  t_dead = (32 + DTG[4:0]) · 16 · T_dts          (крок 16·T_dts, від 512 до 1008·T_dts)
```

де `T_dts = 1 / f_dts` — період внутрішнього тактування фільтрів і мертвого часу, який задається дільником `CKD[1:0]` у регістрі `TIMx_CR1` (значення дільника: 1, 2 або 4 від частоти шини таймера).

#### Функція розрахунку значення DTG

:::tabs
```c
#include <stdint.h>

/**
 * @brief Обчислення коду регістра DTG для таймера STM32
 * @param dead_time_ns Бажаний мертвий час у наносекундах
 * @param timer_freq_hz Частота тактування таймера (наприклад, 168000000 для 168 МГц)
 * @return 8-бітне значення для запису в поле TIM_BDTR_DTG
 */
uint8_t stm32_calc_deadtime_dtg(uint32_t dead_time_ns, uint32_t timer_freq_hz) {
    // Період одного такту таймера у наносекундах (з фіксованою точкою x1000)
    uint64_t t_dts_ps = 1000000000000ULL / timer_freq_hz;
    uint32_t ticks = (uint32_t)((dead_time_ns * 1000ULL + t_dts_ps / 2) / t_dts_ps);

    if (ticks <= 127) {
        // Діапазон 1: DTG[7]=0, крок = 1 такт
        return (uint8_t)ticks;
    } else if (ticks <= 254) {
        // Діапазон 2: DTG[7:6]=10, крок = 2 такти
        uint32_t raw = (ticks / 2) - 64;
        if (raw > 0x3F) raw = 0x3F;
        return (uint8_t)(0x80 | raw);
    } else if (ticks <= 504) {
        // Діапазон 3: DTG[7:5]=110, крок = 8 тактів
        uint32_t raw = (ticks / 8) - 32;
        if (raw > 0x1F) raw = 0x1F;
        return (uint8_t)(0xC0 | raw);
    } else if (ticks <= 1008) {
        // Діапазон 4: DTG[7:5]=111, крок = 16 тактів
        uint32_t raw = (ticks / 16) - 32;
        if (raw > 0x1F) raw = 0x1F;
        return (uint8_t)(0xE0 | raw);
    }

    // Перевищення максимального діапазону: встановлюємо абсолютний максимум
    return 0xFF;
}
```
```cpp
#include <cstdint>
#include <algorithm>

namespace power_control {

class Stm32DeadTimeCalculator {
public:
    static constexpr uint8_t calculate_dtg(uint32_t dead_time_ns, uint32_t timer_freq_hz) noexcept {
        const uint64_t t_dts_ps = 1'000'000'000'000ULL / timer_freq_hz;
        const uint32_t ticks = static_cast<uint32_t>((dead_time_ns * 1'000ULL + t_dts_ps / 2) / t_dts_ps);

        if (ticks <= 127) {
            return static_cast<uint8_t>(ticks);
        }
        if (ticks <= 254) {
            const uint32_t raw = std::clamp((ticks / 2) - 64, 0u, 0x3Fu);
            return static_cast<uint8_t>(0x80 | raw);
        }
        if (ticks <= 504) {
            const uint32_t raw = std::clamp((ticks / 8) - 32, 0u, 0x1Fu);
            return static_cast<uint8_t>(0xC0 | raw);
        }
        if (ticks <= 1008) {
            const uint32_t raw = std::clamp((ticks / 16) - 32, 0u, 0x1Fu);
            return static_cast<uint8_t>(0xE0 | raw);
        }
        return 0xFF;
    }
};

} // namespace power_control
```
:::

---

### 3. Ініціалізація розширеного таймера STM32 TIM1 на бібліотеці Low-Layer (LL)

Використання прямих низькорівневих регістрових функцій (STM32 LL) гарантує повну прозорість генерації коду без прихованих накладних витрат та зайвих рівнів абстракції.

Повна конфігурація включає:
1. Налаштування тактування каналу ШІМ на частоті 50 кГц із центральним вирівнюванням;
2. Генерація комплементарної пари `TIM1_CH1` (PA8) та `TIM1_CH1N` (PB13);
3. Активація блоку мертвого часу (150 нс);
4. Налаштування апаратного входу `BKIN` (PA6) із цифровою фільтрацією брязкоту для миттєвого зняття сигналу дозволу виходів `MOE` при спрацюванні компаратора струму;
5. Встановлення бітів блокування `LOCK` для захисту конфігурації мертвого часу від випадкового перезапису за збою прошивки.

:::tabs
```c
#include "stm32f4xx_ll_tim.h"
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"

void tim1_complementary_pwm_init(uint32_t timer_clk_hz, uint32_t pwm_freq_hz, uint32_t dead_time_ns) {
    // 1. Увімкнення тактування портів GPIO та таймера TIM1
    LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_TIM1);
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);

    // 2. Конфігурація виводів: PA8 (CH1, High-Side), PB13 (CH1N, Low-Side)
    LL_GPIO_InitTypeDef gpio_init = {0};
    gpio_init.Pin = LL_GPIO_PIN_8;
    gpio_init.Mode = LL_GPIO_MODE_ALTERNATE;
    gpio_init.Speed = LL_GPIO_SPEED_FREQ_VERY_HIGH;
    gpio_init.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
    gpio_init.Pull = LL_GPIO_PULL_NO;
    gpio_init.Alternate = LL_GPIO_AF_1;
    LL_GPIO_Init(GPIOA, &gpio_init);

    gpio_init.Pin = LL_GPIO_PIN_13;
    LL_GPIO_Init(GPIOB, &gpio_init);

    // Вхід аварійного захисту BKIN (PA6, AF1, внутрішня підтяжка до землі)
    gpio_init.Pin = LL_GPIO_PIN_6;
    gpio_init.Pull = LL_GPIO_PULL_DOWN;
    LL_GPIO_Init(GPIOA, &gpio_init);

    // 3. Базове налаштування лічильника (Center-aligned Mode 1, симетричний рахунок)
    uint32_t arr_period = timer_clk_hz / (2 * pwm_freq_hz);
    LL_TIM_InitTypeDef tim_base = {0};
    tim_base.Prescaler = 0;
    tim_base.CounterMode = LL_TIM_COUNTERMODE_CENTER_UP_DOWN;
    tim_base.Autoreload = arr_period - 1;
    tim_base.ClockDivision = LL_TIM_CLOCKDIVISION_DIV1;
    tim_base.RepetitionCounter = 0;
    LL_TIM_Init(TIM1, &tim_base);

    // 4. Налаштування каналу 1 (PWM Mode 1 з увімкненим Preload)
    LL_TIM_OC_InitTypeDef oc_init = {0};
    oc_init.OCMode = LL_TIM_OCMODE_PWM1;
    oc_init.OCState = LL_TIM_OCSTATE_ENABLE;
    oc_init.OCNState = LL_TIM_OCNSTATE_ENABLE;
    oc_init.OCPolarity = LL_TIM_OCPOLARITY_HIGH;
    oc_init.OCNPolarity = LL_TIM_OCNPOLARITY_HIGH;
    oc_init.OCIdleState = LL_TIM_OCIDLESTATE_LOW;
    oc_init.OCNIdleState = LL_TIM_OCIDLESTATE_LOW;
    oc_init.CompareValue = arr_period / 2; // Початковий коефіцієнт заповнення 50%
    LL_TIM_OC_Init(TIM1, LL_TIM_CHANNEL_CH1, &oc_init);
    LL_TIM_OC_EnablePreload(TIM1, LL_TIM_CHANNEL_CH1);

    // 5. Конфігурація регістра BDTR (Dead-Time, Break Input та захист Lock)
    uint8_t dtg_val = stm32_calc_deadtime_dtg(dead_time_ns, timer_clk_hz);
    
    LL_TIM_BDTR_InitTypeDef bdtr_init = {0};
    bdtr_init.OSSRState = LL_TIM_OSSR_ENABLE;        // Стан виходів при активному таймері та MOE=0
    bdtr_init.OSSIState = LL_TIM_OSSI_ENABLE;        // Стан виходів при зупиненому таймері та MOE=0
    bdtr_init.LockLevel = LL_TIM_LOCKLEVEL_1;        // Захист бітів DTG від програмного збою
    bdtr_init.DeadTime = dtg_val;
    bdtr_init.BreakState = LL_TIM_BREAK_ENABLE;      // Увімкнення апаратного аварійного входу
    bdtr_init.BreakPolarity = LL_TIM_BREAK_POLARITY_HIGH; // Аварія при високому рівні на PA6
    bdtr_init.BreakFilter = LL_TIM_BREAK_FILTER_FDIV1_N4; // Фільтрація перешкод на 4 такти
    bdtr_init.AutomaticOutput = LL_TIM_AUTOMATIC_OUTPUT_DISABLE; // Блокування до явного скидання
    LL_TIM_BDTR_Init(TIM1, &bdtr_init);

    // 6. Увімкнення генерації події автооновлення, головного виходу та запуск таймера
    LL_TIM_EnableARRPreload(TIM1);
    LL_TIM_EnableAllOutputs(TIM1); // Встановлення біта MOE
    LL_TIM_EnableCounter(TIM1);
}
```
```cpp
#include "stm32f4xx_ll_tim.h"
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"

namespace power_control {

class HalfBridgePwmDriver {
public:
    struct Config {
        uint32_t timer_clk_hz{168'000'000};
        uint32_t pwm_freq_hz{50'000};
        uint32_t dead_time_ns{150};
    };

    explicit HalfBridgePwmDriver(const Config& cfg) noexcept : config_(cfg) {}

    void initialize() noexcept {
        enable_peripheral_clocks();
        configure_gpios();
        configure_timebase();
        configure_channel();
        configure_break_deadtime();

        LL_TIM_EnableARRPreload(TIM1);
        LL_TIM_EnableAllOutputs(TIM1);
        LL_TIM_EnableCounter(TIM1);
    }

    void set_duty_cycle(float duty_ratio) noexcept {
        const uint32_t arr = LL_TIM_GetAutoReload(TIM1);
        const uint32_t ccr = static_cast<uint32_t>(duty_ratio * static_cast<float>(arr));
        LL_TIM_OC_SetCompareCH1(TIM1, ccr);
    }

    bool is_break_triggered() const noexcept {
        return LL_TIM_IsActiveFlag_BRK(TIM1) != 0;
    }

    void clear_break_and_rearm() noexcept {
        LL_TIM_ClearFlag_BRK(TIM1);
        LL_TIM_EnableAllOutputs(TIM1); // Повторне зведення біта MOE
    }

private:
    Config config_;

    void enable_peripheral_clocks() noexcept {
        LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_TIM1);
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);
    }

    void configure_gpios() noexcept {
        LL_GPIO_InitTypeDef gpio = {};
        gpio.Pin = LL_GPIO_PIN_8;
        gpio.Mode = LL_GPIO_MODE_ALTERNATE;
        gpio.Speed = LL_GPIO_SPEED_FREQ_VERY_HIGH;
        gpio.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
        gpio.Alternate = LL_GPIO_AF_1;
        LL_GPIO_Init(GPIOA, &gpio);

        gpio.Pin = LL_GPIO_PIN_13;
        LL_GPIO_Init(GPIOB, &gpio);

        gpio.Pin = LL_GPIO_PIN_6;
        gpio.Pull = LL_GPIO_PULL_DOWN;
        LL_GPIO_Init(GPIOA, &gpio);
    }

    void configure_timebase() noexcept {
        const uint32_t arr = config_.timer_clk_hz / (2 * config_.pwm_freq_hz);
        LL_TIM_InitTypeDef tb = {};
        tb.Prescaler = 0;
        tb.CounterMode = LL_TIM_COUNTERMODE_CENTER_UP_DOWN;
        tb.Autoreload = arr - 1;
        tb.ClockDivision = LL_TIM_CLOCKDIVISION_DIV1;
        LL_TIM_Init(TIM1, &tb);
    }

    void configure_channel() noexcept {
        LL_TIM_OC_InitTypeDef oc = {};
        oc.OCMode = LL_TIM_OCMODE_PWM1;
        oc.OCState = LL_TIM_OCSTATE_ENABLE;
        oc.OCNState = LL_TIM_OCNSTATE_ENABLE;
        oc.OCPolarity = LL_TIM_OCPOLARITY_HIGH;
        oc.OCNPolarity = LL_TIM_OCNPOLARITY_HIGH;
        oc.OCIdleState = LL_TIM_OCIDLESTATE_LOW;
        oc.OCNIdleState = LL_TIM_OCIDLESTATE_LOW;
        oc.CompareValue = LL_TIM_GetAutoReload(TIM1) / 2;
        LL_TIM_OC_Init(TIM1, LL_TIM_CHANNEL_CH1, &oc);
        LL_TIM_OC_EnablePreload(TIM1, LL_TIM_CHANNEL_CH1);
    }

    void configure_break_deadtime() noexcept {
        const uint8_t dtg = Stm32DeadTimeCalculator::calculate_dtg(
            config_.dead_time_ns, config_.timer_clk_hz);

        LL_TIM_BDTR_InitTypeDef bdtr = {};
        bdtr.OSSRState = LL_TIM_OSSR_ENABLE;
        bdtr.OSSIState = LL_TIM_OSSI_ENABLE;
        bdtr.LockLevel = LL_TIM_LOCKLEVEL_1;
        bdtr.DeadTime = dtg;
        bdtr.BreakState = LL_TIM_BREAK_ENABLE;
        bdtr.BreakPolarity = LL_TIM_BREAK_POLARITY_HIGH;
        bdtr.BreakFilter = LL_TIM_BREAK_FILTER_FDIV1_N4;
        bdtr.AutomaticOutput = LL_TIM_AUTOMATIC_OUTPUT_DISABLE;
        LL_TIM_BDTR_Init(TIM1, &bdtr);
    }
};

} // namespace power_control
```
:::

---

### 4. Комплементарна ШІМ у мікроконтролерах ESP32 (Периферія MCPWM)

Периферійний модуль MCPWM (Motor Control PWM) у чипах Espressif ESP32/ESP32-S3 містить спеціалізований апаратний підмодуль **Dead-Time Submodule**. Він побудований за модульним принципом і дозволяє встановлювати повністю незалежні часи наростання (RED — Rising Edge Delay) та спадання (FED — Falling Edge Delay).

#### Архітектурні підмодулі ESP32 MCPWM:
- **MCPWM Timer:** Лічильник періоду (підтримує режим Up/Down для центрального вирівнювання).
- **MCPWM Operator:** Об'єднує генератори сигналів для однієї або кількох фаз.
- **MCPWM Comparator:** Порівнює лічильник зі значенням заповнення.
- **MCPWM Generator:** Формує вихідні імпульси за подіями таймера та компаратора.
- **Dead-Time Generator:** Здійснює апаратну затримку фронту наростання для захисту напівмоста.

:::tabs
```c
#include "driver/mcpwm_prelude.h"
#include "esp_log.h"

static const char *TAG = "MCPWM_HALF_BRIDGE";

void esp32_mcpwm_half_bridge_init(int high_side_gpio, int low_side_gpio, uint32_t dead_time_ns) {
    // 1. Створення таймера MCPWM (тактування 10 МГц, період 50 кГц у симетричному режимі)
    mcpwm_timer_handle_t timer = NULL;
    mcpwm_timer_config_t timer_config = {
        .group_id = 0,
        .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,
        .resolution_hz = 10000000, // 10 МГц (1 такт = 100 нс)
        .period_ticks = 100,       // 100 тактів вгору + 100 вниз = 200 тактів (50 кГц)
        .count_mode = MCPWM_TIMER_COUNT_MODE_UP_DOWN,
    };
    ESP_ERROR_CHECK(mcpwm_new_timer(&timer_config, &timer));

    // 2. Створення оператора (Operator) та прив'язка до таймера
    mcpwm_oper_handle_t oper = NULL;
    mcpwm_operator_config_t operator_config = {
        .group_id = 0,
    };
    ESP_ERROR_CHECK(mcpwm_new_operator(&operator_config, &oper));
    ESP_ERROR_CHECK(mcpwm_operator_connect_timer(oper, timer));

    // 3. Створення компаратора (Comparator) з оновленням за нульовим лічильником
    mcpwm_cmpr_handle_t comparator = NULL;
    mcpwm_comparator_config_t comparator_config = {
        .flags.update_cmp_on_tez = true,
    };
    ESP_ERROR_CHECK(mcpwm_new_comparator(oper, &comparator_config, &comparator));

    // 4. Створення генераторів для High-Side та Low-Side виводів
    mcpwm_gen_handle_t gen_high = NULL;
    mcpwm_generator_config_t gen_h_config = {.gen_gpio_num = high_side_gpio};
    ESP_ERROR_CHECK(mcpwm_new_generator(oper, &gen_h_config, &gen_high));

    mcpwm_gen_handle_t gen_low = NULL;
    mcpwm_generator_config_t gen_l_config = {.gen_gpio_num = low_side_gpio};
    ESP_ERROR_CHECK(mcpwm_new_generator(oper, &gen_l_config, &gen_low));

    // 5. Конфігурація подій виходу генератора PWM_H (високий рівень на початку, низький при співпадінні)
    ESP_ERROR_CHECK(mcpwm_generator_set_action_on_timer_event(
        gen_high,
        MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, MCPWM_TIMER_EVENT_EMPTY, MCPWM_GEN_ACTION_HIGH)));
    ESP_ERROR_CHECK(mcpwm_generator_set_action_on_compare_event(
        gen_high,
        MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, comparator, MCPWM_GEN_ACTION_LOW)));

    // 6. Активація блоку мертвого часу (Dead-Time Insertion)
    // 10 МГц -> 1 такт = 100 нс; перетворення наносекунд у такти таймера
    uint32_t dt_ticks = (dead_time_ns + 50) / 100;
    if (dt_ticks == 0) dt_ticks = 1;

    mcpwm_dead_time_config_t dt_config = {
        .posedge_path = MCPWM_DEAD_TIME_PATH_ACTIVE,
        .negedge_path = MCPWM_DEAD_TIME_PATH_INVERT, // Інверсія для створення комплементарного каналу
    };
    ESP_ERROR_CHECK(mcpwm_generator_set_dead_time(gen_high, gen_high, &dt_config));
    ESP_ERROR_CHECK(mcpwm_generator_set_dead_time(gen_high, gen_low, &dt_config));

    // 7. Увімкнення та запуск таймера
    ESP_ERROR_CHECK(mcpwm_timer_enable(timer));
    ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP));
    ESP_LOGI(TAG, "ESP32 MCPWM Complementary pair initialized, DeadTime=%u ns", (unsigned)dead_time_ns);
}
```
```cpp
#include "driver/mcpwm_prelude.h"
#include "esp_log.h"
#include <memory>

namespace power_control {

class Esp32HalfBridgePwm {
public:
    struct Pins {
        int high_side_gpio;
        int low_side_gpio;
    };

    Esp32HalfBridgePwm(Pins pins, uint32_t pwm_freq_hz, uint32_t dead_time_ns)
        : pins_(pins), freq_hz_(pwm_freq_hz), dead_time_ns_(dead_time_ns) {}

    ~Esp32HalfBridgePwm() {
        if (timer_) {
            mcpwm_timer_start_stop(timer_, MCPWM_TIMER_STOP_EMPTY);
            mcpwm_timer_disable(timer_);
            mcpwm_del_timer(timer_);
        }
        if (oper_) mcpwm_del_operator(oper_);
    }

    void start() {
        mcpwm_timer_config_t timer_cfg = {
            .group_id = 0,
            .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,
            .resolution_hz = 10'000'000,
            .period_ticks = static_cast<uint32_t>(10'000'000 / (2 * freq_hz_)),
            .count_mode = MCPWM_TIMER_COUNT_MODE_UP_DOWN,
        };
        ESP_ERROR_CHECK(mcpwm_new_timer(&timer_cfg, &timer_));

        mcpwm_operator_config_t oper_cfg = {.group_id = 0};
        ESP_ERROR_CHECK(mcpwm_new_operator(&oper_cfg, &oper_));
        ESP_ERROR_CHECK(mcpwm_operator_connect_timer(oper_, timer_));

        mcpwm_comparator_config_t cmpr_cfg = {.flags = {.update_cmp_on_tez = true}};
        ESP_ERROR_CHECK(mcpwm_new_comparator(oper_, &cmpr_cfg, &cmpr_));

        mcpwm_generator_config_t gh_cfg = {.gen_gpio_num = pins_.high_side_gpio};
        ESP_ERROR_CHECK(mcpwm_new_generator(oper_, &gh_cfg, &gen_high_));

        mcpwm_generator_config_t gl_cfg = {.gen_gpio_num = pins_.low_side_gpio};
        ESP_ERROR_CHECK(mcpwm_new_generator(oper_, &gl_cfg, &gen_low_));

        // Конфігурація подій та мертвого часу
        ESP_ERROR_CHECK(mcpwm_generator_set_action_on_timer_event(
            gen_high_,
            MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, MCPWM_TIMER_EVENT_EMPTY, MCPWM_GEN_ACTION_HIGH)));
        ESP_ERROR_CHECK(mcpwm_generator_set_action_on_compare_event(
            gen_high_,
            MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, cmpr_, MCPWM_GEN_ACTION_LOW)));

        mcpwm_dead_time_config_t dt_cfg = {
            .posedge_path = MCPWM_DEAD_TIME_PATH_ACTIVE,
            .negedge_path = MCPWM_DEAD_TIME_PATH_INVERT,
        };
        ESP_ERROR_CHECK(mcpwm_generator_set_dead_time(gen_high_, gen_high_, &dt_cfg));
        ESP_ERROR_CHECK(mcpwm_generator_set_dead_time(gen_high_, gen_low_, &dt_cfg));

        ESP_ERROR_CHECK(mcpwm_timer_enable(timer_));
        ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer_, MCPWM_TIMER_START_NO_STOP));
    }

private:
    Pins pins_;
    uint32_t freq_hz_;
    uint32_t dead_time_ns_;
    mcpwm_timer_handle_t timer_{nullptr};
    mcpwm_oper_handle_t oper_{nullptr};
    mcpwm_cmpr_handle_t cmpr_{nullptr};
    mcpwm_gen_handle_t gen_high_{nullptr};
    mcpwm_gen_handle_t gen_low_{nullptr};
};

} // namespace power_control
```
:::

---

### 5. Інженерні підводні камені та правила розробки

1. **Захист конфігурації через біти LOCK:** У промислових виробах після ініціалізації таймера STM32 обов'язково встановлюють рівень блокування `BDTR.LOCK = 1` або `2`. Це апаратно забороняє будь-які модифікації полів `DTG`, полярності виходів та конфігурації аварійного входу Break аж до наступного повного апаратного скидання MCU. Навіть якщо «дикий» покажчик у програмі затре таблицю векторів або пам'ять периферії, захист силових транзисторів залишиться непорушним.
2. **Підтяжка бутстрепного конденсатора (Bootstrap Refresh):** При роботі на коефіцієнті заповнення, близькому до 100%, верхній транзистор відкритий майже весь час, і бутстрепний конденсатор драйвера перестає підзаряджатися від шини 12 В. Прошивка повинна обмежувати максимальне заповнення рівнем 95–98%, гарантуючи, що нижній транзистор відкриється щонайменше на 200–500 нс у кожному періоді для відновлення заряду бутстрепу.
3. **Асинхронний апаратний компаратор для входу Break:** Сигнал аварії струму (Overcurrent Fault) не повинен проходити через АЦП або цифрові алгоритми мікроконтролера. Вихід резистивного шунта підключають до внутрішнього швидкодіючого аналогового компаратора (STM32 COMP1/COMP2), вихід якого внутрішньою комутаційною матрицею апаратно з'єднаний із лінією `TIM1_BKIN`. Час повної реакції від перевищення струму до зняття імпульсів з затворів становить менше 20–30 наносекунд.

---

### 6. Алгоритм динамічної програмної компенсації мертвого часу (FOC Dead-Time Compensation)

У системах векторного керування синхронними двигунами (FOC) спотворення напруги від мертвого часу призводять до спотворення форми струму та вібрацій ротора на малих обертах. Програмний модуль компенсації розраховує коригувальні поправки для регістрів порівняння `CCR` у кожному циклі ШІМ на основі виміряних фазних струмів.

Щоб запобігти високочастотному дзвону та брязкоту біля нульового струму, використовується функція плавного насичення з лінійною зоною:

```
ΔCCR(I_ph) = CCR_dead_comp · sat(I_ph / I_threshold)
```

:::tabs
```c
#include <stdint.h>
#include <math.h>

typedef struct {
    uint32_t ccr_compensation_ticks; // Кількість тактів таймера для компенсації (t_dead / T_tick)
    float current_threshold_a;       // Поріг зони лінійного переходу (наприклад, 0.2 А)
} foc_deadtime_comp_t;

/**
 * @brief Розрахунок скомпенсованих значень регістрів порівняння ШІМ
 * @param comp Покажчик на структуру конфігурації
 * @param i_a Струм фази A (Ампери)
 * @param i_b Струм фази B (Ампери)
 * @param i_c Струм фази C (Ампери)
 * @param[in,out] ccr_a Значення CCR фази A
 * @param[in,out] ccr_b Значення CCR фази B
 * @param[in,out] ccr_c Значення CCR фази C
 */
void foc_apply_deadtime_compensation(const foc_deadtime_comp_t *comp,
                                     float i_a, float i_b, float i_c,
                                     uint32_t *ccr_a, uint32_t *ccr_b, uint32_t *ccr_c) {
    float sign_a = i_a / comp->current_threshold_a;
    float sign_b = i_b / comp->current_threshold_a;
    float sign_c = i_c / comp->current_threshold_a;

    // Обмеження діапазону від -1.0 до +1.0 (функція насичення)
    if (sign_a > 1.0f) sign_a = 1.0f; else if (sign_a < -1.0f) sign_a = -1.0f;
    if (sign_b > 1.0f) sign_b = 1.0f; else if (sign_b < -1.0f) sign_b = -1.0f;
    if (sign_c > 1.0f) sign_c = 1.0f; else if (sign_c < -1.0f) sign_c = -1.0f;

    // Внесення поправки у вольт-секундну площу
    int32_t delta_a = (int32_t)(sign_a * (float)comp->ccr_compensation_ticks);
    int32_t delta_b = (int32_t)(sign_b * (float)comp->ccr_compensation_ticks);
    int32_t delta_c = (int32_t)(sign_c * (float)comp->ccr_compensation_ticks);

    *ccr_a = (uint32_t)((int32_t)*ccr_a + delta_a);
    *ccr_b = (uint32_t)((int32_t)*ccr_b + delta_b);
    *ccr_c = (uint32_t)((int32_t)*ccr_c + delta_c);
}
```
```cpp
#include <cstdint>
#include <algorithm>

namespace power_control {

class FocDeadTimeCompensator {
public:
    struct Config {
        uint32_t compensation_ticks{15}; // Тактів корекції
        float current_threshold_a{0.2f}; // Поріг струму для лінійного переходу, А
    };

    explicit FocDeadTimeCompensator(const Config& cfg) noexcept : config_(cfg) {}

    struct PwmDutyOutput {
        uint32_t ccr_a;
        uint32_t ccr_b;
        uint32_t ccr_c;
    };

    PwmDutyOutput compensate(uint32_t raw_ccr_a, uint32_t raw_ccr_b, uint32_t raw_ccr_c,
                            float i_a, float i_b, float i_c) const noexcept {
        const auto calc_delta = [this](float current) noexcept -> int32_t {
            const float norm = std::clamp(current / config_.current_threshold_a, -1.0f, 1.0f);
            return static_cast<int32_t>(norm * static_cast<float>(config_.compensation_ticks));
        };

        return PwmDutyOutput{
            static_cast<uint32_t>(static_cast<int32_t>(raw_ccr_a) + calc_delta(i_a)),
            static_cast<uint32_t>(static_cast<int32_t>(raw_ccr_b) + calc_delta(i_b)),
            static_cast<uint32_t>(static_cast<int32_t>(raw_ccr_c) + calc_delta(i_c))
        };
    }

private:
    Config config_;
};

} // namespace power_control
```
:::

---

### 7. Методика верифікації методом подвійного імпульсу (Double Pulse Test)

Перед запуском силового перетворювача у безперервному режимі ШІМ правильність вибору мертвого часу та динамічні параметри комутації транзисторів перевіряють за допомогою тесту подвійним імпульсом (Double Pulse Test, DPT).

#### Послідовність імпульсів:
1. **Перший імпульс (t1):** Нижній ключ відкривається на час `t1 = (L · I_test) / V_bus`. Струм у тестовому дроселі лінійно зростає від 0 до номінального випробувального значення `I_test`.
2. **Пауза мертвого часу (t_dead):** Нижній ключ вимикається. Струм дроселя перехоплює вбудований body-діод верхнього ключа.
3. **Другий імпульс (t2):** Через задану паузу (200–500 нс) нижній ключ знову відкривається на короткий час `t2` (500 нс). Осцилограф фіксує пік зворотного відновлення діода `I_rr`, сплеск напруги `V_ds` та час наростання струму.

Цей тест дозволяє в безпечному режимі одиничних спрацювань без ризику перегріву переконатися у відсутності наскрізного струму перекриття при реальних робочих напругах і струмах силового каскаду.
