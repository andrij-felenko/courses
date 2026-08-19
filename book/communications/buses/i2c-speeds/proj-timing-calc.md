# ⚙️ Алгоритм розрахунку регістрів синхронізації I2C

Для надійного встановлення зв'язку на шині I2C недостатньо просто задати бажану частоту опитування: мікроконтролер повинен сформувати тактові імпульси `SCL` та затримки лінії даних `SDA`, які суворо вкладаються в часові обмеження стандарту NXP (тривалість низького стану `t_LOW`, тривалість високого стану `t_HIGH`, час встановлення даних `t_SU:DAT` та час утримання `t_HD:DAT`). Апаратні блоки сучасних мікроконтролерів (зокрема архітектур STM32, NXP LPC, ESP32) вимагають прямого програмування подільників частоти, лічильників високого/низького стану та затримок із врахуванням реального часу наростання фронту `t_r` і спадання `t_f`.

Нижче наведено повний інженерний алгоритм автоматичного розрахунку бітових полів конфігураційного регістру таймінгів для трьох основних режимів: Standard-mode (100 кГц), Fast-mode (400 кГц) та Fast-mode Plus (1 МГц), а також докладний розбір фізичного змісту кожного часового параметра.

---

### Фізична модель апаратного блоку синхронізації

Сучасні периферійні модулі I2C не використовують простий симетричний меандр. Оскільки фізичні процеси на шині з відкритим стоком принципово асиметричні (швидкий активний спад проти повільного експоненційного наростання), апаратний блок формує тактовий сигнал за допомогою кількох послідовних цифрових автоматів і лічильників.

Вхідна тактова частота периферійної шини `f_PCLK` (або виділеного тактового генератора `f_I2CCLK`) має період `t_PCLK = 1 / f_PCLK`. Цей сигнал спочатку проходить через попередній подільник `PRESC`, який задає внутрішній часовий квант таймера:

```
t_PRESC = (PRESC + 1) · t_PCLK
```

Далі на основі цього кванта відраховуються чотири критичні часові інтервали:

```
 31      28 27    24 23    20 19    16 15     8 7      0
┌──────────┬────────┬────────┬────────┬────────┬────────┐
│  PRESC   │ Зарез. │ SCLDEL │ SDADEL │  SCLH  │  SCLL  │
└──────────┴────────┴────────┴────────┴────────┴────────┘
```

1. **Лічильник низького стану `SCLL` (SCL Low Period):** Визначає, скільки тактів `t_PRESC` вихідний транзистор мікроконтролера утримує лінію SCL притиснутою до землі:
   ```
   t_LOW = (SCLL + 1) · t_PRESC
   ```
2. **Лічильник високого стану `SCLH` (SCL High Period):** Визначає тривалість фази, протягом якої контролер відпускає лінію SCL і очікує, поки вона перебуває на високому рівні:
   ```
   t_HIGH = (SCLH + 1) · t_PRESC
   ```
3. **Затримка встановлення даних `SCLDEL` (Data Setup Time Delay):** Задає час між виставленням нового біта на лінію SDA та подальшим формуванням висхідного фронту SCL. Цей інтервал гарантує виконання вимоги `t_SU:DAT` для всіх ведених пристроїв.
4. **Затримка утримання даних `SDADEL` (Data Hold Time Delay):** Задає час, протягом якого контролер утримує попередній біт на лінії SDA після того, як лінія SCL опустилася до нуля. Це запобігає випадковому сприйняттю зміни даних як сигналу СТАРТ або СТОП.

Крім того, вхідний каскад кожного виводу містить аналоговий фільтр пригнічення сплесків із затримкою `t_AF` (номінально 50 нс) та програмований цифровий фільтр на `DNF` тактів (`t_DNF = DNF · t_PCLK`). Ці фільтри затримують детектування реального перепаду напруги на шині, тому їхній вплив необхідно компенсувати при розрахунку лічильників.

---

### Нормативні вимоги стандарту NXP I2C

Розрахунок зобов'язаний задовольняти граничні часові нормативи специфікації NXP UM10204:

