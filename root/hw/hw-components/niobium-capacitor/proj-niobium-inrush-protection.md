# ⚙️ Розрахунок кіл живлення з ніобій-оксидними конденсаторами: пускові струми, дератинг та оцінка надійності

При проектуванні вторинних джерел живлення, імпульсних перетворювачів та вузлів гарячого підключення (*Hot-Swap*) інженер стикається з трьома критичними явищами:
1. **Комутаційні перехідні процеси:** екстремальні амплітуди пускового струму `I_peak` та швидкість його наростання `dI/dt` під час подачі живлення;
2. **Температурний дератинг напруги:** необхідність зниження робочої напруги приладу відносно номінальної при роботі за підвищених температур;
3. **Оцінка надійності та ризиків загоряння:** розрахунок показника інтенсивності відмов (FIT) та середнього часу безвідмовної роботи (MTBF) при виборі між оксидно-ніобієвими (NbO) та класичними танталовими (Ta-MnO₂) компонентами.

Розгляньмо фізику перехідних процесів у розподільних мережах живлення (PDN — *Power Distribution Network*), інженерну методику розрахунку та програмну реалізацію калькулятора мовами C та C++.

### Фізика пускових струмів та коливального контуру

Коли плата підключається до шини живлення або відкривається силовий транзисторний ключ, незаряджений конденсатор фільтра веде себе як коротке замикання. Вхідний контур утворює послідовне RLC-коло, що складається з внутрішнього опору джерела живлення `R_source`, паразитного активного опору друкованих провідників `R_trace`, еквівалентного послідовного опору конденсатора `ESR`, а також паразитної індуктивності кабелів і трас `L_loop`.

Паразитна індуктивність мікросмужкової лінії на друкованій платі оцінюється аналітичним виразом:

```
L_trace ≈ 2 × 10⁻⁷ · l · [ ln( 2·l / (w + t) ) + 0.5 + 0.2235 · (w + t) / l ]  (Гн)
```

де `l` — довжина провідника, `w` — ширина, `t` — товщина мідної фольги. Типові значення для трас живлення становлять від 5 до 30 нГн на кожні 10 см довжини.

Поведінка кола описується диференціальним рівнянням другого порядку для заряду:

```
L_loop · (d²q/dt²) + R_total · (dq/dt) + q/C = V_in
```

де `R_total = R_source + R_trace + ESR`.

Характеристичні корені рівняння визначаються параметрами контуру:
```
s₁,₂ = -α ± √( α² - ω₀² )
```
де `α = R_total / (2 · L_loop)` — коефіцієнт згасання, `ω₀ = 1 / √( L_loop · C )` — власна кутова резонансна частота контуру.

Характер перехідного процесу визначається коефіцієнтом демпфування `ζ` (*damping ratio*):

```
ζ = α / ω₀ = (R_total / 2) · √( C / L_loop )
```

Можливі три режими комутації:
1. **Коливальний режим (Underdamped, ζ < 1):** Якщо активний опір дуже малий (наприклад, при використанні багатошарової кераміки MLCC з ESR у кілька міліом), у контурі виникають високочастотні коливання. Пікова напруга на конденсаторі в момент комутації описується формулою:
   ```
   V_peak = V_in · [ 1 + exp( -π·ζ / √(1 - ζ²) ) ]
   ```
   При `ζ → 0` пікова напруга сягає `V_peak ≈ 2 · V_in`, що створює ризик миттєвого діелектричного пробою.
2. **Критичне демпфування (Critically damped, ζ = 1):** Конденсатор заряджається за мінімально можливий час без перерегулювання та дзвону.
3. **Аперіодичний режим (Overdamped, ζ > 1):** Характерний для оксидно-ніобієвих конденсаторів, помірний ESR яких (0.1–0.3 Ом) природно демпфує паразитні коливання індуктивності трас без потреби у встановленні додаткових баластних резисторів.

Максимальний пусковий струм та гранична швидкість наростання оцінюються співвідношеннями:
```
I_peak ≈ V_in / R_total
(dI/dt)_max ≈ V_in / L_loop
```

