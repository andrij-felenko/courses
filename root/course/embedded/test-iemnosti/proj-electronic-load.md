# ⚙️ Програмно-апаратний контролер електронного навантаження

Ця вставка містить детальну інженерну архітектуру та повну реалізацію прошивки лабораторного мікроконтролерного стенду тестування ємності батарей. Прошивка підтримує чотири режими навантаження (CC, CR, CP та Pulsed), реалізує 4-провідний захист від перерозряду, аварійне термовідключення радіатора силового транзистора, розрахунок кулонів (мА·год), енергії (мВт·год), а також періодичне вимірювання динамічного внутрішнього опору (DC IR) за методом струмової сходинки.

## Апаратна частина та розрахунок стабільності контуру

Створення аналогового керованого навантаження вимагає вирішення кількох нетривіальних проблем силової електроніки, з якими стикається розробник під час переводу польового транзистора в лінійний режим.

```
       +V_batt (Force +)
          |
          +----+----------------------------+
          |    |                            |
         [ ]  --- C_batt (опціонально)     [ ] R_div1 (Sense +)
         DUT  ---                          [ ]
          |    |                            |
          |    +----------------------------+---> ADC1 (V_batt diff)
          |                                 |
          |   +---------+                  [ ] R_div2 (Sense −)
          |   |  Радіатор                  [ ]
          |   +---------+                   |
          |        |                        +---> GND_sense
          +--------|-----------+
                   |           | (Drain)
               +---|-----------|-+
               |   |   |---|   | |
    DAC --->[+]|   |---|MOS|   | | (N-FET IRLZ44N)
            OpAmp      |---|   | |
    +------>[-]          |     | |
    |          |       (Source)| |
    |          +-------+-------+-+
    |                  |
    |                 [ ] R_shunt (0.05 Ом, 1%, 4-провідний)
    |                  |
    +------------------+------------------------> ADC2 (I_actual)
                       |
                      GND_power (Force −)
```

### 1. Лінійний режим MOSFET та зона безпечної роботи (SOA)

Більшість сучасних силових транзисторів N-MOSFET оптимізовані для ключового режиму (мінімальний опір `R_ds(on)` у відкритому стані). У лінійному режимі навантаження транзистор працює в активній області: на ньому одночасно падає значна напруга `V_ds = 2.5 – 4.2 В` і протікає струм `I_d = 0.5 – 3 А`.

Розсіювана потужність сягає:

```
P_fet = V_ds · I_d = 4.0 В · 2.5 А = 10 Вт
```

У лінійній області проявляється ефект Спіріто (*Spirito effect*): за низьких напруг на затворі температурний коефіцієнт порогової напруги є від'ємним. Локальне нагрівання кристала призводить до зниження порогової напруги в цій точці, струм концентрується у вузькому каналі, що викликає локальний тепловий пробій (*thermal runaway*) навіть за потужностей, значно менших за паспортний максимум транзистора. Тому для стенду обирають транзистори в корпусах TO-220 або TO-247 з великою площею кристала та обов'язковим масивним алюмінієвим радіатором з активним охолодженням.

### 2. Стійкість контуру зворотного зв'язку за струмом

Операційний підсилювач керує затвором MOSFET, підтримуючи падіння напруги на шунті `V_shunt` рівним опорній напрузі `V_dac`.

Велика вхідна ємність затвора транзистора `C_iss ≈ 1500 – 3000 пФ` разом із вихідним опором ОП `R_out_op` утворює паразитний низькочастотний полюс:

```
f_p = 1 / (2 · π · R_out_op · C_iss) ≈ 10 – 50 кГц
```

Цей полюс зменшує запас стійкості за фазою до нуля, спричиняючи автоколивання контуру на частотах 50–200 кГц. Для забезпечення безумовної стійкості контуру застосовують два обов'язкові компоненти:
1. **Затворний демпфер `R_g = 47 – 100 Ом`**: ізолює вихід ОП від ємності затвора;
2. **Конденсатор місцевого зворотного зв'язку `C_comp = 10 – 47 нФ`**: увімкнений між виходом ОП та його інвертуючим входом `(−)`. Він перетворює ОП на інтегратор на високих частотах, забезпечуючи спад підсилення −20 дБ/декада та запас за фазою > 60°.