| Параметр специфікації | Позначення | Standard (100 кГц) | Fast (400 кГц) | Fast-mode+ (1 МГц) |
| :--- | :--- | :--- | :--- | :--- |
| **Максимальна частота SCL** | `f_SCL,max` | 100 кГц | 400 кГц | 1000 кГц |
| **Мінімальний час низького стану** | `t_LOW,min` | 4700 нс | 1300 нс | 500 нс |
| **Мінімальний час високого стану** | `t_HIGH,min` | 4000 нс | 600 нс | 260 нс |
| **Мінімальний час встановлення даних** | `t_SU:DAT,min`| 250 нс | 100 нс | 50 нс |
| **Максимальний час утримання даних** | `t_HD:DAT,max`| 3450 нс | 900 нс | 450 нс |
| **Максимальний час наростання** | `t_r,max` | 1000 нс | 300 нс | 120 нс |
| **Максимальний час спадання** | `t_f,max` | 300 нс | 300 нс | 120 нс |

Повний період тактового сигналу на шині складається з чотирьох послідовних фаз:

```
t_SCL = t_LOW + t_HIGH + t_r + t_f
```

Звідси очевидно: якщо не врахувати фактичний час наростання `t_r` (який витрачається на пасивне заряджання ємності через підтяжку), реальна частота шини виявиться значно нижчою за розрахункову, а тривалість високого стану `t_HIGH` скоротиться нижче безпечної межі.

---

### Реалізація алгоритму на мовах C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    I2C_MODE_STANDARD = 0, /* 100 kHz */
    I2C_MODE_FAST     = 1, /* 400 kHz */
    I2C_MODE_FAST_PLUS= 2  /* 1 MHz   */
} i2c_speed_mode_t;

typedef struct {
    uint32_t pclk_hz;       /* Тактова частота периферії (наприклад, 48000000 для 48 МГц) */
    uint32_t target_scl_hz; /* Бажана швидкість SCL (наприклад, 400000) */
    uint32_t rise_time_ns;  /* Оцінений/виміряний час наростання tr (нс) */
    uint32_t fall_time_ns;  /* Оцінений/виміряний час спадання tf (нс) */
    uint32_t dnf_cycles;    /* Цифровий фільтр шуму (0..15 циклів) */
    bool     analog_filter; /* Увімкнення аналогового фільтра (зазвичай 50 нс) */
} i2c_bus_params_t;

typedef struct {
    uint8_t  presc;     /* Подільник частоти (0..15) */
    uint8_t  scll;      /* Лічильник низького рівня SCL (0..255) */
    uint8_t  sclh;      /* Лічильник високого рівня SCL (0..255) */
    uint8_t  sdadel;    /* Затримка утримання даних (0..15) */
    uint8_t  scldel;    /* Затримка встановлення даних (0..15) */
    uint32_t raw_value; /* Упакований регістр TIMINGR */
    uint32_t actual_hz; /* Фактично отримана частота SCL */
} i2c_timing_reg_t;

typedef struct {
    uint32_t t_low_min_ns;
    uint32_t t_high_min_ns;
    uint32_t t_sudat_min_ns;
    uint32_t t_hddat_max_ns;
    uint32_t tr_max_ns;
    uint32_t tf_max_ns;
} i2c_mode_spec_t;

static const i2c_mode_spec_t SPECS[3] = {
    [I2C_MODE_STANDARD]  = { 4700, 4000, 250, 3450, 1000, 300 },
    [I2C_MODE_FAST]      = { 1300,  600, 100,  900,  300, 300 },
    [I2C_MODE_FAST_PLUS] = {  500,  260,  50,  450,  120, 120 }
};