Для класичних танталових конденсаторів із катодом MnO₂ високі значення `dI/dt > 50–100 А/мкс` є смертельно небезпечними. Струм локалізується на мікроскопічних дефектах кристалічної решітки оксиду Ta₂O₅, викликаючи точкове теплове розганяння та катастрофічне займання деталі. З цієї причини військові та аерокосмічні стандарти (MIL-HDBK-217, NASA-STD-8739.10) вимагають обов'язкового послідовного захисного резистора не менше `0.1–0.3 Ом/В` для танталу MnO₂.

В оксидно-ніобієвих конденсаторах NbO завдяки властивості самопасивації (перетворенню Nb₂O₅ на високоомний діоксид NbO₂ при нагріванні) обмеження на мінімальний опір контуру **повністю знято**. Вони витримують багаторазові жорсткі комутаційні удари без вибухів і полум'я.

### Інженерні правила дератингу напруги

Зниження робочої напруги (*voltage derating*) — це базовий метод підвищення експлуатаційної надії пасивних компонентів. Норми дератингу суттєво відрізняються залежно від хімічної системи:

* **Класичний тантал Ta-MnO₂:**
  * За температури `T ≤ +85 °C` робоча напруга не повинна перевищувати `50%` від номінальної (`V_op ≤ 0.50 · V_rated`).
  * У температурному діапазоні від `+85 °C` до `+125 °C` напруга лінійно знижується від `50%` до `33%` (`V_op ≤ 0.33 · V_rated` за +125 °C).
  * *Практичний наслідок:* Для шини живлення 5.0 В не можна використовувати танталовий конденсатор на 6.3 В. Інженер зобов'язаний закладати деталь на 10 В або 16 В, що істотно збільшує габарити друкованої плати та вартість специфікації (BOM).

* **Оксид ніобію NbO (серії OxiCap):**
  * За температури `T ≤ +85 °C` виробники (KYOCERA AVX, Vishay) нормують дератинг усього `20%` (`V_op ≤ 0.80 · V_rated`).
  * У діапазоні від `+85 °C` до `+125 °C` дозволена напруга лінійно спадає від `80%` до `50%`.
  * *Практичний наслідок:* Конденсатор NbO з номіналом 6.3 В повністю легально та безпечно працює на шині 5.0 В аж до +85 °C (дозволена напруга `6.3 · 0.80 = 5.04 В`). Для шини 3.3 В достатньо компактного компонента на 4.0 В.

### Розрахунок теплового балансу від струму пульсацій

Крім постійної напруги, на конденсатор діє змінна складова струму — струм пульсацій `I_rms` (*ripple current*), що виникає при комутації ключів DC-DC перетворювача.

Потужність внутрішніх джоулевих втрат на активному опорі діелектрика та електроліту:
```
P_loss = (I_rms)² · ESR
```

Ця потужність розсіюється через поверхню корпусу в навколишнє середовище. Температурний перегрів конденсатора відносно плати становить:
```
ΔT = P_loss · R_th
```

де `R_th` — тепловий опір корпусу (наприклад, для типорозміру EIA 3528 / Case B `R_th ≈ 100–120 °C/Вт`).

Граничний перегрів для стабільної роботи оксидно-ніобієвих конденсаторів обмежують величиною `ΔT_max = +10 °C` за температури навколишнього середовища до +85 °C і `ΔT_max = +5 °C` при роботі біля верхньої межі +125 °C.

### Математична модель надійності (FIT та MTBF)

Інтенсивність відмов `λ` (кількість відмов на `10⁹` годин роботи) розраховується за формулою:

```
λ = λ_base · AF_V · AF_T
```

1. **Коефіцієнт прискорення напругою (AF_V):**
   ```
   AF_V = ( V_op / V_rated )^n
   ```
   Для оксидно-ніобієвих конденсаторів ступеневий показник становить `n ≈ 3.5`, тоді як для танталу MnO₂ він досягає `n ≈ 14.0`. Величезне значення показника для танталу пояснює, чому навіть незначне перевищення напруги викликає лавиноподібне зростання відмов.

