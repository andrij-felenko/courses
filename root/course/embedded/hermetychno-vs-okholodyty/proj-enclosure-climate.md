# ⚙️ Моніторинг мікроклімату герметичного корпусу

Ця вставка містить повноцінний вбудований програмний модуль для безперервного контролю мікроклімату всередині герметичного корпусу IP67/IP68: зчитування сенсорів температури, вологості (SHT40 / BME280) та барометричного тиску (DPS310 / BMP388), обчислення точки роси за формулою Магнуса-Тетенса, розрахунок похідної тиску `dP/dt` для виявлення розгерметизації або забиття дихальної мембрани, а також ступінчастий автомат теплового тротлінгу.

## 1. Фізичні принципи та архітектура вимірювань

Контроль стану замкненого об'єму герметичного приладу вимагає одночасного моніторингу трьох термодинамічних параметрів: абсолютної температури повітря, відносної вологості та абсолютного тиску. На відміну від відкритих систем, де локальний перегрів розсіюється конвективним потоком, у закритому боксі будь-яка зміна потужності призводить до швидкої зміни рівноважного тиску та фазового стану води.

Для реалізації телеметрії використовуються дві групи спеціалізованих напівпровідникових давачів:
1. **Ємнісний датчик відносної вологості й температури (Sensirion SHT40 / Bosch BME280):**
   Чутливий елемент вологості містить мікроскопічний полімерний діелектрик, розміщений між перфорованими металевими електродами. Молекули водяної пари дифундують у полімер, змінюючи його діелектричну проникність, що фіксується інтегральним прецизійним перетворювачем ємності в цифровий код. Вбудований датчик температури вимірює напругу P-N переходу кремнію з високою лінійністю (±0.1 °C).
2. **П'єзорезистивний датчик абсолютного тиску (Infineon DPS310 / Bosch BMP388):**
   Чутливий елемент є пружною монокристалічною кремнієвою мембраною з інтегрованими тензорезисторами, увімкненими за схемою моста Вітстона. Зворотний бік мембрани вакуумований. Прогин мембрани під дією атмосферного тиску генерує диференціальну напругу, яка оцифровується 24-бітним сигма-дельта АЦП із роздільною здатністю до 0.06 Па (еквівалент зміни висоти на 5 см).

### Алгоритмічні задачі модуля

Програмний драйвер виконує чотири діагностичні функції:
1. **Контроль точки роси (Dew Point Margin):**
   Обчислення температури конденсації вологи `T_dew` та порівняння її з мінімальною температурою стінки корпусу. Якщо запас `ΔT_margin = T_стінка − T_dew < 3.0 °C`, активується внутрішній нагрівач або знижується потужність обчислень.
2. **Детекція порушення герметичності (Gasket Breach):**
   Різкий стрибок похідної тиску `dP/dt` під час занурення або зливи сигналізує про прорив ущільнювача.
3. **Детекція блокування дихальної мембрани (Membrane Clogging):**
   Поступове зростання надлишкового внутрішнього тиску `ΔP > 5.0 кПа` під час прогріву свідчить про обмерзання або забруднення пор ePTFE.
4. **Адаптивний тепловий тротлінг (Thermal Throttling):**
   Багаторівневе обмеження тактової частоти SoC за перегріву внутрішнього середовища понад +75 °C.

### Формула точки роси (Магнус-Тетенс)

Для діапазону температур від −40 °C до +80 °C наближення Магнуса забезпечує похибку менше 0.2 °C:

```
γ(T, RH) = (a · T) / (b + T) + ln(RH / 100.0)
T_dew    = (b · γ(T, RH)) / (a − γ(T, RH))
```

де константи для повітря становлять: `a = 17.27`, `b = 237.7 °C`.

---

## 2. Реалізація модуля (C та C++)