bool i2c_calculate_timings(const i2c_bus_params_t *params,
                           i2c_speed_mode_t mode,
                           i2c_timing_reg_t *out)
{
    if (!params || !out || params->pclk_hz == 0 || params->target_scl_hz == 0) {
        return false;
    }

    const i2c_mode_spec_t *spec = &SPECS[mode];
    uint32_t t_af_ns = params->analog_filter ? 50 : 0;
    uint32_t tr = params->rise_time_ns > 0 ? params->rise_time_ns : spec->tr_max_ns;
    uint32_t tf = params->fall_time_ns > 0 ? params->fall_time_ns : spec->tf_max_ns;

    /* Обчислення періоду квантування t_I2CCLK у наносекундах */
    double t_pclk_ns = 1000000000.0 / (double)params->pclk_hz;
    uint32_t target_period_ns = 1000000000U / params->target_scl_hz;

    /* Пошук мінімального валідного значення PRESC (0..15) */
    for (uint32_t presc = 0; presc <= 15; ++presc) {
        double t_presc_ns = (double)(presc + 1) * t_pclk_ns;

        /* Сумарна затримка внутрішніх фільтрів */
        double t_filter_ns = (double)t_af_ns + ((double)params->dnf_cycles * t_pclk_ns);

        /* Розрахунок мінімальних значень SCLL та SCLH */
        double scll_min = (spec->t_low_min_ns + tf - t_filter_ns) / t_presc_ns - 1.0;
        double sclh_min = (spec->t_high_min_ns + tr - t_filter_ns) / t_presc_ns - 1.0;

        uint32_t scll_val = scll_min > 0.0 ? (uint32_t)(scll_min + 0.999) : 0;
        uint32_t sclh_val = sclh_min > 0.0 ? (uint32_t)(sclh_min + 0.999) : 0;

        /* Розрахунок сумарного періоду при мінімальних лічильниках */
        double current_period_ns = ((double)(scll_val + 1) + (double)(sclh_val + 1)) * t_presc_ns + tr + tf;

        /* Якщо базовий період менший за цільовий, розподіляємо надлишок порівну */
        if (current_period_ns < (double)target_period_ns) {
            double extra_ns = (double)target_period_ns - current_period_ns;
            uint32_t extra_ticks = (uint32_t)(extra_ns / t_presc_ns);
            scll_val += (extra_ticks + 1) / 2;
            sclh_val += extra_ticks / 2;
        }

        /* Перевірка на переповнення 8-бітних полів */
        if (scll_val > 255 || sclh_val > 255) {
            continue; /* Переходимо до більшого дільника PRESC */
        }

        /* Розрахунок затримок SCLDEL та SDADEL */
        double scldel_min = (spec->t_sudat_min_ns + tr - t_filter_ns) / t_presc_ns - 1.0;
        double sdadel_min = (tf - t_filter_ns) / t_presc_ns - 1.0;

        uint32_t scldel_val = scldel_min > 0.0 ? (uint32_t)(scldel_min + 0.999) : 0;
        uint32_t sdadel_val = sdadel_min > 0.0 ? (uint32_t)(sdadel_min + 0.999) : 0;

        /* Перевірка на переповнення 4-бітних полів */
        if (scldel_val > 15 || sdadel_val > 15) {
            continue;
        }

        /* Знайдено оптимальну комбінацію */
        out->presc   = (uint8_t)presc;
        out->scll    = (uint8_t)scll_val;
        out->sclh    = (uint8_t)sclh_val;
        out->sdadel  = (uint8_t)sdadel_val;
        out->scldel  = (uint8_t)scldel_val;

        /* Пакування в апаратний формат 32-бітного регістру */
        out->raw_value = ((uint32_t)out->presc  << 28) |
                         ((uint32_t)out->scldel << 20) |
                         ((uint32_t)out->sdadel << 16) |
                         ((uint32_t)out->sclh   << 8)  |
                         ((uint32_t)out->scll   << 0);

        double actual_period = ((double)(out->scll + 1) + (double)(out->sclh + 1)) * t_presc_ns + tr + tf;
        out->actual_hz = (uint32_t)(1000000000.0 / actual_period);

        return true;
    }

    return false; /* Не знайдено валідного налаштування для вказаних обмежень */
}
```
```cpp
#include <cstdint>
#include <optional>
#include <array>
#include <string_view>

namespace hal::i2c {

enum class SpeedMode : uint8_t {
    Standard = 0, // 100 kHz
    Fast     = 1, // 400 kHz
    FastPlus = 2  // 1 MHz
};

struct BusParameters {
    uint32_t pclkHz{48'000'000};       // Тактова частота модуля
    uint32_t targetSclHz{400'000};     // Цільова частота
    uint32_t riseTimeNs{200};          // Фактичний час наростання tr
    uint32_t fallTimeNs{40};           // Фактичний час спадання tf
    uint8_t  dnfCycles{0};             // Цифровий фільтр (0..15)
    bool     analogFilter{true};       // Аналоговий фільтр (50 нс)
};

struct TimingRegisters {
    uint8_t  prescaler{0};
    uint8_t  sclLow{0};
    uint8_t  sclHigh{0};
    uint8_t  sdaDelay{0};
    uint8_t  sclDelay{0};
    uint32_t packedRegister{0};
    uint32_t actualFrequencyHz{0};