2. **Коефіцієнт температурного прискорення Арреніуса (AF_T):**
   ```
   AF_T = exp[ (E_a / k_B) · ( 1 / T_ref_K - 1 / T_op_K ) ]
   ```
   де `E_a ≈ 0.15 еВ` — енергія активації деградаційних процесів, `k_B = 8.617 × 10⁻⁵ еВ/К`, `T_ref_K = 358.15 К` (+85 °C).

Середній час безвідмовної роботи в роках:
```
MTBF_years = ( 10⁹ / λ ) / 8760
```

### Програмний інструмент аналізу шини живлення

Поданий нижче код виконує повний інженерний аналіз: розраховує пусковий струм, коефіцієнт демпфування контуру, перевіряє критерії дератингу, оцінює тепловий розігрів пульсаціями та обчислює надійність для заданих умов схеми.

У версії C++ реалізовано сучасні ідіоми стандарту C++23: використання `std::expected` для безпечної обробки помилок без винятків, `constexpr` функції для можливості валідації компонентів під час компіляції прошивки, та `std::string_view` для ефективної передачі рядкових ідентифікаторів без динамічного виділення пам'яті.

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define KB_EV 8.617333262e-5 /* Стала Больцмана в еВ/К */
#define T_REF_K (85.0 + 273.15) /* Опорна температура +85 °C у Кельвінах */

typedef enum {
    CAP_TYPE_NBO,      /* Оксидно-ніобієвий конденсатор (NbO) */
    CAP_TYPE_TA_MNO2   /* Класичний танталовий конденсатор (Ta-MnO2) */
} CapType;

typedef struct {
    CapType type;
    const char *part_number;
    double capacitance_uf;   /* Ємність у мікрофарадах */
    double rated_voltage_v;  /* Номінальна напруга V_rated */
    double esr_ohm;          /* Послідовний опір ESR на 100 кГц */
    double r_th_c_per_w;     /* Тепловий опір корпусу, °C/Вт */
    double base_fit;         /* Базовий FIT за номінальних умов (+85 °C, V_rated) */
} CapacitorSpec;

typedef struct {
    double bus_voltage_v;    /* Робоча напруга шини живлення */
    double ripple_current_a; /* Діючий струм пульсацій I_rms */
    double source_res_ohm;   /* Опір джерела та проводки плати */
    double loop_inductance_nh;/* Паразитна індуктивність контуру в нГн */
    double operating_temp_c; /* Робоча температура навколишнього середовища в °C */
} CircuitCondition;

typedef struct {
    double inrush_peak_current_a;
    double didt_max_a_per_us;
    double damping_factor;
    double power_loss_w;
    double temp_rise_c;
    double allowed_voltage_v;
    bool is_derating_valid;
    bool is_thermal_valid;
    double operating_fit;
    double mtbf_years;
    const char *safety_status;
} AnalysisResult;