:::tabs
```c
// climate_monitor.h / climate_monitor.c
// Модуль контролю мікроклімату герметичного корпусу (Embedded C99 / C11)

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define CLIMATE_HISTORY_SIZE       8
#define DEW_MARGIN_CRITICAL_C      3.0f
#define PRESSURE_LEAK_RATE_KPA_S   0.25f
#define MEMBRANE_CLOG_DP_KPA       5.0f

typedef enum {
    CLIMATE_STATUS_OK = 0,
    CLIMATE_WARN_CONDENSATION_RISK = (1 << 0),
    CLIMATE_WARN_MEMBRANE_CLOGGED  = (1 << 1),
    CLIMATE_ALERT_SEAL_BREACH      = (1 << 2),
    CLIMATE_ALERT_OVERHEAT         = (1 << 3)
} climate_status_flags_t;

typedef enum {
    THROTTLE_LEVEL_NONE = 0,
    THROTTLE_LEVEL_LIGHT,      // -25% тактової частоти
    THROTTLE_LEVEL_HEAVY,      // -50% тактової частоти, вимкнення радіомодулів
    THROTTLE_LEVEL_CRITICAL    // Екстрений перехід у сон (Sleep mode)
} thermal_throttle_level_t;

typedef struct {
    float temp_c;              // Температура внутрішнього повітря (°C)
    float humidity_rh;         // Відносна вологість (0.0 - 100.0 %)
    float pressure_kpa;        // Внутрішній абсолютний тиск (кПа)
    float wall_temp_c;         // Температура внутрішньої стінки корпусу (°C)
    float ext_pressure_kpa;    // Зовнішній барометричний тиск (кПа)
} climate_raw_sensors_t;

typedef struct {
    float dew_point_c;
    float dew_margin_c;
    float pressure_delta_kpa;
    float dp_dt_kpa_s;
    climate_status_flags_t flags;
    thermal_throttle_level_t throttle;
} climate_processed_state_t;

typedef struct {
    float pressure_history[CLIMATE_HISTORY_SIZE];
    uint32_t timestamp_history_ms[CLIMATE_HISTORY_SIZE];
    uint8_t history_idx;
    uint8_t history_count;
    climate_processed_state_t current_state;
} climate_monitor_ctx_t;

// Ініціалізація контексту
void climate_monitor_init(climate_monitor_ctx_t *ctx) {
    if (!ctx) return;
    ctx->history_idx = 0;
    ctx->history_count = 0;
    ctx->current_state.dew_point_c = 0.0f;
    ctx->current_state.dew_margin_c = 100.0f;
    ctx->current_state.pressure_delta_kpa = 0.0f;
    ctx->current_state.dp_dt_kpa_s = 0.0f;
    ctx->current_state.flags = CLIMATE_STATUS_OK;
    ctx->current_state.throttle = THROTTLE_LEVEL_NONE;
}

// Обчислення точки роси за формулою Магнуса
static float compute_dew_point(float t_c, float rh) {
    if (rh <= 0.01f) rh = 0.01f;
    if (rh > 100.0f) rh = 100.0f;
    const float a = 17.27f;
    const float b = 237.7f;
    float gamma = (a * t_c) / (b + t_c) + logf(rh / 100.0f);
    return (b * gamma) / (a - gamma);
}

// Періодична функція аналізу мікроклімату (викликається, наприклад, щосекунди)
void climate_monitor_update(climate_monitor_ctx_t *ctx,
                            const climate_raw_sensors_t *raw,
                            uint32_t now_ms) {
    if (!ctx || !raw) return;

    // 1. Розрахунок точки роси та запасу до конденсації
    float dew_point = compute_dew_point(raw->temp_c, raw->humidity_rh);
    float dew_margin = raw->wall_temp_c - dew_point;

    // 2. Розрахунок різниці внутрішнього та зовнішнього тиску
    float delta_p = raw->pressure_kpa - raw->ext_pressure_kpa;

    // 3. Обчислення швидкості зміни внутрішнього тиску dP/dt
    float dp_dt = 0.0f;
    if (ctx->history_count > 0) {
        uint8_t oldest_idx = (ctx->history_count < CLIMATE_HISTORY_SIZE) ? 0 : ctx->history_idx;
        float dt_sec = (float)(now_ms - ctx->timestamp_history_ms[oldest_idx]) / 1000.0f;
        if (dt_sec > 0.05f) {
            float dp = raw->pressure_kpa - ctx->pressure_history[oldest_idx];
            dp_dt = dp / dt_sec;
        }
    }

    // Оновлення кільцевого буфера тиску
    ctx->pressure_history[ctx->history_idx] = raw->pressure_kpa;
    ctx->timestamp_history_ms[ctx->history_idx] = now_ms;
    ctx->history_idx = (ctx->history_idx + 1) % CLIMATE_HISTORY_SIZE;
    if (ctx->history_count < CLIMATE_HISTORY_SIZE) ctx->history_count++;

    // 4. Формування прапорців стану
    climate_status_flags_t flags = CLIMATE_STATUS_OK;

    if (dew_margin < DEW_MARGIN_CRITICAL_C) {
        flags |= CLIMATE_WARN_CONDENSATION_RISK;
    }
    if (fabsf(delta_p) > MEMBRANE_CLOG_DP_KPA) {
        flags |= CLIMATE_WARN_MEMBRANE_CLOGGED;
    }
    if (fabsf(dp_dt) > PRESSURE_LEAK_RATE_KPA_S) {
        flags |= CLIMATE_ALERT_SEAL_BREACH;
    }
    if (raw->temp_c > 85.0f || raw->wall_temp_c > 75.0f) {
        flags |= CLIMATE_ALERT_OVERHEAT;
    }

    // 5. Автомат теплового тротлінгу
    thermal_throttle_level_t throttle = THROTTLE_LEVEL_NONE;
    if (raw->temp_c > 95.0f || raw->wall_temp_c > 85.0f) {
        throttle = THROTTLE_LEVEL_CRITICAL;
    } else if (raw->temp_c > 85.0f || raw->wall_temp_c > 75.0f) {
        throttle = THROTTLE_LEVEL_HEAVY;
    } else if (raw->temp_c > 75.0f || raw->wall_temp_c > 65.0f) {
        throttle = THROTTLE_LEVEL_LIGHT;
    }

    // Запис вихідного стану
    ctx->current_state.dew_point_c = dew_point;
    ctx->current_state.dew_margin_c = dew_margin;
    ctx->current_state.pressure_delta_kpa = delta_p;
    ctx->current_state.dp_dt_kpa_s = dp_dt;
    ctx->current_state.flags = flags;
    ctx->current_state.throttle = throttle;
}
```
```cpp
// climate_monitor.hpp
// Модуль контролю мікроклімату герметичного корпусу (C++20)

#pragma once

#include <cmath>
#include <cstdint>
#include <array>
#include <optional>
#include <span>

namespace embedded::enclosure {

enum class ClimateWarning : uint8_t {
    None              = 0,
    CondensationRisk  = 1 << 0,
    MembraneClogged   = 1 << 1,
    SealBreach        = 1 << 2,
    Overheat          = 1 << 3
};

constexpr ClimateWarning operator|(ClimateWarning lhs, ClimateWarning rhs) noexcept {
    return static_cast<ClimateWarning>(static_cast<uint8_t>(lhs) | static_cast<uint8_t>(rhs));
}

constexpr bool has_flag(ClimateWarning val, ClimateWarning flag) noexcept {
    return (static_cast<uint8_t>(val) & static_cast<uint8_t>(flag)) != 0;
}

enum class ThrottleLevel : uint8_t {
    None = 0,
    Light,      // -25% тактової частоти
    Heavy,      // -50% частоти, вимкнення радіо
    Critical    // Перехід у режим глибокого сну
};

struct SensorReadings {
    float internal_temp_c{25.0f};
    float relative_humidity{50.0f};
    float internal_pressure_kpa{101.325f};
    float wall_temp_c{25.0f};
    float ambient_pressure_kpa{101.325f};
};

struct EnclosureState {
    float dew_point_c{0.0f};
    float dew_margin_c{100.0f};
    float pressure_delta_kpa{0.0f};
    float dp_dt_kpa_s{0.0f};
    ClimateWarning warnings{ClimateWarning::None};
    ThrottleLevel throttle{ThrottleLevel::None};
};

template <size_t HistorySize = 8>
class ClimateMonitor {
public:
    static constexpr float DewMarginThresholdC = 3.0f;
    static constexpr float LeakRateThresholdKPaS = 0.25f;
    static constexpr float MembraneClogThresholdKPa = 5.0f;

    constexpr ClimateMonitor() noexcept = default;

    EnclosureState update(const SensorReadings& raw, uint32_t now_ms) noexcept {
        const float dew_point = compute_dew_point(raw.internal_temp_c, raw.relative_humidity);
        const float dew_margin = raw.wall_temp_c - dew_point;
        const float delta_p = raw.internal_pressure_kpa - raw.ambient_pressure_kpa;

        float dp_dt = 0.0f;
        if (history_count_ > 0) {
            const size_t oldest_idx = (history_count_ < HistorySize) ? 0 : history_idx_;
            const float dt_sec = static_cast<float>(now_ms - timestamp_history_[oldest_idx]) / 1000.0f;
            if (dt_sec > 0.05f) {
                const float dp = raw.internal_pressure_kpa - pressure_history_[oldest_idx];
                dp_dt = dp / dt_sec;
            }
        }

        pressure_history_[history_idx_] = raw.internal_pressure_kpa;
        timestamp_history_[history_idx_] = now_ms;
        history_idx_ = (history_idx_ + 1) % HistorySize;
        if (history_count_ < HistorySize) {
            ++history_count_;
        }

        ClimateWarning warnings = ClimateWarning::None;
        if (dew_margin < DewMarginThresholdC) {
            warnings = warnings | ClimateWarning::CondensationRisk;
        }
        if (std::abs(delta_p) > MembraneClogThresholdKPa) {
            warnings = warnings | ClimateWarning::MembraneClogged;
        }
        if (std::abs(dp_dt) > LeakRateThresholdKPaS) {
            warnings = warnings | ClimateWarning::SealBreach;
        }
        if (raw.internal_temp_c > 85.0f || raw.wall_temp_c > 75.0f) {
            warnings = warnings | ClimateWarning::Overheat;
        }

        ThrottleLevel throttle = ThrottleLevel::None;
        if (raw.internal_temp_c > 95.0f || raw.wall_temp_c > 85.0f) {
            throttle = ThrottleLevel::Critical;
        } else if (raw.internal_temp_c > 85.0f || raw.wall_temp_c > 75.0f) {
            throttle = ThrottleLevel::Heavy;
        } else if (raw.internal_temp_c > 75.0f || raw.wall_temp_c > 65.0f) {
            throttle = ThrottleLevel::Light;
        }

        current_state_ = EnclosureState{
            .dew_point_c = dew_point,
            .dew_margin_c = dew_margin,
            .pressure_delta_kpa = delta_p,
            .dp_dt_kpa_s = dp_dt,
            .warnings = warnings,
            .throttle = throttle
        };

        return current_state_;
    }

    [[nodiscard]] const EnclosureState& state() const noexcept {
        return current_state_;
    }

private:
    static float compute_dew_point(float temp_c, float rh) noexcept {
        const float clamped_rh = std::clamp(rh, 0.01f, 100.0f);
        constexpr float a = 17.27f;
        constexpr float b = 237.7f;
        const float gamma = (a * temp_c) / (b + temp_c) + std::log(clamped_rh / 100.0f);
        return (b * gamma) / (a - gamma);
    }

    std::array<float, HistorySize> pressure_history_{};
    std::array<uint32_t, HistorySize> timestamp_history_{};
    size_t history_idx_{0};
    size_t history_count_{0};
    EnclosureState current_state_{};
};

} // namespace embedded::enclosure
```
:::