### 3. Струмовимірювальний шунт та трасування друкованої плати

Для мінімізації самонагрівання та температурного дрейфу використовують прецизійний 4-вивідний резистор Кельвіна номіналом `R_shunt = 0.05 Ом` з температурним коефіцієнтом опору TCO < 50 ppm/°C і потужністю 3–5 Вт.

Трасування плати розрядного стенду вимагає суворого дотримання правил розділення силових і сигнальних кіл:
* Силова земля `GND_power` (по якій протікають струми до 3 А) з'єднується з сигнальною землею `GND_analog` в одній-єдиній точці — безпосередньо біля виводу силового джерела живлення («зірка»);
* Лінії `Sense +` та `Sense −` трасуються паралельною диференціальною парою з мінімальним зазором і захищаються суцільним екранним полігоном землі зверху і знизу;
* Термістор NTC монтується термопастою безпосередньо на металеву підкладку силового транзистора біля кристала.

## Двоточкова калібровка вимірювального тракту

Похибки номіналів резисторів дільника напруги та струмового шунта призводять до систематичної похибки вимірювання. Для їх компенсації у флеш-пам'ять мікроконтролера записують коефіцієнти лінійної калібровки (коефіцієнт підсилення `Gain` та зміщення нуля `Offset`):

```
V_calibrated = (V_raw · Gain_v) / 1000 + Offset_v
I_calibrated = (I_raw · Gain_i) / 1000 + Offset_i
```

Процедура калібрування виконується за зразковим лабораторним мультиметром у двох точках: для каналу напруги — при 2.500 В та 4.200 В; для каналу струму — при 100 мА та 2000 мА.

## Архітектура керуючого автомата

Керування стендом реалізовано у вигляді детермінованого скінченного автомата (*Finite State Machine*), який виконується з фіксованим періодом квантування `T_sample = 10 мс` (100 Гц):

```
       +------------------+
       |   STATE_IDLE     | <-------------------------+
       +------------------+                           |
                 |                                    |
            [cmd_start]                               |
                 v                                    |
       +------------------+   [V_cell < V_cutoff]     |
       |  STATE_DISCHARGE | ------------------------> |
       +------------------+                           |
                 |                                    |
          [t_ir_trigger]                              |
                 v                                    |
       +------------------+                           |
       |   STATE_PULSE_IR | --------------------------+
       +------------------+    [T_heatsink > T_max]
                               [або аварійний brown-out]
```

1. **STATE_IDLE**: силове навантаження вимкнено (`DAC = 0`), очікування команди запуску через UART або кнопки.
2. **STATE_DISCHARGE**: основний цикл розряду. Залежно від режиму (CC, CR, CP) обчислюється необхідний вихідний струм, встановлюється значення ЦАП, проводиться чисельне інтегрування струму та енергії за правилом трапецій.
3. **STATE_PULSE_IR**: короткочасний сплеск струму (або сходинка зняття навантаження) тривалістю 100 мс для фіксації перепаду напруги `ΔV` та розрахунку `DC IR = ΔV / ΔI`.

## Реалізація прошивки