bool evaluate_capacitor(const CapacitorSpec *cap, const CircuitCondition *cond, AnalysisResult *out) {
    if (!cap || !cond || !out) return false;

    /* 1. Розрахунок параметрів пускового струму та коливального контуру */
    double total_r = cond->source_res_ohm + cap->esr_ohm;
    if (total_r < 1e-4) total_r = 1e-4;
    out->inrush_peak_current_a = cond->bus_voltage_v / total_r;

    double loop_l_h = cond->loop_inductance_nh * 1e-9;
    double cap_f = cap->capacitance_uf * 1e-6;

    if (loop_l_h > 1e-12) {
        out->didt_max_a_per_us = (cond->bus_voltage_v / loop_l_h) * 1e-6;
        out->damping_factor = (total_r / 2.0) * sqrt(cap_f / loop_l_h);
    } else {
        out->didt_max_a_per_us = 0.0;
        out->damping_factor = 10.0; /* Аперіодичний */
    }

    /* 2. Розрахунок втрат потужності та власного нагріву */
    out->power_loss_w = (cond->ripple_current_a * cond->ripple_current_a) * cap->esr_ohm;
    out->temp_rise_c = out->power_loss_w * cap->r_th_c_per_w;
    out->is_thermal_valid = (out->temp_rise_c <= 10.0);

    /* 3. Перевірка температурного дератингу напруги */
    double t_effective = cond->operating_temp_c + out->temp_rise_c;

    if (cap->type == CAP_TYPE_NBO) {
        if (t_effective <= 85.0) {
            out->allowed_voltage_v = cap->rated_voltage_v * 0.80;
        } else if (t_effective <= 125.0) {
            double derate_factor = 0.80 - 0.30 * ((t_effective - 85.0) / 40.0);
            out->allowed_voltage_v = cap->rated_voltage_v * derate_factor;
        } else {
            out->allowed_voltage_v = 0.0;
        }
    } else { /* Ta-MnO2 */
        if (t_effective <= 85.0) {
            out->allowed_voltage_v = cap->rated_voltage_v * 0.50;
        } else if (t_effective <= 125.0) {
            double derate_factor = 0.50 - 0.17 * ((t_effective - 85.0) / 40.0);
            out->allowed_voltage_v = cap->rated_voltage_v * derate_factor;
        } else {
            out->allowed_voltage_v = 0.0;
        }
    }

    out->is_derating_valid = (cond->bus_voltage_v <= out->allowed_voltage_v);

    /* 4. Оцінка надійності: FIT та MTBF */
    double voltage_ratio = cond->bus_voltage_v / cap->rated_voltage_v;
    if (voltage_ratio > 1.2) voltage_ratio = 1.2;

    double n_exp = (cap->type == CAP_TYPE_NBO) ? 3.5 : 14.0;
    double af_v = pow(voltage_ratio, n_exp);

    double t_op_k = t_effective + 273.15;
    double ea_ev = 0.15;
    double delta_inv_t = (1.0 / T_REF_K) - (1.0 / t_op_k);
    double af_t = exp((ea_ev / KB_EV) * delta_inv_t);

    out->operating_fit = cap->base_fit * af_v * af_t;
    if (out->operating_fit > 0.0) {
        out->mtbf_years = (1.0e9 / out->operating_fit) / 8760.0;
    } else {
        out->mtbf_years = 0.0;
    }

    /* Формування вердикту безпеки */
    if (!out->is_derating_valid) {
        out->safety_status = (cap->type == CAP_TYPE_NBO) 
            ? "ПОПЕРЕДЖЕННЯ: перевищено дератинг (відмова безпечна: перехід у розрив)"
            : "КРИТИЧНА ПОМИЛКА: порушено дератинг 50%! Ризик займання танталу!";
    } else if (!out->is_thermal_valid) {
        out->safety_status = "УВАГА: надмірний перегрів від пульсацій струму (dT > 10 °C)";
    } else {
        out->safety_status = "НОРМА: дератинг, пульсації та надійність у межах стандарту";
    }

    return true;
}