    [[nodiscard]] constexpr uint32_t raw() const noexcept {
        return packedRegister;
    }
};

struct ModeSpecification {
    uint32_t tLowMinNs;
    uint32_t tHighMinNs;
    uint32_t tSuDatMinNs;
    uint32_t tHdDatMaxNs;
    uint32_t tRiseMaxNs;
    uint32_t tFallMaxNs;
};

inline constexpr std::array<ModeSpecification, 3> Specs{{
    {4700, 4000, 250, 3450, 1000, 300}, // Standard
    {1300,  600, 100,  900,  300, 300}, // Fast
    { 500,  260,  50,  450,  120, 120}  // FastPlus
}};

class TimingCalculator {
public:
    [[nodiscard]] static std::optional<TimingRegisters> compute(
        const BusParameters& params,
        SpeedMode mode) noexcept
    {
        if (params.pclkHz == 0 || params.targetSclHz == 0) {
            return std::nullopt;
        }

        const auto& spec = Specs[static_cast<size_t>(mode)];
        const uint32_t tAfNs = params.analogFilter ? 50 : 0;
        const uint32_t tr = params.riseTimeNs > 0 ? params.riseTimeNs : spec.tRiseMaxNs;
        const uint32_t tf = params.fallTimeNs > 0 ? params.fallTimeNs : spec.tFallMaxNs;

        const double tPclkNs = 1e9 / static_cast<double>(params.pclkHz);
        const uint32_t targetPeriodNs = 1'000'000'000U / params.targetSclHz;

        for (uint32_t presc = 0; presc <= 15; ++presc) {
            const double tPrescNs = static_cast<double>(presc + 1) * tPclkNs;
            const double tFilterNs = static_cast<double>(tAfNs) + 
                                     (static_cast<double>(params.dnfCycles) * tPclkNs);

            const double scllMin = (spec.tLowMinNs + tf - tFilterNs) / tPrescNs - 1.0;
            const double sclhMin = (spec.tHighMinNs + tr - tFilterNs) / tPrescNs - 1.0;

            uint32_t scllVal = scllMin > 0.0 ? static_cast<uint32_t>(scllMin + 0.999) : 0;
            uint32_t sclhVal = sclhMin > 0.0 ? static_cast<uint32_t>(sclhMin + 0.999) : 0;

            const double currentPeriodNs = (static_cast<double>(scllVal + 1) + 
                                            static_cast<double>(sclhVal + 1)) * tPrescNs + tr + tf;

            if (currentPeriodNs < static_cast<double>(targetPeriodNs)) {
                const double extraNs = static_cast<double>(targetPeriodNs) - currentPeriodNs;
                const uint32_t extraTicks = static_cast<uint32_t>(extraNs / tPrescNs);
                scllVal += (extraTicks + 1) / 2;
                sclhVal += extraTicks / 2;
            }

            if (scllVal > 255 || sclhVal > 255) {
                continue;
            }

            const double scldelMin = (spec.tSuDatMinNs + tr - tFilterNs) / tPrescNs - 1.0;
            const double sdadelMin = (tf - tFilterNs) / tPrescNs - 1.0;

            const uint32_t scldelVal = scldelMin > 0.0 ? static_cast<uint32_t>(scldelMin + 0.999) : 0;
            const uint32_t sdadelVal = sdadelMin > 0.0 ? static_cast<uint32_t>(sdadelMin + 0.999) : 0;

            if (scldelVal > 15 || sdadelVal > 15) {
                continue;
            }

            TimingRegisters reg{};
            reg.prescaler = static_cast<uint8_t>(presc);
            reg.sclLow    = static_cast<uint8_t>(scllVal);
            reg.sclHigh   = static_cast<uint8_t>(sclhVal);
            reg.sdaDelay  = static_cast<uint8_t>(sdadelVal);
            reg.sclDelay  = static_cast<uint8_t>(scldelVal);

            reg.packedRegister = (static_cast<uint32_t>(reg.prescaler) << 28) |
                                 (static_cast<uint32_t>(reg.sclDelay)  << 20) |
                                 (static_cast<uint32_t>(reg.sdaDelay)  << 16) |
                                 (static_cast<uint32_t>(reg.sclHigh)   << 8)  |
                                 (static_cast<uint32_t>(reg.sclLow)    << 0);

            const double actualPeriod = (static_cast<double>(reg.sclLow + 1) + 
                                         static_cast<double>(reg.sclHigh + 1)) * tPrescNs + tr + tf;
            reg.actualFrequencyHz = static_cast<uint32_t>(1e9 / actualPeriod);

            return reg;
        }

        return std::nullopt;
    }
};

} // namespace hal::i2c
```
:::

---

### Покроковий числовий розбір двох практичних конфігурацій

#### Приклад 1. Конфігурація Fast-mode (400 кГц при частоті ядра 48 МГц)
- Вхідна тактова частота периферії: `f_PCLK = 48 МГц` (`t_PCLK = 20.833 нс`).
- Цільовий режим: **Fast-mode (400 кГц)**, цільовий період `t_SCL = 2500 нс`.
- Фізичні параметри плати: виміряний час наростання `t_r = 200 нс`, час спадання `t_f = 40 нс`.
- Фільтри: увімкнено аналоговий фільтр `t_AF = 50 нс`, цифровий фільтр вимкнено (`DNF = 0`).

1. **Перевірка дільника `PRESC = 0`:**
   - Квант таймінгу: `t_PRESC = (0 + 1) · 20.833 нс = 20.833 нс`.
   - Сумарна затримка фільтра: `t_filter = 50 нс`.

2. **Обчислення мінімальних лічильників SCLL та SCLH:**
   ```
   scll_min = (1300 нс + 40 нс - 50 нс) / 20.833 нс - 1 = 1290 / 20.833 - 1 = 61.92 - 1 = 60.92
   SCLL = ceil(60.92) = 61

