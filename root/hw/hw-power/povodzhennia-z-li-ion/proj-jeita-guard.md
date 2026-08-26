# ⚙️ Програмний модуль контролю температурних зон JEITA та аварійних блокувань

У цьому проєктному модулі реалізовано скінченний автомат для вбудованих систем, який зчитує показники NTC-термістора батареї, класифікує поточний стан за п'ятьма температурними зонами стандарту JEITA з гістерезисом та динамічно обмежує струм і напругу зарядного контролера або повністю вимикає заряд при аварійних станах. Без програмного контролю температурного профілю апаратний зарядник не здатний запобігти осадженню металевого літію на холоді чи тепловому розгону на спеці.

## Архітектура керування безпекою заряду

Більшість апаратних мікросхем контролерів заряду (таких як серії Texas Instruments BQ24xxx/BQ25xxx, Analog Devices LTC4162 або MPS MP26xx) мають вбудований аналоговий компаратор для виводу `TS` (Temperature Sense). Проте апаратні компаратори мають фіксовані або грубо налаштовувані пороги, які часто не відповідають специфікаціям конкретної хімії (NMC, LCO чи LFP) та не підтримують гнучких багатозонних профілів.

Програмний модуль сторожа (Safety Guard) реалізує багаторівневу логіку супервізора, що періодично виконується в головному циклі або за таймером операційної системи реального часу (RTOS) з періодом 100–500 мс:

1. **Аналогова фільтрація та лінеаризація:** Напруга з дільника терморезистора NTC оцифровується АЦП мікроконтролера. Через наявність високих імпульсних завад від силового ШІМ-перетворювача зарядника сирі відліки пропускаються крізь експоненційний ковзний фільтр (EMA) або медіанний фільтр. Опір датчика перераховується в градуси Цельсія за рівнянням Бета або Стейнхарта-Харта.
2. **Оцінка градієнта нагріву (`dT/dt`):** Модуль зберігає кільцевий буфер вимірювань за останні кілька секунд. Якщо швидкість зростання температури перевищує безпечну межу (наприклад, понад 1.5 °C/с за помірного зарядного струму), це свідчить про виникнення внутрішнього локального мікрозамикання в комірці або теплової лавини. Модуль негайно виставляє засувку аварії (Fault Latch) і блокує силовий ключ.
3. **Автомат станів зон JEITA з гістерезисом:** Температура зіставляється з порогами п'яти зон стандарту JEITA (Japan Electronics and Information Technology Industries Association). Для запобігання брязкоту станів і циклічного перемикання струму на межах діапазонів застосовується симетричний гістерезис (за замовчуванням `ΔT_hyst = 2.0 °C`).
4. **Формування та запис уставок у силовий драйвер:** Залежно від поточної зони формується кортеж параметрів `{ChargeEnable, I_limit, V_limit}`, які передаються до регістрів контролера заряду цифровою шиною I2C/SMBus або через ШІМ-виходи.

## Таблиця температурних зон та параметрів обмеження

| Зона JEITA | Діапазон температур | Струм заряду (`I_chg`) | Напруга термінації (`V_term`) | Механізм захисту |
|---|---|---|---|---|
| **Cold** | `T < 0.0 °C` | 0 мА (Заряд вимкнено) | 4200 мВ (або 0 В) | Запобігання осадженню металевого літію (Lithium Plating) |
| **Cool** | `0.0 °C ≤ T < 10.0 °C` | Знижений: `0.2C..0.5C` | 4200 мВ | Компенсація сповільненої дифузії іонів у графіті |
| **Standard** | `10.0 °C ≤ T < 45.0 °C` | Номінальний: `1.0C` | 4200 мВ | Оптимальне вікно безпечної роботи |
| **Warm** | `45.0 °C ≤ T < 60.0 °C` | Знижений: `0.5C` | Знижена: `4100 мВ` | Зниження окиснювального стресу на катоді та електроліті |
| **Hot** | `T ≥ 60.0 °C` | 0 мА (Заряд вимкнено) | 4200 мВ (або 0 В) | Запобігання розпаду SEI-шару та тепловому розгону |

## Фізичний зміст переходів між зонами

Кожна зона стандарту JEITA безпосередньо відповідає певному термодинамічному стану хімічної системи. Перехід між ними вимагає ретельного дотримання напрямку зміни температури:

