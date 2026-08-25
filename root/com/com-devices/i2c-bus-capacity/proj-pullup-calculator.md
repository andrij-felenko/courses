# ⚙️ Програмний розрахунок ємності шини та вибір резисторів підтяжки

Цей інженерний інструмент автоматизує розрахунок сумарної паразитної ємності шини I²C за топологічними параметрами друкованої плати й кабельних трас, визначає допустиме вікно опорів підтяжки `[R_p,min, R_p,max]` відповідно до специфікації NXP UM10204, підбирає оптимальний номінал зі стандартного ряду E24 та розраховує статичну потужність розсіювання й час наростання фронту `t_r`.

### Постановка задачі та фізична модель розрахунку

При проєктуванні апаратних інтерфейсів I²C інженер стикається з класичним компромісом теорії кіл: завищений опір підтяжки призводить до затягування фронтів і зриву зв'язку на високих швидкостях, а занижений — до перевищення допустимого струму вихідних каскадів мікросхем і зміщення логічного нуля вище порога `V_IL`.

Фізична модель калькулятора враховує чотири незалежні джерела паразитної ємності, що підключаються паралельно між сигнальною лінією (SDA чи SCL) та землею:

1. **Ємність виводів мікросхем (`C_pin`):**
   За стандартом NXP UM10204 кожен вивід додає від `5` до `10 пФ` (за замовчуванням береться консервативна оцінка `10.0 пФ` на кожен чіп, включаючи мікроконтролер-ведучий і всі ведені пристрої).
2. **Ємність друкованих провідників плати (`C_trace`):**
   Для мікрополоскових ліній на стандартному склотекстоліті FR-4 (діелектрична проникність `ε_r ≈ 4.3`, висота діелектрика `h = 0.2 мм`, ширина траси `w = 0.2 мм`) питома погонна ємність становить `1.2–1.5 пФ/см`. У калькуляторі використовується типове значення `1.3 пФ/см`.
3. **Ємність з'єднувальних кабелів і шлейфів (`C_cable`):**
   Для стрічкових плоских шлейфів або гнучких кабелів зв'язку береться значення `75 пФ/м` (при кроці провідників 1.27 мм) або до `100 пФ/м` для екранованих пар.