   sclh_min = (600 нс + 200 нс - 50 нс) / 20.833 нс - 1 = 750 / 20.833 - 1 = 36.00 - 1 = 35.00
   SCLH = 35
   ```

3. **Перевірка сумарного періоду та розподіл залишку:**
   Мінімальний період при знайдених лічильниках складе:
   ```
   t_min = (61 + 1) · 20.833 + (35 + 1) · 20.833 + 200 + 40 = 1291.6 + 750.0 + 240 = 2281.6 нс
   ```
   Оскільки цільовий період становить 2500 нс, маємо дефіцит часу:
   ```
   Δt = 2500 - 2281.6 = 218.4 нс
   Кількість додаткових квантів: 218.4 / 20.833 = 10.48 ≈ 10 квантів
   ```
   Додаємо 5 квантів до `SCLL` (`61 + 5 = 66`) та 5 квантів до `SCLH` (`35 + 5 = 40`).
   Фактичні тривалості станів:
   - `t_LOW = (66 + 1) · 20.833 = 1395.8 нс` (перевищує нормативні 1300 нс).
   - `t_HIGH = (40 + 1) · 20.833 = 854.2 нс` (перевищує нормативні 600 нс).
   - Фактичний період: `1395.8 + 854.2 + 200 + 40 = 2490 нс` (частота 401.6 кГц).

4. **Розрахунок затримок ліній даних:**
   ```
   scldel_min = (100 нс + 200 нс - 50 нс) / 20.833 нс - 1 = 250 / 20.833 - 1 = 12.0 - 1 = 11.0
   SCLDEL = 11