* **Перехід Cold → Cool (нагрів від мінусових температур):** Коли акумулятор перебуває на морозі (наприклад, -5 °C), підключення зовнішнього джерела живлення не повинно відкривати силове коло. Комірка може споживати лише кілька міліампер на підігрівний нагрівач (якщо він передбачений у конструкції батарейного блоку). Лише коли температура перевищить `0 °C + ΔT_hyst = +2.0 °C`, контролер переходить у зону Cool і подає обмежений струм `0.2C`.
* **Перехід Standard → Warm (розігрів на спеці або під час швидкого заряду):** За температури понад 45 °C хімічний потенціал повністю зарядженого катода (4.20 В) викликає прискорене каталітичне окиснення молекул органічного розчинника з виділенням газів. Зниження кінцевої напруги заряду до 4.10 В зменшує ступінь деінтеркаляції кобальту або нікелю, зміщуючи потенціал у термодинамічно стійкішу область і знижуючи швидкість окиснення в 3–4 рази.
* **Перехід Warm → Hot (аварійне відключення):** При досягненні 60 °C починається деструкція метастабільного SEI-шару. Будь-яке подальше протікання зарядного струму створює додатковий джоулів нагрів `I²·R_int`, що штовхає комірку до критичної точки біфуркації Семенова. Силовий ключ розмикається негайно.