4. **Ємність контактних рознімів (`C_conn`):**
   Кожен рознім (штирьові з'єднувачі, JST, Molex) додає приблизно `2.0 пФ`.

Алгоритм розрахунку виконує такі послідовні кроки:
1. Обчислення загальної ємності шини:
   ```
   C_b = (N_chips · C_pin) + (L_pcb · C_trace_unit) + (L_cable · C_cable_unit) + (N_conn · C_conn_unit)
   ```
2. Порівняння розрахованої ємності з нормативною межею стандарту (`400 пФ` для Standard та Fast режимів, `550 пФ` для Fast-mode Plus).
3. Розрахунок мінімального опору підтяжки з обмеження струму стоку `I_OL`:
   ```
   R_p,min = (V_DD - V_OL,max) / I_OL,max
   ```
4. Розрахунок максимального опору підтяжки з обмеження часу наростання `t_r,max`:
   ```
   R_p,max = t_r,max / (0.847298 · C_b)
   ```
5. Перевірка умови працездатності вікна: `R_p,min ≤ R_p,max`. Якщо `R_p,min > R_p,max`, видається помилка з рекомендацією розділити шину буфером або перейти на активні прискорювачі.
6. Підбір номіналу зі стандартного ряду E24 з урахуванням технологічного допуску резисторів (±5%).
7. Розрахунок очікуваного часу наростання `t_r` та статичної потужності розсіювання при низькому стані лінії `P_static = (V_DD - V_OL)² / R_p`.

---

### Програмна реалізація калькулятора

Нижче наведено програмні модулі розрахунку мовами C (C99/C11) та сучасним C++20. Обидва варіанти є повністю автономними, не використовують динамічного виділення пам'яті й можуть виконуватися безпосередньо у вбудованих середовищах.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Швидкісні режими за NXP UM10204 */
typedef enum {
    I2C_MODE_STANDARD,   /* 100 кГц, tr_max = 1000 нс, Cb_max = 400 пФ, Iol = 3 мА */
    I2C_MODE_FAST,       /* 400 кГц, tr_max = 300 нс,  Cb_max = 400 пФ, Iol = 3 мА */
    I2C_MODE_FAST_PLUS   /* 1 МГц,   tr_max = 120 нс,  Cb_max = 550 пФ, Iol = 20 мА */
} i2c_bus_mode_t;

/* Вхідні параметри конфігурації шини */
typedef struct {
    double vdd_volts;            /* Напруга живлення (наприклад, 3.3 В) */
    i2c_bus_mode_t mode;         /* Швидкісний режим */
    int chip_count;              /* Кількість мікросхем на шині (MCU + ведені) */
    double pcb_trace_length_cm;  /* Загальна довжина доріжки PCB (см) */
    double cable_length_m;       /* Довжина зовнішнього кабелю (м) */
    int connector_count;         /* Кількість рознімних з'єднань */
} i2c_bus_config_t;

/* Результати інженерного розрахунку */
typedef struct {
    double total_capacitance_pf; /* Сумарна розрахована ємність Cb (пФ) */
    double rp_min_ohms;          /* Нижня межа опору підтяжки (Ом) */
    double rp_max_ohms;          /* Верхня межа опору підтяжки (Ом) */
    double rp_recommended_ohms;  /* Рекомендований номінал з ряду E24 (Ом) */
    double actual_rise_time_ns;  /* Розрахунковий час наростання tr (нс) */
    double static_power_mw;      /* Статична розсіювана потужність на лінію (мВт) */
    bool is_valid_window;        /* Чи існує фізично припустиме вікно Rp */
    bool exceeds_standard_cb;    /* Чи перевищено норматив Cb для даного режиму */
} i2c_calc_result_t;

/* Стандартний ряд E24 (базові мантиси) */
static const double E24_SERIES[] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};
static const int E24_COUNT = sizeof(E24_SERIES) / sizeof(E24_SERIES[0]);

/* Підбір найближчого стандартного номіналу E24 у межах діапазону */
static double find_e24_resistor(double r_min, double r_max) {
    /* Цільове значення — зсунуте до нижньої третини вікна для запасу по tr */
    double target = r_min * 1.25;
    if (target > r_max) {
        target = (r_min + r_max) / 2.0;
    }

    double best_val = -1.0;
    double min_diff = 1e9;

    for (int dec = 1; dec <= 5; ++dec) {
        double mult = pow(10.0, dec);
        for (int i = 0; i < E24_COUNT; ++i) {
            double candidate = E24_SERIES[i] * mult;
            /* З урахуванням допуску ±5% */
            double worst_low = candidate * 0.95;
            double worst_high = candidate * 1.05;

            if (worst_low >= r_min && worst_high <= r_max) {
                double diff = fabs(candidate - target);
                if (diff < min_diff) {
                    min_diff = diff;
                    best_val = candidate;
                }
            }
        }
    }

    return best_val;
}