:::tabs
```c
/* load_controller.h - C implementation */
#ifndef LOAD_CONTROLLER_H
#define LOAD_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    MODE_CC = 0,    /* Постійний струм (мА) */
    MODE_CR,        /* Постійний опір (мОм) */
    MODE_CP,        /* Постійна потужність (мВт) */
    MODE_PULSED     /* Імпульсний профіль (радіотракт) */
} load_mode_t;

typedef enum {
    STATE_IDLE = 0,
    STATE_RUNNING,
    STATE_IR_STEP,
    STATE_CUTOFF_REACHED,
    STATE_OVERHEAT_FAULT
} load_state_t;

typedef struct {
    load_mode_t mode;
    uint32_t setpoint_val;     /* мА для CC, мОм для CR, мВт для CP */
    uint32_t pulse_high_ma;    /* Струм імпульсу для Pulsed (мА) */
    uint32_t pulse_low_ma;     /* Струм бази для Pulsed (мА) */
    uint32_t pulse_high_ms;    /* Тривалість імпульсу (мс) */
    uint32_t pulse_period_ms;  /* Період повторення (мс) */
    uint32_t cutoff_mv;        /* Кінцева напруга відсічки (мВ) */
    uint32_t max_temp_c;       /* Максимальна температура радіатора (°C) */
} load_config_t;

typedef struct {
    load_state_t state;
    load_config_t cfg;
    uint32_t v_cell_mv;        /* Поточна напруга комірки (мВ) */
    uint32_t i_actual_ma;      /* Фактичний струм (мА) */
    uint32_t temp_heatsink_c;  /* Температура радіатора (°C) */
    
    /* Інтегратори */
    uint64_t microamp_seconds; /* Кулонометрія (мкА·с) */
    uint64_t microwatt_seconds;/* Лічильник енергії (мкВт·с) */
    
    /* Розрахунок DC IR */
    uint32_t ir_v_baseline_mv;
    uint32_t ir_i_baseline_ma;
    uint32_t last_dc_ir_mohm;
    uint32_t ir_timer_ms;
    
    uint32_t elapsed_ms;
} load_tester_t;

/* HAL-колбеки для зв'язку з апаратним рівнем */
typedef struct {
    void (*set_dac_current_ma)(uint32_t ma);
    void (*read_adc_channels)(uint32_t *v_cell_mv, uint32_t *i_shunt_ma, uint32_t *temp_c);
    void (*send_uart_log)(const char *str);
} load_hal_t;

void load_tester_init(load_tester_t *t, const load_config_t *cfg, const load_hal_t *hal);
void load_tester_start(load_tester_t *t);
void load_tester_stop(load_tester_t *t);
void load_tester_tick(load_tester_t *t, uint32_t dt_ms);

#endif /* LOAD_CONTROLLER_H */
```
```c
/* load_controller.c */
#include "load_controller.h"
#include <stdio.h>

static const load_hal_t *s_hal = NULL;

void load_tester_init(load_tester_t *t, const load_config_t *cfg, const load_hal_t *hal) {
    if (!t || !cfg || !hal) return;
    s_hal = hal;
    t->cfg = *cfg;
    t->state = STATE_IDLE;
    t->v_cell_mv = 0;
    t->i_actual_ma = 0;
    t->temp_heatsink_c = 0;
    t->microamp_seconds = 0;
    t->microwatt_seconds = 0;
    t->last_dc_ir_mohm = 0;
    t->ir_timer_ms = 0;
    t->elapsed_ms = 0;
    
    if (s_hal->set_dac_current_ma) {
        s_hal->set_dac_current_ma(0);
    }
}

void load_tester_start(load_tester_t *t) {
    if (!t) return;
    t->state = STATE_RUNNING;
    t->microamp_seconds = 0;
    t->microwatt_seconds = 0;
    t->elapsed_ms = 0;
    t->ir_timer_ms = 0;
}

void load_tester_stop(load_tester_t *t) {
    if (!t) return;
    t->state = STATE_IDLE;
    if (s_hal && s_hal->set_dac_current_ma) {
        s_hal->set_dac_current_ma(0);
    }
}

static uint32_t compute_target_current_ma(load_tester_t *t) {
    switch (t->cfg.mode) {
        case MODE_CC:
            return t->cfg.setpoint_val;
            
        case MODE_CR:
            /* I = V / R; V в мВ, R в мОм -> I = (V * 1000) / R */
            if (t->cfg.setpoint_val == 0) return 0;
            return (t->v_cell_mv * 1000UL) / t->cfg.setpoint_val;
            
        case MODE_CP:
            /* I = P / V; P в мВт, V в мВ -> I = (P * 1000) / V */
            if (t->v_cell_mv < 500) return 0; /* Захист від ділення на нуль */
            return (t->cfg.setpoint_val * 1000UL) / t->v_cell_mv;
            
        case MODE_PULSED: {
            uint32_t phase = t->elapsed_ms % t->cfg.pulse_period_ms;
            if (phase < t->cfg.pulse_high_ms) {
                return t->cfg.pulse_high_ma;
            } else {
                return t->cfg.pulse_low_ma;
            }
        }
        default:
            return 0;
    }
}

void load_tester_tick(load_tester_t *t, uint32_t dt_ms) {
    if (!t || !s_hal) return;

    /* 1. Зчитування фізичних сигналів АЦП (4-провідні виміри) */
    s_hal->read_adc_channels(&t->v_cell_mv, &t->i_actual_ma, &t->temp_heatsink_c);
    
    if (t->state != STATE_RUNNING && t->state != STATE_IR_STEP) {
        s_hal->set_dac_current_ma(0);
        return;
    }

    /* 2. Захисти: Термічний та Відсічка за напругою */
    if (t->temp_heatsink_c >= t->cfg.max_temp_c) {
        s_hal->set_dac_current_ma(0);
        t->state = STATE_OVERHEAT_FAULT;
        return;
    }

    if (t->v_cell_mv <= t->cfg.cutoff_mv && t->v_cell_mv > 200) {
        s_hal->set_dac_current_ma(0);
        t->state = STATE_CUTOFF_REACHED;
        return;
    }

    /* 3. Періодичний вимір DC IR (кожні 30 секунд: імпульсний стрибок 100 мс) */
    t->ir_timer_ms += dt_ms;
    if (t->state == STATE_RUNNING && t->ir_timer_ms >= 30000) {
        t->state = STATE_IR_STEP;
        t->ir_v_baseline_mv = t->v_cell_mv;
        t->ir_i_baseline_ma = t->i_actual_ma;
        
        /* Ступінчасте збільшення струму на +200 мА */
        s_hal->set_dac_current_ma(t->i_actual_ma + 200);
        return;
    }

    if (t->state == STATE_IR_STEP) {
        if (t->ir_timer_ms >= 30100) { /* Минуло 100 мс після сходинки */
            int32_t delta_v = (int32_t)t->ir_v_baseline_mv - (int32_t)t->v_cell_mv;
            int32_t delta_i = (int32_t)t->i_actual_ma - (int32_t)t->ir_i_baseline_ma;
            
            if (delta_i > 50 && delta_v > 0) {
                /* R_dc = (ΔV_mV * 1000) / ΔI_mA -> в мОм */
                t->last_dc_ir_mohm = (uint32_t)((delta_v * 1000L) / delta_i);
            }
            t->ir_timer_ms = 0;
            t->state = STATE_RUNNING;
        } else {
            return; /* Утримуємо імпульс 100 мс */
        }
    }

    /* 4. Керування струмом навантаження */
    uint32_t target_i_ma = compute_target_current_ma(t);
    s_hal->set_dac_current_ma(target_i_ma);

    /* 5. Чисельне інтегрування енергії та ємності */
    t->microamp_seconds += (uint64_t)t->i_actual_ma * 1000ULL * dt_ms / 1000ULL;
    uint32_t power_mw = (uint32_t)(((uint64_t)t->v_cell_mv * t->i_actual_ma) / 1000ULL);
    t->microwatt_seconds += (uint64_t)power_mw * 1000ULL * dt_ms / 1000ULL;

    t->elapsed_ms += dt_ms;

    /* 6. Логування в CSV форматі раз на секунду */
    if (t->elapsed_ms % 1000 < dt_ms) {
        char buf[128];
        uint32_t mah = (uint32_t)(t->microamp_seconds / 3600000ULL);
        uint32_t mwh = (uint32_t)(t->microwatt_seconds / 3600000ULL);
        snprintf(buf, sizeof(buf), "%lu,%lu,%lu,%lu,%lu,%lu\r\n",
                 (unsigned long)t->elapsed_ms / 1000,
                 (unsigned long)t->v_cell_mv,
                 (unsigned long)t->i_actual_ma,
                 (unsigned long)mah,
                 (unsigned long)mwh,
                 (unsigned long)t->last_dc_ir_mohm);
        if (s_hal->send_uart_log) {
            s_hal->send_uart_log(buf);
        }
    }
}
```
```cpp
/* LoadTester.hpp - Idiomatic C++20 implementation */
#pragma once

#include <cstdint>
#include <chrono>
#include <string_view>
#include <concepts>
#include <array>

namespace EmbeddedPower {

using namespace std::chrono_literals;

enum class LoadMode : uint8_t {
    ConstantCurrent,
    ConstantResistance,
    ConstantPower,
    PulsedRadio
};

enum class TesterState : uint8_t {
    Idle,
    Discharging,
    MeasuringIrStep,
    CutoffReached,
    ThermalFault
};

struct TestProfile {
    LoadMode mode{LoadMode::ConstantCurrent};
    uint32_t setpointValue{500};     // mA, mOhm, or mW
    uint32_t pulseHighMa{200};
    uint32_t pulseLowMa{1};
    std::chrono::milliseconds pulseHighDuration{30ms};
    std::chrono::milliseconds pulsePeriod{1000ms};
    uint32_t cutoffMv{3000};
    uint32_t maxHeatsinkTempC{75};
};

struct MeasurementSample {
    uint32_t cellVoltageMv{0};
    uint32_t loadCurrentMa{0};
    uint32_t heatsinkTempC{0};
};

template <typename HardwareDriver>
class ElectronicLoadController {
public:
    explicit constexpr ElectronicLoadController(HardwareDriver& driver, TestProfile profile) noexcept
        : driver_{driver}, profile_{profile} {}

    void start() noexcept {
        state_ = TesterState::Discharging;
        microampSeconds_ = 0;
        microwattSeconds_ = 0;
        elapsedTime_ = 0ms;
        irTimer_ = 0ms;
    }

    void stop() noexcept {
        state_ = TesterState::Idle;
        driver_.setOutputCurrent(0);
    }

    void update(std::chrono::milliseconds dt) noexcept {
        const auto sample = driver_.readSensors();
        currentSample_ = sample;

        if (state_ != TesterState::Discharging && state_ != TesterState::MeasuringIrStep) {
            driver_.setOutputCurrent(0);
            return;
        }

        // Safety supervision
        if (sample.heatsinkTempC >= profile_.maxHeatsinkTempC) {
            driver_.setOutputCurrent(0);
            state_ = TesterState::ThermalFault;
            return;
        }

        if (sample.cellVoltageMv <= profile_.cutoffMv && sample.cellVoltageMv > 200) {
            driver_.setOutputCurrent(0);
            state_ = TesterState::CutoffReached;
            return;
        }

        // Periodic Dynamic DC IR sampling (every 30 seconds)
        irTimer_ += dt;
        if (state_ == TesterState::Discharging && irTimer_ >= 30s) {
            state_ = TesterState::MeasuringIrStep;
            irBaselineVoltageMv_ = sample.cellVoltageMv;
            irBaselineCurrentMa_ = sample.loadCurrentMa;
            driver_.setOutputCurrent(sample.loadCurrentMa + 200);
            return;
        }

        if (state_ == TesterState::MeasuringIrStep) {
            if (irTimer_ >= 30s + 100ms) {
                const auto deltaV = static_cast<int32_t>(irBaselineVoltageMv_) - static_cast<int32_t>(sample.cellVoltageMv);
                const auto deltaI = static_cast<int32_t>(sample.loadCurrentMa) - static_cast<int32_t>(irBaselineCurrentMa_);
                if (deltaI > 50 && deltaV > 0) {
                    lastDcIrMohm_ = static_cast<uint32_t>((deltaV * 1000) / deltaI);
                }
                irTimer_ = 0ms;
                state_ = TesterState::Discharging;
            } else {
                return; // Hold pulse
            }
        }

        // Calculate target current
        const uint32_t targetMa = calculateSetpointCurrent(sample.cellVoltageMv);
        driver_.setOutputCurrent(targetMa);

        // Numerical integration
        microampSeconds_ += static_cast<uint64_t>(sample.loadCurrentMa) * 1000ULL * dt.count() / 1000ULL;
        const uint32_t powerMw = (sample.cellVoltageMv * sample.loadCurrentMa) / 1000UL;
        microwattSeconds_ += static_cast<uint64_t>(powerMw) * 1000ULL * dt.count() / 1000ULL;

        elapsedTime_ += dt;
    }

    [[nodiscard]] constexpr TesterState state() const noexcept { return state_; }
    [[nodiscard]] constexpr uint32_t capacityMah() const noexcept { return static_cast<uint32_t>(microampSeconds_ / 3600000ULL); }
    [[nodiscard]] constexpr uint32_t energyMwh() const noexcept { return static_cast<uint32_t>(microwattSeconds_ / 3600000ULL); }
    [[nodiscard]] constexpr uint32_t dynamicEsrMohm() const noexcept { return lastDcIrMohm_; }

private:
    [[nodiscard]] uint32_t calculateSetpointCurrent(uint32_t vCellMv) const noexcept {
        switch (profile_.mode) {
            case LoadMode::ConstantCurrent:
                return profile_.setpointValue;
            case LoadMode::ConstantResistance:
                return (profile_.setpointValue > 0) ? (vCellMv * 1000UL) / profile_.setpointValue : 0;
            case LoadMode::ConstantPower:
                return (vCellMv >= 500) ? (profile_.setpointValue * 1000UL) / vCellMv : 0;
            case LoadMode::PulsedRadio: {
                const auto phase = elapsedTime_ % profile_.pulsePeriod;
                return (phase < profile_.pulseHighDuration) ? profile_.pulseHighMa : profile_.pulseLowMa;
            }
        }
        return 0;
    }

    HardwareDriver& driver_;
    TestProfile profile_;
    TesterState state_{TesterState::Idle};
    MeasurementSample currentSample_{};

    uint64_t microampSeconds_{0};
    uint64_t microwattSeconds_{0};
    std::chrono::milliseconds elapsedTime_{0ms};
    std::chrono::milliseconds irTimer_{0ms};

    uint32_t irBaselineVoltageMv_{0};
    uint32_t irBaselineCurrentMa_{0};
    uint32_t lastDcIrMohm_{0};
};

} // namespace EmbeddedPower
```
:::