int main(void) {
    CapacitorSpec nbo_cap = {
        .type = CAP_TYPE_NBO,
        .part_number = "NOJB107M006R0200 (AVX 100uF / 6.3V)",
        .capacitance_uf = 100.0,
        .rated_voltage_v = 6.3,
        .esr_ohm = 0.200,
        .r_th_c_per_w = 110.0,
        .base_fit = 5000.0
    };

    CapacitorSpec ta_cap = {
        .type = CAP_TYPE_TA_MNO2,
        .part_number = "TAJB107M006RNJ (KEMET 100uF / 6.3V)",
        .capacitance_uf = 100.0,
        .rated_voltage_v = 6.3,
        .esr_ohm = 0.250,
        .r_th_c_per_w = 110.0,
        .base_fit = 5000.0
    };

    CircuitCondition bus_5v = {
        .bus_voltage_v = 5.0,
        .ripple_current_a = 0.450, /* 450 мА RMS */
        .source_res_ohm = 0.030,
        .loop_inductance_nh = 15.0,
        .operating_temp_c = 65.0
    };

    AnalysisResult res_nbo, res_ta;
    evaluate_capacitor(&nbo_cap, &bus_5v, &res_nbo);
    evaluate_capacitor(&ta_cap, &bus_5v, &res_ta);

    printf("=================================================================\n");
    printf("РОЗРАХУНОК НАДІЙНОСТІ ТА ДЕРАТИНГУ НА ШИНІ 5.0 В (T = +65 °C)\n");
    printf("=================================================================\n");

    printf("\n1. ОКСИД НІОБІЮ: %s\n", nbo_cap.part_number);
    printf("   Пусковий струм: %.1f А, dI/dt: %.1f А/мкс, Демпфування zeta: %.2f\n", 
           res_nbo.inrush_peak_current_a, res_nbo.didt_max_a_per_us, res_nbo.damping_factor);
    printf("   Перегрів від пульсацій: +%.1f °C (Втрати: %.3f Вт)\n", res_nbo.temp_rise_c, res_nbo.power_loss_w);
    printf("   Дозволена напруга: %.2f В (Факт: %.2f В) -> %s\n", 
           res_nbo.allowed_voltage_v, bus_5v.bus_voltage_v, res_nbo.is_derating_valid ? "ПРОХОДИТЬ" : "НЕ ПРОХОДИТЬ");
    printf("   Інтенсивність відмов: %.1f FIT | MTBF: %.1f років\n", res_nbo.operating_fit, res_nbo.mtbf_years);
    printf("   Статус: %s\n", res_nbo.safety_status);

    printf("\n2. ТАНТАЛ MnO2: %s\n", ta_cap.part_number);
    printf("   Пусковий струм: %.1f А, dI/dt: %.1f А/мкс, Демпфування zeta: %.2f\n", 
           res_ta.inrush_peak_current_a, res_ta.didt_max_a_per_us, res_ta.damping_factor);
    printf("   Перегрів від пульсацій: +%.1f °C (Втрати: %.3f Вт)\n", res_ta.temp_rise_c, res_ta.power_loss_w);
    printf("   Дозволена напруга: %.2f В (Факт: %.2f В) -> %s\n", 
           res_ta.allowed_voltage_v, bus_5v.bus_voltage_v, res_ta.is_derating_valid ? "ПРОХОДИТЬ" : "НЕ ПРОХОДИТЬ");
    printf("   Інтенсивність відмов: %.1f FIT | MTBF: %.1f років\n", res_ta.operating_fit, res_ta.mtbf_years);
    printf("   Статус: %s\n", res_ta.safety_status);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>
#include <expected>
#include <algorithm>

namespace power_analysis {

constexpr double KB_EV = 8.617333262e-5;
constexpr double T_REF_K = 85.0 + 273.15;

enum class CapType {
    NiobiumOxide,
    TantalumMno2
};

struct CapacitorSpec {
    CapType type;
    std::string_view part_number;
    double capacitance_uf;
    double rated_voltage_v;
    double esr_ohm;
    double r_th_c_per_w;
    double base_fit;
};

struct CircuitCondition {
    double bus_voltage_v;
    double ripple_current_a;
    double source_res_ohm;
    double loop_inductance_nh;
    double operating_temp_c;
};

struct AnalysisResult {
    double inrush_peak_current_a;
    double didt_max_a_per_us;
    double damping_factor;
    double power_loss_w;
    double temp_rise_c;
    double allowed_voltage_v;
    bool is_derating_valid;
    bool is_thermal_valid;
    double operating_fit;
    double mtbf_years;
    std::string_view safety_status;
};

enum class AnalysisError {
    InvalidParameters,
    TemperatureOutOfRange
};

[[nodiscard]] constexpr std::expected<AnalysisResult, AnalysisError> evaluate_capacitor(
    const CapacitorSpec& cap,
    const CircuitCondition& cond) noexcept
{
    if (cap.rated_voltage_v <= 0.0 || cond.bus_voltage_v <= 0.0 || cap.capacitance_uf <= 0.0) {
        return std::unexpected(AnalysisError::InvalidParameters);
    }
    if (cond.operating_temp_c < -55.0 || cond.operating_temp_c > 150.0) {
        return std::unexpected(AnalysisError::TemperatureOutOfRange);
    }

    AnalysisResult res{};

    // 1. Динаміка пускового струму та коефіцієнт демпфування
    const double total_r = std::max(1e-4, cond.source_res_ohm + cap.esr_ohm);
    res.inrush_peak_current_a = cond.bus_voltage_v / total_r;

    const double loop_l_h = cond.loop_inductance_nh * 1e-9;
    const double cap_f = cap.capacitance_uf * 1e-6;

    if (loop_l_h > 1e-12) {
        res.didt_max_a_per_us = (cond.bus_voltage_v / loop_l_h) * 1e-6;
        res.damping_factor = (total_r / 2.0) * std::sqrt(cap_f / loop_l_h);
    } else {
        res.didt_max_a_per_us = 0.0;
        res.damping_factor = 10.0;
    }

    // 2. Втрати потужності та тепловий баланс
    res.power_loss_w = (cond.ripple_current_a * cond.ripple_current_a) * cap.esr_ohm;
    res.temp_rise_c = res.power_loss_w * cap.r_th_c_per_w;
    res.is_thermal_valid = (res.temp_rise_c <= 10.0);

    // 3. Дератинг напруги з урахуванням власного перегріву
    const double t_effective = cond.operating_temp_c + res.temp_rise_c;

    if (cap.type == CapType::NiobiumOxide) {
        if (t_effective <= 85.0) {
            res.allowed_voltage_v = cap.rated_voltage_v * 0.80;
        } else if (t_effective <= 125.0) {
            const double factor = 0.80 - 0.30 * ((t_effective - 85.0) / 40.0);
            res.allowed_voltage_v = cap.rated_voltage_v * factor;
        } else {
            res.allowed_voltage_v = 0.0;
        }
    } else { // TantalumMno2
        if (t_effective <= 85.0) {
            res.allowed_voltage_v = cap.rated_voltage_v * 0.50;
        } else if (t_effective <= 125.0) {
            const double factor = 0.50 - 0.17 * ((t_effective - 85.0) / 40.0);
            res.allowed_voltage_v = cap.rated_voltage_v * factor;
        } else {
            res.allowed_voltage_v = 0.0;
        }
    }

    res.is_derating_valid = (cond.bus_voltage_v <= res.allowed_voltage_v);

    // 4. Оцінка надійності: FIT та MTBF
    const double v_ratio = std::clamp(cond.bus_voltage_v / cap.rated_voltage_v, 0.0, 1.2);
    const double n_exp = (cap.type == CapType::NiobiumOxide) ? 3.5 : 14.0;
    const double af_v = std::pow(v_ratio, n_exp);

    const double t_op_k = t_effective + 273.15;
    constexpr double ea_ev = 0.15;
    const double delta_inv_t = (1.0 / T_REF_K) - (1.0 / t_op_k);
    const double af_t = std::exp((ea_ev / KB_EV) * delta_inv_t);

    res.operating_fit = cap.base_fit * af_v * af_t;
    res.mtbf_years = (res.operating_fit > 0.0) ? ((1.0e9 / res.operating_fit) / 8760.0) : 0.0;

    if (!res.is_derating_valid) {
        res.safety_status = (cap.type == CapType::NiobiumOxide)
            ? "ПОПЕРЕДЖЕННЯ: дератинг перевищено (відмова без горіння)"
            : "КРИТИЧНА ПОМИЛКА: ризик спалаху танталу через перевищення дератингу 50%!";
    } else if (!res.is_thermal_valid) {
        res.safety_status = "УВАГА: перегрів від пульсацій струму перевищує норму (+10 °C)";
    } else {
        res.safety_status = "НОРМА: робоча зона безпечна";
    }

    return res;
}

} // namespace power_analysis

int main() {
    using namespace power_analysis;

    constexpr CapacitorSpec nbo_cap{
        .type = CapType::NiobiumOxide,
        .part_number = "NOJB107M006R0200 (AVX 100uF / 6.3V)",
        .capacitance_uf = 100.0,
        .rated_voltage_v = 6.3,
        .esr_ohm = 0.200,
        .r_th_c_per_w = 110.0,
        .base_fit = 5000.0
    };

    constexpr CapacitorSpec ta_cap{
        .type = CapType::TantalumMno2,
        .part_number = "TAJB107M006RNJ (KEMET 100uF / 6.3V)",
        .capacitance_uf = 100.0,
        .rated_voltage_v = 6.3,
        .esr_ohm = 0.250,
        .r_th_c_per_w = 110.0,
        .base_fit = 5000.0
    };

    constexpr CircuitCondition bus_5v{
        .bus_voltage_v = 5.0,
        .ripple_current_a = 0.450,
        .source_res_ohm = 0.030,
        .loop_inductance_nh = 15.0,
        .operating_temp_c = 65.0
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=================================================================\n";
    std::cout << "ПОРІВНЯЛЬНИЙ АНАЛІЗ ПОВЕДІНКИ NbO ТА Ta-MnO2 НА ШИНІ 5.0 В\n";
    std::cout << "=================================================================\n\n";

    if (auto res = evaluate_capacitor(nbo_cap, bus_5v); res.has_value()) {
        std::cout << "1. " << nbo_cap.part_number << '\n';
        std::cout << "   Пусковий струм I_peak: " << res->inrush_peak_current_a << " А, dI/dt: "
                  << res->didt_max_a_per_us << " А/мкс, Демпфування zeta: " << res->damping_factor << '\n';
        std::cout << "   Перегрів від пульсацій: +" << res->temp_rise_c << " °C\n";
        std::cout << "   Дозволена напруга: " << res->allowed_voltage_v << " В -> "
                  << (res->is_derating_valid ? "ПРОХОДИТЬ (20% дератинг)" : "ЗАБОРОНЕНО") << '\n';
        std::cout << "   FIT: " << res->operating_fit << " | MTBF: " << res->mtbf_years << " років\n";
        std::cout << "   Статус: " << res->safety_status << "\n\n";
    }

    if (auto res = evaluate_capacitor(ta_cap, bus_5v); res.has_value()) {
        std::cout << "2. " << ta_cap.part_number << '\n';
        std::cout << "   Пусковий струм I_peak: " << res->inrush_peak_current_a << " А, dI/dt: "
                  << res->didt_max_a_per_us << " А/мкс, Демпфування zeta: " << res->damping_factor << '\n';
        std::cout << "   Перегрів від пульсацій: +" << res->temp_rise_c << " °C\n";
        std::cout << "   Дозволена напруга: " << res->allowed_voltage_v << " В -> "
                  << (res->is_derating_valid ? "ПРОХОДИТЬ" : "НЕ ПРОХОДИТЬ (потрібно 50%)") << '\n';
        std::cout << "   FIT: " << res->operating_fit << " | MTBF: " << res->mtbf_years << " років\n";
        std::cout << "   Статус: " << res->safety_status << "\n";
    }

    return 0;
}
```
:::

### Інженерні висновки та рекомендації трасування друкованої плати

1. **Габаритна оптимізація посадкового місця:** Використання оксидно-ніобієвого конденсатора 6.3 В на шині 5.0 В дозволяє зменшити площу друкованої плати у 2–2.5 раза порівняно з танталом MnO₂, для якого потрібен компонент на 10 В або 16 В більшого типорозміру Case D/E.
2. **Топологія підключення (Kelvin Connections):** Конденсатори фільтра слід розміщувати безпосередньо біля виводів живлення навантаження. Підключення до полігонів живлення та землі виконують широкими короткими трасами або здвоєними перехідними отворами (*vias*) безпосередньо біля контактних майданчиків для мінімізації паразитної індуктивності контуру `L_loop`.
3. **Демпфування паразитних резонансів:** Завдяки стабільному ESR (0.15–0.30 Ом) оксидно-ніобієвий конденсатор забезпечує коефіцієнт демпфування `ζ > 0.7`, що запобігає виникненню високовольтного дзвону при комутаціях і усуває потребу у встановленні додаткових зовнішніх RC-ланцюгів.
4. **Контроль теплового режиму:** При струмах пульсацій понад 0.5 А слід перевіряти перегрів `ΔT = I_rms² · ESR · R_th`. Якщо перегрів перевищує +10 °C, рекомендується розподілити навантаження на два паралельних конденсатори меншого типорозміру.