/* Головна функція розрахунку параметрів шини I2C */
bool i2c_calculate_pullup(const i2c_bus_config_t *cfg, i2c_calc_result_t *res) {
    if (!cfg || !res) return false;

    /* Типові питомі ємності компонентів */
    const double C_PIN_PER_CHIP_PF = 10.0;    /* 10 пФ на вивід за UM10204 */
    const double C_PCB_PER_CM_PF = 1.3;       /* 1.3 пФ/см для стандартного FR-4 */
    const double C_CABLE_PER_M_PF = 75.0;     /* 75 пФ/м для стрічкового шлейфу */
    const double C_CONNECTOR_PF = 2.0;        /* 2 пФ на рознім */

    /* 1. Сумарна ємність шини */
    res->total_capacitance_pf = (cfg->chip_count * C_PIN_PER_CHIP_PF) +
                                (cfg->pcb_trace_length_cm * C_PCB_PER_CM_PF) +
                                (cfg->cable_length_m * C_CABLE_PER_M_PF) +
                                (cfg->connector_count * C_CONNECTOR_PF);

    /* 2. Параметри швидкісного режиму */
    double tr_max_ns = 1000.0;
    double cb_limit_pf = 400.0;
    double iol_max_amps = 0.003;
    double vol_max_volts = 0.4;

    switch (cfg->mode) {
        case I2C_MODE_STANDARD:
            tr_max_ns = 1000.0;
            cb_limit_pf = 400.0;
            iol_max_amps = 0.003;
            break;
        case I2C_MODE_FAST:
            tr_max_ns = 300.0;
            cb_limit_pf = 400.0;
            iol_max_amps = 0.003;
            break;
        case I2C_MODE_FAST_PLUS:
            tr_max_ns = 120.0;
            cb_limit_pf = 550.0;
            iol_max_amps = 0.020;
            break;
    }

    if (cfg->vdd_volts <= 2.0) {
        vol_max_volts = 0.2 * cfg->vdd_volts;
    }

    res->exceeds_standard_cb = (res->total_capacitance_pf > cb_limit_pf);

    /* 3. Розрахунок меж Rp */
    res->rp_min_ohms = (cfg->vdd_volts - vol_max_volts) / iol_max_amps;

    const double LN_7_3 = 0.84729786;
    double cb_farads = res->total_capacitance_pf * 1e-12;
    double tr_max_sec = tr_max_ns * 1e-9;
    res->rp_max_ohms = tr_max_sec / (LN_7_3 * cb_farads);

    /* 4. Перевірка валідності вікна */
    if (res->rp_min_ohms <= res->rp_max_ohms) {
        res->is_valid_window = true;
        res->rp_recommended_ohms = find_e24_resistor(res->rp_min_ohms, res->rp_max_ohms);

        if (res->rp_recommended_ohms > 0.0) {
            res->actual_rise_time_ns = LN_7_3 * res->rp_recommended_ohms * cb_farads * 1e9;
            res->static_power_mw = (pow(cfg->vdd_volts - vol_max_volts, 2.0) / res->rp_recommended_ohms) * 1000.0;
        } else {
            /* Не знайшли резистор із запасом ±5%, беремо середнє арифметичне */
            res->rp_recommended_ohms = (res->rp_min_ohms + res->rp_max_ohms) / 2.0;
            res->actual_rise_time_ns = LN_7_3 * res->rp_recommended_ohms * cb_farads * 1e9;
            res->static_power_mw = (pow(cfg->vdd_volts - vol_max_volts, 2.0) / res->rp_recommended_ohms) * 1000.0;
        }
    } else {
        res->is_valid_window = false;
        res->rp_recommended_ohms = 0.0;
        res->actual_rise_time_ns = 0.0;
        res->static_power_mw = 0.0;
    }

    return true;
}