## Практичні рекомендації щодо калібрування стенду

1. **Калібрування нульового зміщення ОП (Offset Voltage):** Навіть прецизійні операційні підсилювачі мають зміщення входу `V_os ≈ 0.5 – 2 мВ`. При шунті `0.05 Ом` зміщення `1 мВ` еквівалентне паразитному струму розряду `20 мА`. Необхідно калібрувати зміщення програмно під час увімкнення стенду без підключеного акумулятора;
2. **Фільтрація АЦП:** Для усунення високочастотного шуму комутації силового MOSFET рекомендується застосовувати цифровий IIR-фільтр експоненційного згладжування першого порядку `y[k] = α · x[k] + (1 - α) · y[k-1]` з коефіцієнтом `α = 0.1 – 0.2`;
3. **Розрахунок температури NTC за формулою Стейнхарта-Харта:** Для аварійного захисту радіатора опір термістора `R_ntc` перераховують у температуру за спрощеним рівнянням B-параметра:

```
1 / T = 1 / T_0 + (1 / B) · ln(R_ntc / R_0)
```

де `T_0 = 298.15 К` (25°C), `R_0 = 10 кОм`, `B = 3950 К`. Якщо температура радіатора перевищує +75°C, прошивка негайно обнуляє вихід ЦАП і зупиняє розряд, запобігаючи руйнуванню силового каскаду.