---

## 3. Практичні пастки впровадження та крайові випадки

Під час розгортання модуля в реальних вбудованих пристроях виникають специфічні апаратні та системні пастки, які необхідно враховувати на етапі написання прошивки:

1. **Власний самонагрів сенсорів (Sensor Self-Heating):**
   При безперервному опитуванні давача вологості та тиску по шині I2C із високою частотою (наприклад, понад 10 Гц) струм, що протікає крізь внутрішній аналоговий тракт чипа (1–2 мА), розігріває кристал на 1...3 °C вище навколишнього повітря. Це призводить до систематичної помилки вимірювання: підвищення локальної температури чутливого елемента штучно занижує виміряну відносну вологість на 5...15% RH, спотворюючи розрахунок точки роси. Рекомендована частота зчитування кліматичних параметрів у стаціонарному режимі становить 0.2...1.0 Гц.
2. **Гістерезис насичення полімерного шару:**
   Якщо прилад тривалий час перебував у середовищі з відносною вологістю понад 90–95%, молекули води глибоко проникають у полімерну матрицю чутливого шару. Після зниження вологості сенсор вимагає від 2 до 6 годин для повної десорбції молекул води (ефект повзучості / creep). Для примусового скидання використовується вбудований імпульсний мікронагрівач сенсора (наприклад, команда запуску нагрівача `Heater Run` у SHT40 потужністю 200 мВт протягом 100 мс), що випаровує зв'язану вологу без деградації калібрування.
3. **Хибні тривоги про витік під час зміни барометричної висоти:**
   Коли пристрій транспортується в автомобілі через гірський перевал або перебуває на борту дрона під час швидкого набору висоти (вертикальна швидкість 5–15 м/с), зовнішній атмосферний тиск падає зі швидкістю до 0.1...0.3 кПа/с. Якщо прошивка аналізуватиме лише абсолютний внутрішній тиск, це викличе помилкове спрацьовування тривоги `CLIMATE_ALERT_SEAL_BREACH`. Для запобігання хибним спрацьовуванням диференціальний тиск обов'язково розраховується як різниця між внутрішнім барометром і зовнішнім датчиком атмосферного тиску.
4. **Аварійне зависання шини I2C у вологому середовищі:**
   При підвищеній конденсаційній небезпеці лінії тактування `SCL` та даних `SDA` можуть зазнавати струмів витоку через мікроплівки вологи. Якщо підлеглий сенсор зависає, утримуючи лінію `SDA` в низькому стані, хост-контролер перед кожним циклом зчитування повинен перевіряти стан шини й у разі блокування генерувати послідовність із 9 тактових імпульсів `SCL` із наступним формуванням стану `STOP` для апаратного скидання кінцевого автомата сенсора.