int main(void) {
    i2c_bus_config_t bus_cfg = {
        .vdd_volts = 3.3,
        .mode = I2C_MODE_FAST,          /* Fast-mode 400 кГц */
        .chip_count = 5,                /* 1 MCU + 4 сенсори */
        .pcb_trace_length_cm = 20.0,    /* 20 см траси */
        .cable_length_m = 0.8,          /* 80 см кабелю до модуля */
        .connector_count = 2
    };

    i2c_calc_result_t result;
    if (i2c_calculate_pullup(&bus_cfg, &result)) {
        printf("=== Результати розрахунку шини I2C ===\n");
        printf("Сумарна ємність Cb:      %.1f пФ\n", result.total_capacitance_pf);
        printf("Перевищення ліміту Cb:   %s\n", result.exceeds_standard_cb ? "ТАК (НЕБЕЗПЕЧНО)" : "НІ");
        printf("Діапазон підтяжки:       [%.0f Ом ... %.0f Ом]\n", result.rp_min_ohms, result.rp_max_ohms);

        if (result.is_valid_window) {
            printf("Рекомендований номінал:  %.0f Ом (E24)\n", result.rp_recommended_ohms);
            printf("Очікуваний час tr:       %.1f нс (ліміт: 300 нс)\n", result.actual_rise_time_ns);
            printf("Статична потужність:     %.2f мВт на лінію\n", result.static_power_mw);
        } else {
            printf("ПОМИЛКА: Вікно значень Rp замкнене! Потрібен буфер або зниження ємності.\n");
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <array>
#include <optional>
#include <expected>
#include <string_view>

namespace i2c {

enum class BusMode {
    Standard,   // 100 kHz, tr_max = 1000 ns, Cb_max = 400 pF, Iol = 3 mA
    Fast,       // 400 kHz, tr_max = 300 ns,  Cb_max = 400 pF, Iol = 3 mA
    FastPlus    // 1 MHz,   tr_max = 120 ns,  Cb_max = 550 pF, Iol = 20 mA
};

struct BusConfig {
    double vdd_volts{3.3};
    BusMode mode{BusMode::Fast};
    int chip_count{5};
    double pcb_trace_length_cm{20.0};
    double cable_length_m{0.8};
    int connector_count{2};
};

struct CalculationResult {
    double total_capacitance_pf{0.0};
    double rp_min_ohms{0.0};
    double rp_max_ohms{0.0};
    double rp_recommended_ohms{0.0};
    double actual_rise_time_ns{0.0};
    double static_power_mw{0.0};
    bool exceeds_standard_cb{false};
};

enum class CalculationError {
    InvalidVoltage,
    ClosedDesignWindow,
    ExcessiveCapacitance
};

class PullupCalculator {
public:
    static constexpr double C_PIN_PER_CHIP_PF = 10.0;
    static constexpr double C_PCB_PER_CM_PF   = 1.3;
    static constexpr double C_CABLE_PER_M_PF  = 75.0;
    static constexpr double C_CONNECTOR_PF    = 2.0;
    static constexpr double LN_7_3            = 0.847297860387;

    static constexpr std::array<double, 24> E24_SERIES = {
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
    };

    static std::expected<CalculationResult, CalculationError> calculate(const BusConfig& cfg) noexcept {
        if (cfg.vdd_volts <= 0.0) {
            return std::unexpected(CalculationError::InvalidVoltage);
        }

        CalculationResult res;
        res.total_capacitance_pf = (cfg.chip_count * C_PIN_PER_CHIP_PF) +
                                   (cfg.pcb_trace_length_cm * C_PCB_PER_CM_PF) +
                                   (cfg.cable_length_m * C_CABLE_PER_M_PF) +
                                   (cfg.connector_count * C_CONNECTOR_PF);

        double tr_max_ns = 1000.0;
        double cb_limit_pf = 400.0;
        double iol_max_amps = 0.003;
        double vol_max_volts = (cfg.vdd_volts <= 2.0) ? (0.2 * cfg.vdd_volts) : 0.4;

        switch (cfg.mode) {
            case BusMode::Standard:
                tr_max_ns = 1000.0;
                cb_limit_pf = 400.0;
                iol_max_amps = 0.003;
                break;
            case BusMode::Fast:
                tr_max_ns = 300.0;
                cb_limit_pf = 400.0;
                iol_max_amps = 0.003;
                break;
            case BusMode::FastPlus:
                tr_max_ns = 120.0;
                cb_limit_pf = 550.0;
                iol_max_amps = 0.020;
                break;
        }

        res.exceeds_standard_cb = (res.total_capacitance_pf > cb_limit_pf);
        res.rp_min_ohms = (cfg.vdd_volts - vol_max_volts) / iol_max_amps;

        const double cb_farads = res.total_capacitance_pf * 1e-12;
        const double tr_max_sec = tr_max_ns * 1e-9;
        res.rp_max_ohms = tr_max_sec / (LN_7_3 * cb_farads);

        if (res.rp_min_ohms > res.rp_max_ohms) {
            return std::unexpected(CalculationError::ClosedDesignWindow);
        }

        auto e24_opt = select_e24_value(res.rp_min_ohms, res.rp_max_ohms);
        res.rp_recommended_ohms = e24_opt.value_or((res.rp_min_ohms + res.rp_max_ohms) / 2.0);

        res.actual_rise_time_ns = LN_7_3 * res.rp_recommended_ohms * cb_farads * 1e9;
        const double delta_v = cfg.vdd_volts - vol_max_volts;
        res.static_power_mw = (delta_v * delta_v / res.rp_recommended_ohms) * 1000.0;

        return res;
    }

private:
    static constexpr std::optional<double> select_e24_value(double r_min, double r_max) noexcept {
        const double target = r_min * 1.25;
        double best_val = -1.0;
        double min_diff = 1e9;

        for (int dec = 1; dec <= 5; ++dec) {
            double mult = 1.0;
            for (int d = 0; d < dec; ++d) mult *= 10.0;

            for (double mantissa : E24_SERIES) {
                const double candidate = mantissa * mult;
                const double worst_low = candidate * 0.95;
                const double worst_high = candidate * 1.05;

                if (worst_low >= r_min && worst_high <= r_max) {
                    const double diff = std::abs(candidate - target);
                    if (diff < min_diff) {
                        min_diff = diff;
                        best_val = candidate;
                    }
                }
            }
        }

        if (best_val > 0.0) {
            return best_val;
        }
        return std::nullopt;
    }
};

} // namespace i2c

int main() {
    i2c::BusConfig config{
        .vdd_volts = 3.3,
        .mode = i2c::BusMode::Fast,
        .chip_count = 5,
        .pcb_trace_length_cm = 20.0,
        .cable_length_m = 0.8,
        .connector_count = 2
    };

    auto calc_res = i2c::PullupCalculator::calculate(config);

    if (calc_res) {
        const auto& r = *calc_res;
        std::cout << "=== Результати розрахунку шини I2C (C++20) ===\n";
        std::cout << std::fixed << std::setprecision(1);
        std::cout << "Сумарна ємність Cb:      " << r.total_capacitance_pf << " пФ\n";
        std::cout << "Перевищення ліміту Cb:   " << (r.exceeds_standard_cb ? "ТАК (НЕБЕЗПЕЧНО)" : "НІ") << "\n";
        std::cout << "Діапазон підтяжки:       [" << std::setprecision(0) << r.rp_min_ohms
                  << " Ом ... " << r.rp_max_ohms << " Ом]\n";
        std::cout << "Рекомендований номінал:  " << r.rp_recommended_ohms << " Ом (E24)\n";
        std::cout << std::setprecision(1);
        std::cout << "Очікуваний час tr:       " << r.actual_rise_time_ns << " нс (ліміт: 300 нс)\n";
        std::cout << std::setprecision(2);
        std::cout << "Статична потужність:     " << r.static_power_mw << " мВт на лінію\n";
    } else {
        std::cerr << "Помилка розрахунку: вікно допустимих значень замкнене!\n";
    }

    return 0;
}
```
:::

---

### Аналіз реальних інженерних сценаріїв

Розгляньмо роботу алгоритму на трьох практичних інженерних конфігураціях:

#### Сценарій 1: Компактна плата польотного контролера (Fast-mode 400 кГц)

Параметри системи:
- Напруга живлення: `V_DD = 3.3 В`;
- Швидкісний режим: Fast-mode (`f = 400 кГц`, `t_r,max = 300 нс`);
- Кількість чіпів на платі: 3 (мікроконтролер STM32, гіроскоп/акселерометр ICM-42688P, магнітометр LIS3MDL);
- Довжина друкованих трас: `12 см`;
- Зовнішній кабель відсутній (`0 м`), рознімів немає.

Розрахунок:
1. Ємність мікросхем: `3 · 10 пФ = 30 пФ`.
2. Ємність друкованої плати: `12 см · 1.3 пФ/см = 15.6 пФ`.
3. Сумарна ємність: `C_b = 30 + 15.6 = 45.6 пФ` (значно менше ліміту 400 пФ).
4. Межі опору підтяжки:
   ```
   R_p,min = (3.3 - 0.4) / 0.003 = 967 Ом
   R_p,max = 300 · 10⁻⁹ / (0.8473 · 45.6 · 10⁻¹²) ≈ 7765 Ом (7.76 кОм)
   ```
5. Вікно опорів: `[967 Ом ... 7765 Ом]`.
6. Оптимальний вибір з ряду E24: резистор **`2.2 кОм`** або **`3.3 кОм`**.
   При `R_p = 2.2 кОм` фактичний час наростання становить `t_r = 0.8473 · 2200 · 45.6 · 10⁻¹² ≈ 85 нс` (ідеальний запас швидкості), а статична потужність — лише `3.8 мВт`.

#### Сценарій 2: Промислова шафа автоматики з виносним пультом (Standard-mode 100 кГц)

Параметри системи:
- Напруга живлення: `V_DD = 5.0 В`;
- Швидкісний режим: Standard-mode (`f = 100 кГц`, `t_r,max = 1000 нс`);
- Кількість чіпів: 4 (головний контролер, годинник DS3231, два розширювачі PCF8574);
- Довжина трас на платі: `25 см`;
- Довжина стрічкового кабелю до панелі керування: `1.5 м`;
- Кількість штирьових рознімів: 2.

Розрахунок:
1. Ємність мікросхем: `4 · 10 пФ = 40 пФ`.
2. Ємність трас PCB: `25 см · 1.3 пФ/см = 32.5 пФ`.
3. Ємність кабелю: `1.5 м · 75 пФ/м = 112.5 пФ`.
4. Ємність рознімів: `2 · 2.0 пФ = 4.0 пФ`.
5. Сумарна ємність: `C_b = 40 + 32.5 + 112.5 + 4 = 189 пФ`.
6. Межі опору:
   ```
   R_p,min = (5.0 - 0.4) / 0.003 = 1533 Ом (1.53 кОм)
   R_p,max = 1000 · 10⁻⁹ / (0.8473 · 189 · 10⁻¹²) ≈ 6245 Ом (6.25 кОм)
   ```
7. Вікно опорів: `[1533 Ом ... 6245 Ом]`.
8. Оптимальний вибір з ряду E24: резистор **`2.7 кОм`** або **`3.3 кОм`**.
   Типовий аматорський номінал `10 кОм` тут неприпустимий, оскільки перевищує `R_p,max` і викличе таймаути шини при опитуванні дисплея.

#### Сценарій 3: Високошвидкісний масив сенсорів (Fast-mode Plus 1 МГц)

Параметри системи:
- Напруга живлення: `V_DD = 3.3 В`;
- Швидкісний режим: Fast-mode Plus (`f = 1 МГц`, `t_r,max = 120 нс`, `I_OL = 20 мА`);
- Кількість пристроїв: 10 спеціалізованих АЦП;
- Сумарна ємність шини: `C_b = 350 пФ`.

Розрахунок:
1. Мінімальний опір (при струмі драйвера 20 мА):
   ```
   R_p,min = (3.3 - 0.4) / 0.020 = 145 Ом
   ```
2. Максимальний опір для забезпечення фронту 120 нс:
   ```
   R_p,max = 120 · 10⁻⁹ / (0.8473 · 350 · 10⁻¹²) ≈ 404 Ом
   ```
3. Вікно опорів: `[145 Ом ... 404 Ом]`.
4. Оптимальний номінал E24: **`220 Ом`** або **`270 Ом`**.
   При `R_p = 220 Ом` фактичний час наростання становить `65 нс`, що гарантує стабільну роботу на частоті 1 МГц.

---

### Методика осцилографічного вимірювання та діагностики

Теоретичний розрахунок завжди має підтверджуватися фізичним вимірюванням на реальній друкованій платі. При цьому слід уникати типових помилок вимірювального тракту:

1. **Врахування паразитної ємності щупа осцилографа:**
   Звичайний пасивний щуп у режимі `1X` має власну ємність `80–120 пФ`. Підключення такого щупа до лінії I²C миттєво подвоює її ємність і спотворює форму сигналу. Вимірювання слід проводити **виключно в режимі 10X** (де вхідна ємність щупа становить лише `10–15 пФ`) або за допомогою активного диференційного пробника з ємністю менше `1 пФ`.
2. **Перевірка точок порогів перемикання:**
   На екрані цифрового осцилографа встановлюють горизонтальні курсори на рівні `0.3 · V_DD` та `0.7 · V_DD`. Автоматичний вимірник часу наростання `Rise Time` необхідно переналаштувати з заводських меж `10% → 90%` на стандартні для I²C межі `30% → 70%`. Якщо прилад підтримує лише вимірювання `10% → 90%`, виміряне значення слід перерахувати за формулою:
   ```
   t_r(30%→70%) ≈ t_r(10%→90%) · (0.8473 / 2.1972) ≈ 0.3856 · t_r(10%→90%)
   ```
3. **Контроль завад і перехресних наведень (Crosstalk):**
   Під час передачі послідовності `0xAA` або `0x55` на лінії SDA перевіряють відсутність голчастих сплесків напруги на сусідній лінії SCL у моменти перемикання даних. Амплітуда наведеної перехресної перешкоди не повинна перевищувати `0.1 · V_DD`.

---

### Інженерний чеклист налагодження апаратного рівня I²C

Перед запуском серійного виробництва електронного виробу рекомендується пройти повний діагностичний чеклист:

1. **Вимірювання статичного опору:** За відключеного живлення омметром перевірте результуючий опір між SDA і `V_DD`, а також між SCL і `V_DD`. Переконайтеся, що значення не є меншим за розрахований `R_p,min` (відсутні невраховані паралельні підтяжки на модулях).
2. **Перевірка рівня V_OL:** Під час передачі активного нульового байта `0x00` виміряйте спад напруги на виводах SDA/SCL. Напруга не повинна перевищувати `0.4 В` на найвіддаленішому веденому чіпі.
3. **Оцінка крутизни фронту t_r:** Перевірте тривалість наростання між `0.3 · V_DD` та `0.7 · V_DD` за найгірших умов (підключені всі зовнішні кабелі та модулі). Значення `t_r` має вкладатися в норму обраного швидкісного режиму з інженерним запасом не менше 20%.
4. **Аналіз температурного діапазону:** Проведіть випробування плати в кліматичній камері при максимальній робочій температурі (+70 °C або +85 °C). Зростання опору каналів транзисторів не повинно призводити до зриву підтвердження ACK.
5. **Тест на завадостійкість:** Перевірте роботу шини при вмиканні поруч розташованих потужних споживачів (двигунів, реле, імпульсних DC-DC перетворювачів). Відсутність хибних спрацьовувань підтверджує коректний вибір завадостійкого опору підтяжки.

---

### Типові схемотехнічні пастки та способи їх усунення

Практична інтеграція резисторів підтяжки в реальних приладах пов'язана з кількома поширеними помилками:

1. **Паралельне нашарування підтяжок (Breakout board trap):**
   Більшість готових модулів із давачами (наприклад, GY-модулі гіроскопів, барометрів чи дисплеїв) містять розпаяні SMD-резистори підтяжки номіналом `4.7 кОм` або `10 кОм`. Якщо підключити до однієї шини чотири такі модулі та ще й увімкнути внутрішню підтяжку мікроконтролера, еквівалентний опір виявиться паралельним з'єднанням усіх резисторів:
   ```
   1 / R_p,eq = 1/R_1 + 1/R_2 + 1/R_3 + 1/R_4
   R_p,eq = 4.7 кОм / 4 = 1.175 кОм
   ```
   У 5-вольтовій системі `R_p,min = 1.53 кОм`, тому `1.175 кОм` викличе неприпустиме струмове перевантаження транзисторів (`I_OL > 3 мА`) і підвищення рівня нуля `V_OL` вище `0.4 В`. Перед складанням схеми необхідно випоювати дублювальні резистори з плат розширення.

2. **Температурний дрейф опору транзистора `R_DS(on)`:**
   Опір відкритого каналу польового транзистора має додатний температурний коефіцієнт і зростає на 40–60% при нагріванні від +25 °C до +105 °C. Якщо номінал `R_p` обрано точно на межі `R_p,min`, при нагріванні приладу спад напруги `V_OL` перевищить поріг `0.4 В`, що спричинить раптові збої підтвердження ACK у нагрітому стані. Завжди закладайте інженерний запас не менше 20–30% вище `R_p,min`.

3. **Асиметрія навантаження SDA та SCL:**
   Часто розробники встановлюють однакові резистори на лінії даних і такту, проте лінія SDA нерідко має більшу ємність через довші відгалуження до багатьох сенсорів. Якщо лінія SDA перевантажена ємністю, для неї слід обирати менший номінал `R_p`, ніж для SCL, щоб збалансувати крутизну фронтів і виключити фазовий зсув між даними й тактом.