:::tabs
```c
/* jeita_guard.h / jeita_guard.c — Програмний сторож температурного профілю */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    JEITA_ZONE_COLD = 0,    /* T < 0 °C: Заряд суворо заборонено (0 мА) */
    JEITA_ZONE_COOL,        /* 0..10 °C: Знижений струм (0.2C..0.5C), 4.20 В */
    JEITA_ZONE_STANDARD,    /* 10..45 °C: Повний номінальний струм (1.0C), 4.20 В */
    JEITA_ZONE_WARM,        /* 45..60 °C: Помірний струм (0.5C), знижена напруга (4.10 В) */
    JEITA_ZONE_HOT          /* T >= 60 °C: Заряд суворо заборонено (0 мА) */
} jeita_zone_t;

typedef struct {
    float temp_c;           /* Поточна згладжена температура, °C */
    float temp_rate;        /* Швидкість зміни dT/dt, °C/с */
    jeita_zone_t zone;      /* Поточна активна зона */
    uint16_t charge_i_ma;   /* Дозволений струм заряду, мА */
    uint16_t charge_v_mv;   /* Гранична напруга заряду, мВ */
    bool charge_enable;     /* Дозвіл роботи силового каскаду */
    bool fault_latch;       /* Аварійне апаратне блокування */
} jeita_status_t;

typedef struct {
    float t_cold;           /* Поріг холоду: 0.0 °C */
    float t_cool;           /* Поріг прохолоди: 10.0 °C */
    float t_warm;           /* Поріг тепла: 45.0 °C */
    float t_hot;            /* Поріг спеки: 60.0 °C */
    float t_hyst;           /* Гістерезис переходів: 2.0 °C */
    float max_dt_rate;      /* Гранична швидкість нагріву: 1.5 °C/с */
    uint16_t i_standard_ma; /* Номінальний струм CC: наприклад, 2000 мА */
    uint16_t i_reduced_ma;  /* Знижений струм: наприклад, 500 мА */
    uint16_t v_standard_mv; /* Номінальна напруга CV: 4200 мВ */
    uint16_t v_reduced_mv;  /* Знижена напруга CV: 4100 мВ */
} jeita_config_t;

/* Розрахунок температури NTC за формулою бета-коефіцієнта */
float ntc_calc_temperature_c(uint16_t adc_raw, uint16_t adc_max, float r_pullup, float r_ntc_25, float beta) {
    if (adc_raw == 0 || adc_raw >= adc_max) {
        return (adc_raw == 0) ? -50.0f : 120.0f; /* Обрив або коротке датчика */
    }
    float v_ratio = (float)adc_raw / (float)adc_max;
    float r_ntc = r_pullup * (v_ratio / (1.0f - v_ratio));
    
    /* T = 1 / ( (1/T0) + (1/B)*ln(R/R0) ) */
    const float t0_kelvin = 298.15f; /* 25 °C */
    float inv_t = (1.0f / t0_kelvin) + (1.0f / beta) * logf(r_ntc / r_ntc_25);
    return (1.0f / inv_t) - 273.15f;
}

/* Оновлення стану профілю з урахуванням гістерезису та швидкості зростання температури */
void jeita_guard_update(jeita_status_t *stat, const jeita_config_t *cfg, float measured_temp, float dt_sec) {
    if (stat->fault_latch) {
        stat->charge_enable = false;
        stat->charge_i_ma = 0;
        return;
    }

    if (dt_sec > 0.001f) {
        stat->temp_rate = (measured_temp - stat->temp_c) / dt_sec;
    }
    stat->temp_c = measured_temp;

    /* Перевірка на аномальний градієнт саморозігріву */
    if (stat->temp_rate > cfg->max_dt_rate && stat->temp_c > cfg->t_cool) {
        stat->fault_latch = true;
        stat->charge_enable = false;
        stat->charge_i_ma = 0;
        return;
    }

    /* Автомат переходу між зонами з гістерезисом cfg->t_hyst */
    switch (stat->zone) {
        case JEITA_ZONE_COLD:
            if (stat->temp_c >= (cfg->t_cold + cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_COOL;
            }
            break;
        case JEITA_ZONE_COOL:
            if (stat->temp_c < cfg->t_cold) {
                stat->zone = JEITA_ZONE_COLD;
            } else if (stat->temp_c >= (cfg->t_cool + cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_STANDARD;
            }
            break;
        case JEITA_ZONE_STANDARD:
            if (stat->temp_c < (cfg->t_cool - cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_COOL;
            } else if (stat->temp_c >= cfg->t_warm) {
                stat->zone = JEITA_ZONE_WARM;
            }
            break;
        case JEITA_ZONE_WARM:
            if (stat->temp_c < (cfg->t_warm - cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_STANDARD;
            } else if (stat->temp_c >= cfg->t_hot) {
                stat->zone = JEITA_ZONE_HOT;
            }
            break;
        case JEITA_ZONE_HOT:
            if (stat->temp_c < (cfg->t_hot - cfg->t_hyst)) {
                stat->zone = JEITA_ZONE_WARM;
            }
            break;
    }

    /* Призначення апаратних лімітів відповідно до активної зони */
    switch (stat->zone) {
        case JEITA_ZONE_COLD:
        case JEITA_ZONE_HOT:
            stat->charge_enable = false;
            stat->charge_i_ma = 0;
            stat->charge_v_mv = cfg->v_standard_mv;
            break;
        case JEITA_ZONE_COOL:
            stat->charge_enable = true;
            stat->charge_i_ma = cfg->i_reduced_ma;
            stat->charge_v_mv = cfg->v_standard_mv;
            break;
        case JEITA_ZONE_STANDARD:
            stat->charge_enable = true;
            stat->charge_i_ma = cfg->i_standard_ma;
            stat->charge_v_mv = cfg->v_standard_mv;
            break;
        case JEITA_ZONE_WARM:
            stat->charge_enable = true;
            stat->charge_i_ma = cfg->i_reduced_ma;
            stat->charge_v_mv = cfg->v_reduced_mv;
            break;
    }
}
```
```cpp
// JeitaGuard.hpp — Об'єктно-орієнтований сторож безпеки заряду
#pragma once
#include <cstdint>
#include <cmath>
#include <expected>
#include <algorithm>

namespace BatterySafety {

enum class JeitaZone : uint8_t {
    Cold = 0,   // < 0 °C: Заряд заблоковано
    Cool,       // 0..10 °C: Знижений струм
    Standard,   // 10..45 °C: Номінальний режим
    Warm,       // 45..60 °C: Знижена напруга
    Hot         // >= 60 °C: Заряд заблоковано
};

enum class GuardFault : uint8_t {
    SensorFault,
    RapidThermalRise,
    HardwareTrip
};

struct ChargeLimits {
    bool enabled;
    uint16_t current_ma;
    uint16_t voltage_mv;
    JeitaZone zone;
};

struct JeitaConfig {
    float temp_cold_c{0.0f};
    float temp_cool_c{10.0f};
    float temp_warm_c{45.0f};
    float temp_hot_c{60.0f};
    float hyst_c{2.0f};
    float max_temp_rate_c_per_s{1.5f};
    uint16_t standard_current_ma{2000};
    uint16_t reduced_current_ma{500};
    uint16_t standard_voltage_mv{4200};
    uint16_t reduced_voltage_mv{4100};
};

class NtcSensor {
public:
    constexpr NtcSensor(float pullup_r, float nominal_r, float beta) noexcept
        : pullup_ohm_{pullup_r}, nominal_ohm_{nominal_r}, beta_{beta} {}

    [[nodiscard]] std::expected<float, GuardFault> read_temperature(uint16_t raw_adc, uint16_t max_adc) const noexcept {
        if (raw_adc == 0 || raw_adc >= max_adc) {
            return std::unexpected(GuardFault::SensorFault);
        }
        const float ratio = static_cast<float>(raw_adc) / static_cast<float>(max_adc);
        const float r_ntc = pullup_ohm_ * (ratio / (1.0f - ratio));
        constexpr float t0_kelvin = 298.15f;
        const float inv_t = (1.0f / t0_kelvin) + (1.0f / beta_) * std::log(r_ntc / nominal_ohm_);
        return (1.0f / inv_t) - 273.15f;
    }

private:
    float pullup_ohm_;
    float nominal_ohm_;
    float beta_;
};

class JeitaGuard {
public:
    explicit constexpr JeitaGuard(const JeitaConfig& config) noexcept
        : config_{config}, current_zone_{JeitaZone::Cold} {}

    std::expected<ChargeLimits, GuardFault> update(float current_temp_c, float dt_s) noexcept {
        if (fault_latched_) {
            return std::unexpected(GuardFault::HardwareTrip);
        }

        if (dt_s > 0.001f) {
            const float rate = (current_temp_c - last_temp_c_) / dt_s;
            if (rate > config_.max_temp_rate_c_per_s && current_temp_c > config_.temp_cool_c) {
                fault_latched_ = true;
                return std::unexpected(GuardFault::RapidThermalRise);
            }
        }
        last_temp_c_ = current_temp_c;
        evaluate_zone(current_temp_c);

        return calculate_limits();
    }

    void reset_latch() noexcept {
        fault_latched_ = false;
    }

private:
    void evaluate_zone(float temp_c) noexcept {
        switch (current_zone_) {
            case JeitaZone::Cold:
                if (temp_c >= (config_.temp_cold_c + config_.hyst_c))
                    current_zone_ = JeitaZone::Cool;
                break;
            case JeitaZone::Cool:
                if (temp_c < config_.temp_cold_c)
                    current_zone_ = JeitaZone::Cold;
                else if (temp_c >= (config_.temp_cool_c + config_.hyst_c))
                    current_zone_ = JeitaZone::Standard;
                break;
            case JeitaZone::Standard:
                if (temp_c < (config_.temp_cool_c - config_.hyst_c))
                    current_zone_ = JeitaZone::Cool;
                else if (temp_c >= config_.temp_warm_c)
                    current_zone_ = JeitaZone::Warm;
                break;
            case JeitaZone::Warm:
                if (temp_c < (config_.temp_warm_c - config_.hyst_c))
                    current_zone_ = JeitaZone::Standard;
                else if (temp_c >= config_.temp_hot_c)
                    current_zone_ = JeitaZone::Hot;
                break;
            case JeitaZone::Hot:
                if (temp_c < (config_.temp_hot_c - config_.hyst_c))
                    current_zone_ = JeitaZone::Warm;
                break;
        }
    }

    [[nodiscard]] ChargeLimits calculate_limits() const noexcept {
        ChargeLimits limits{};
        limits.zone = current_zone_;
        switch (current_zone_) {
            case JeitaZone::Cold:
            case JeitaZone::Hot:
                limits.enabled = false;
                limits.current_ma = 0;
                limits.voltage_mv = config_.standard_voltage_mv;
                break;
            case JeitaZone::Cool:
                limits.enabled = true;
                limits.current_ma = config_.reduced_current_ma;
                limits.voltage_mv = config_.standard_voltage_mv;
                break;
            case JeitaZone::Standard:
                limits.enabled = true;
                limits.current_ma = config_.standard_current_ma;
                limits.voltage_mv = config_.standard_voltage_mv;
                break;
            case JeitaZone::Warm:
                limits.enabled = true;
                limits.current_ma = config_.reduced_current_ma;
                limits.voltage_mv = config_.reduced_voltage_mv;
                break;
        }
        return limits;
    }

    JeitaConfig config_;
    JeitaZone current_zone_;
    float last_temp_c_{25.0f};
    bool fault_latched_{false};
};

} // namespace BatterySafety
```
:::