   sdadel_min = (40 нс - 50 нс) / 20.833 нс - 1 = -10 / 20.833 - 1 < 0
   SDADEL = 0
   ```

5. **Формування значення конфігураційного регістру:**
   ```
   TIMINGR = (0 << 28) | (11 << 20) | (0 << 16) | (40 << 8) | (66 << 0) = 0x00B02842
   ```

---

#### Приклад 2. Конфігурація Fast-mode Plus (1 МГц при частоті ядра 80 МГц)
- Вхідна частота: `f_PCLK = 80 МГц` (`t_PCLK = 12.5 нс`).
- Цільовий режим: **Fm+ (1 МГц)**, цільовий період `t_SCL = 1000 нс`.
- Параметри плати: `t_r = 80 нс`, `t_f = 25 нс`, аналоговий фільтр `t_AF = 50 нс`.

1. При `PRESC = 0` (`t_PRESC = 12.5 нс`):
   ```
   scll_min = (500 + 25 - 50) / 12.5 - 1 = 475 / 12.5 - 1 = 38 - 1 = 37
   sclh_min = (260 + 80 - 50) / 12.5 - 1 = 290 / 12.5 - 1 = 23.2 - 1 = 22.2 -> SCLL = 37, SCLH = 23
   ```
2. Розрахунок періоду:
   ```
   t_current = (38 + 24) · 12.5 + 80 + 25 = 775 + 105 = 880 нс
   Залишок до 1000 нс: 120 нс -> 120 / 12.5 ≈ 9 квантів (5 до SCLL, 4 до SCLH)
   SCLL = 37 + 5 = 42 (t_LOW = 43 · 12.5 = 537.5 нс > 500 нс)
   SCLH = 23 + 4 = 27 (t_HIGH = 28 · 12.5 = 350.0 нс > 260 нс)
   Фактичний період: 537.5 + 350.0 + 80 + 25 = 992.5 нс (частота 1007.5 кГц)
   ```
3. Затримки:
   ```
   scldel_min = (50 + 80 - 50) / 12.5 - 1 = 80 / 12.5 - 1 = 6.4 - 1 = 5.4 -> SCLDEL = 6
   sdadel_min = (25 - 50) / 12.5 - 1 < 0 -> SDADEL = 0
   ```
4. Упакований регістр:
   ```
   TIMINGR = (0 << 28) | (6 << 20) | (0 << 16) | (27 << 8) | (42 << 0) = 0x00601B2A
   ```

---

### Методика верифікації таймінгів за допомогою осцилографа

Після прошивки розрахованих значень у регістри периферії якість сигналу обов'язково перевіряють на реальній платі двоканальним цифровим осцилографом (зі смугою пропускання не менше 100 МГц) за таким алгоритмом:

1. **Вимірювання часу наростання `t_r`:** Встановлюють горизонтальні курсори на рівні `0.3 · V_DD` та `0.7 · V_DD`. Вертикальними курсорами вимірюють інтервал часу між точками перетину цих рівнів на висхідному фронті сигналу SCL. Отримане значення повинно суворо вкладатися в норму обраного режиму (наприклад, `t_r ≤ 300 нс` для 400 кГц).
2. **Перевірка часу встановлення даних `t_SU:DAT`:** Перший канал осцилографа підключають до SCL, другий — до SDA. Вимірюють часовий зсув від моменту стабілізації біта на лінії SDA до моменту досягнення напруги `0.3 · V_DD` на висхідному фронті SCL. Інтервал повинен перевищувати мінімальний поріг (100 нс для Fast-mode).
3. **Контроль залишкової напруги `V_OL`:** Збільшують вертикальну чутливість осцилографа (наприклад, 100 мВ/поділку) і вимірюють потенціал полички логічного нуля під час передачі бітів веденим пристроєм та ведучим контролером. Потенціал не повинен перевищувати 0.4 В.

---

### Апаратні пастки та крайові випадки

1. **Дрейф тактової частоти внутрішніх RC-генераторів (HSI):** Якщо периферійний модуль I2C тактується від внутрішнього некоригованого RC-генератора мікроконтролера, його частота може дрейфувати на ±1–3% у робочому температурному діапазоні. При граничних налаштуваннях таймінгів це може вивести тривалість `t_HIGH` за межі стандарту. Рекомендується завжди закладати 10-відсотковий запас за тривалістю імпульсів.
2. **Асинхронний розрив зв'язку при розтягуванні такту (Clock Stretching Timeout):** Якщо ведений пристрій зависає під час утримання лінії SCL у нулі, стандартний цифровий автомат контролера блокується в очікуванні висхідного перепаду. Для запобігання вічному блокуванню прошивки необхідно вмикати апаратний модуль тайм-ауту (*SMBus/I2C Timeout Detector*), який автоматично генерує переривання помилки шини при утриманні SCL довше 25–35 мс.
3. **Паразитна зміна затримки аналогових фільтрів:** Реальна затримка вбудованого 50-нс аналогового фільтра може варіюватися від 30 до 90 нс залежно від напруги живлення та температури кристала. Якщо затримка `SCLDEL` розрахована без запасу, ведений пристрій отримає спад SCL раніше, ніж завершиться фільтрація даних на SDA, викликавши хибне зчитування байта.
4. **Затримки арбітражу на шині DMA:** Якщо передача даних I2C обслуговується контролером прямого доступу до пам'яті (DMA), високе навантаження на внутрішню шину мікроконтролера іншими периферійними блоками (наприклад, дисплеєм або Ethernet) може спричинити затримку завантаження наступного байта в регістр передавача. Якщо модуль I2C не підтримує автоматичне апаратне утримання такту на час очікування DMA, виникає помилка спустошення буфера (*underrun*), що призводить до передачі некоректних даних.