## Інженерні пастки та лабораторна валідація

1. **Розміщення датчика NTC:** Терморезистор має бути притиснутий теплопровідним компаундом або еластичною силіконовою подушкою безпосередньо до середини гільзи або пакету комірки, а не припаяний на плату контролера біля силових транзисторів. Якщо NTC вимірює нагрів гарячого MOSFET-ключа інвертора, а не хімічного тіла батареї, алгоритм безпідставно відключить заряд холодної комірки або пропустить її локальний екзотермічний перегрів.
2. **Точність аналогового опорного джерела (VREF):** Живлення дільника NTC та опорна напруга АЦП мікроконтролера мають братися від однієї рейки живлення (раціометрична схема). При раціометричній схемі коливання напруги живлення однаково масштабують напругу на NTC і опорний рівень АЦП, зводячи абсолютну похибку вимірювання опору до нуля незалежно від просідання живлення мікроконтролера.
3. **Обробка несправностей датчика:** Якщо провід NTC обірвався (АЦП видає 0 або максимальне значення), алгоритм не має трактувати це як «безпечний нуль градусів». Обрив або коротке замикання лінії датчика повинно миттєво генерувати аварійний код `GuardFault::SensorFault` і вимикати силове коло заряду.
4. **Методика стендової перевірки:** Перед передачею прошивки у виробництво сторож перевіряють за допомогою магазину опорів (Decade Resistor Box), що підключається замість NTC. Послідовно змінюючи опір, інженер фіксує осцилографом реакцію лінії керування зарядом: час переходу між зонами має відповідати гістерезису, а реакція на аварійний нагрів або обрив має переривати силове коло за час менше 50 мілісекунд.
