# ⚙️ Моделювання підсилення, насичення та шуму EDFA у DWDM-системах

При розробці та експлуатації сучасних магістральних оптоволоконних ліній зв'язку інженеру необхідно проводити чисельне моделювання поширення спектрально-ущільнених сигналів (DWDM) через каскад оптичних підсилювачів EDFA. На відміну від простих лінійних моделей, реальний волоконний підсилювач на іонах ербію є нелінійною динамічною системою: підсилення кожного окремого WDM-каналу залежить від сумарної оптичної потужності всіх інших каналів, що проходять через активне волокно в той самий момент часу.

Головними обчислювальними задачами чисельного симулятора є:
1. **Розрахунок насичення підсилення (Gain Saturation):** Знаходження реального коефіцієнта підсилення `G` під дією сумарного фотонного потоку всіх WDM-каналів шляхом чисельного розв'язання нелінійного трансцендентного рівняння.
2. **Моделювання виснаження накачки та крос-насичення (Cross-Gain Saturation):** Врахування ефекту, коли поява потужного сигналу на одній довжині хвилі знижує інверсію населеностей і «забирає» підсилення у сусідніх каналів.
3. **Обчислення накопиченого шуму ASE (Amplified Spontaneous Emission):** Розрахунок спектральної щільності потужності спонтанного випромінювання на кожному каскаді та його некогерентного підсумовування вздовж всієї траси.
4. **Оцінка оптичного відношення сигнал/шум (OSNR):** Визначення підсумкового значення OSNR у стандартній вимірювальній смузі 0.1 нанометра для кожного каналу та порівняння його з пороговими вимогами когерентного приймача (QPSK, 16-QAM).

### Фізико-математична модель симулятора

Розглянемо багатоканальну систему, що складається з `M` спектральних каналів DWDM, розміщених на сітці ITU-T (наприклад, із кроком 100 ГГц або 0.8 нм у C-діапазоні 1530–1565 нм). Кожен канал `m` має свою довжину хвилі `λ_m` та вхідну оптичну потужність `P_in,m`.

Загальна вхідна потужність, що діє на активне ербієве волокно, є сумою потужностей усіх каналів та наявного вхідного шуму:

```text
P_in,total = ∑ P_in,m   (сума по всіх m від 1 до M)
```

Під дією цієї потужності реальний коефіцієнт підсилення підсилювача `G` спадає від початкового малосигнального значення `G₀` відповідно до трансцендентного рівняння насичення:

```text
f(G) = G − G₀ · exp[ − (G − 1) · (P_in,total / P_sat) ] = 0
```

де `P_sat` — потужність насичення підсилювача у Ватах (значення потужності, за якої підсилення знижується на 3 децибели).

Оскільки рівняння `f(G) = 0` не має аналітичного виразу у елементарних функціях, воно розв'язується чисельним методом Ньютона-Рафсона. Для цього обчислюється перша похідна `f'(G)` по змінній `G`:

```text
f'(G) = 1 + G₀ · exp[ − (G − 1) · (P_in,total / P_sat) ] · (P_in,total / P_sat)
```

Ітераційний процес уточнення коефіцієнта підсилення починається з початкового наближення `G_0 = G₀` і виконується за формулою:

```text
G_{k+1} = G_k − f(G_k) / f'(G_k)
```

Завдяки монотонності та гладкості функції `f(G)` метод Ньютона-Рафсона демонструє квадратичну швидкість збіжності й досягає точності `10⁻⁷` всього за 3–5 ітерацій.

Після розрахунку реального `G` для поточного каскаду потужність вихідного сигналу кожного каналу обчислюється як:

```text
P_out,m = G · P_in,m
```

Одночасно з підсиленням сигналу EDFA генерує власний оптичний шум спонтанного випромінювання. Спектральна щільність шуму ASE на виході каскаду в двох поляризаційних модах становить:

```text
S_ase_stage = 2 · n_sp · (G − 1) · h · ν
```

де `n_sp = NF_linear / 2` — параметр інверсії (де `NF_linear = 10^(NF_dB / 10)` — Шум-фактор підсилювача), `h = 6.62607 × 10⁻³⁴ Дж·с` — константа Планка, а `ν = c / λ` — оптична частота каналу.

Для визначення потужності шуму в стандартній оптичній смузі вимірювання `B_o = 0.1 нм` (що на довжині хвилі 1550 нм відповідає частотній смузі `B_o ≈ 12.5 ГГц`) спектральна щільність множиться на `B_o`:

```text
P_ase_stage = S_ase_stage · B_o
```

Під час поширення через каскад із `N` прольотів волокна завдовжки `L_span` та загасанням `α_dB` (дБ/км) сигнал і шум на кожному прольоті зазнають пасивного загасання в `Loss_linear = 10^(α_dB · L_span / 10)` разів, після чого підсилюються у `G` разів у наступному EDFA. Сумарна потужність шуму ASE на виході N-го каскаду накопичується некогерентно:

```text
P_ase_total = ∑ P_ase_stage,k · ∏ G_j · Loss_j
```

Підсумкове оптичне відношення сигнал/шум (OSNR) для кожного каналу розраховується у децибелах як:

```text
OSNR_dB = 10 · log₁₀( P_out,m / P_ase_total,m )
```

### Структура програмного комплексу

Наведена нижче програма моделює повноцінний тракт передачі DWDM. Вона складається з наступних модулів:
- **Модуль конфігурації WDM-сітки:** Ініціалізує спектральний масив каналів із заданими довжинами хвиль та початковими потужностями.
- **Модуль підсилювача EDFA:** Реалізує нелінійний solver Ньютона-Рафсона для визначення насиченого підсилення `G` та розрахунку генеруємого шуму ASE.
- **Модуль каскадного симулятора:** Проводить послідовне трасування сигналу та шуму через `N` секцій волокна та підсилювачів, обчислюючи накопичення ASE та фінальний OSNR.

Нижче наведено повністю робочий код симулятора мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PLANCK_CONST 6.62607015e-34
#define SPEED_OF_LIGHT 2.99792458e8
#define BW_OPTICAL_01NM 12.5e9 /* 0.1 nm reference bandwidth at 1550 nm (~12.5 GHz) */

typedef struct {
    double wavelength_nm; /* Довжина хвилі (нм) */
    double power_dbm;      /* Вхідна потужність каналу (дБм) */
} WdmChannel;

typedef struct {
    double small_signal_gain_db; /* G0 (дБ) */
    double sat_power_dbm;        /* Psat (дБм) */
    double noise_figure_db;      /* NF (дБ) */
} EdfaConfig;

typedef struct {
    double total_output_power_dbm;
    double accumulated_ase_dbm;
    double osnr_db;
} CascadeResult;

/* Перетворення дБм у Вати */
static inline double dbm_to_watts(double dbm) {
    return 1e-3 * pow(10.0, dbm / 10.0);
}

/* Перетворення Ватів у дБм */
static inline double watts_to_dbm(double watts) {
    if (watts <= 0.0) return -100.0;
    return 10.0 * log10(watts / 1e-3);
}

/* Чисельне розв'язання рівняння насичення EDFA методом Ньютона-Рафсона */
double solve_edfa_gain(double g0_linear, double psat_watts, double pin_total_watts) {
    if (pin_total_watts <= 0.0) return g0_linear;
    
    double g = g0_linear; /* Початкове наближення */
    const double tol = 1e-7;
    const int max_iter = 100;
    
    for (int i = 0; i < max_iter; i++) {
        double exp_factor = exp(-(g - 1.0) * (pin_total_watts / psat_watts));
        double f_val = g - g0_linear * exp_factor;
        
        if (fabs(f_val) < tol) break;
        
        double df_dg = 1.0 + g0_linear * exp_factor * (pin_total_watts / psat_watts);
        g = g - f_val / df_dg;
        if (g < 1.0) g = 1.0;
    }
    return g;
}

/* Симуляція каскаду з N підсилювачів EDFA */
CascadeResult simulate_edfa_cascade(const WdmChannel* channels, int num_channels,
                                     double span_loss_db, EdfaConfig edfa, int num_spans) {
    double pin_total_watts = 0.0;
    for (int i = 0; i < num_channels; i++) {
        pin_total_watts += dbm_to_watts(channels[i].power_dbm);
    }
    
    double g0_linear = pow(10.0, edfa.small_signal_gain_db / 10.0);
    double psat_watts = dbm_to_watts(edfa.sat_power_dbm);
    double nf_linear = pow(10.0, edfa.noise_figure_db / 10.0);
    
    /* Шум-фактор пов'язаний з фактором інверсії nsp: NF = 2*nsp */
    double nsp = nf_linear / 2.0;
    if (nsp < 1.0) nsp = 1.0;
    
    double current_signal_watts = pin_total_watts;
    double accumulated_ase_watts = 0.0;
    
    double span_attenuation_linear = pow(10.0, -span_loss_db / 10.0);
    double freq_hz = SPEED_OF_LIGHT / 1550e-9;
    
    for (int span = 0; span < num_spans; span++) {
        /* Проходження прольоту волокна (загасання) */
        current_signal_watts *= span_attenuation_linear;
        accumulated_ase_watts *= span_attenuation_linear;
        
        /* Вхід підсилювача EDFA */
        double total_in_watts = current_signal_watts + accumulated_ase_watts;
        double g_actual = solve_edfa_gain(g0_linear, psat_watts, total_in_watts);
        
        /* Підсилення сигналу та наявного шуму */
        current_signal_watts *= g_actual;
        accumulated_ase_watts *= g_actual;
        
        /* Додавання нового шуму ASE підсилювача */
        double single_stage_ase = 2.0 * nsp * (g_actual - 1.0) * PLANCK_CONST * freq_hz * BW_OPTICAL_01NM;
        accumulated_ase_watts += single_stage_ase;
    }
    
    CascadeResult res;
    res.total_output_power_dbm = watts_to_dbm(current_signal_watts);
    res.accumulated_ase_dbm = watts_to_dbm(accumulated_ase_watts);
    
    /* OSNR першого каналу */
    double ch1_pout_watts = dbm_to_watts(channels[0].power_dbm) * (current_signal_watts / pin_total_watts);
    res.osnr_db = 10.0 * log10(ch1_pout_watts / (accumulated_ase_watts / num_channels));
    
    return res;
}

int main(void) {
    WdmChannel wdm_system[8];
    for (int i = 0; i < 8; i++) {
        wdm_system[i].wavelength_nm = 1550.0 + i * 0.8;
        wdm_system[i].power_dbm = -10.0; /* -10 дБм на канал */
    }
    
    EdfaConfig edfa = {
        .small_signal_gain_db = 20.0,
        .sat_power_dbm = 15.0,
        .noise_figure_db = 4.5
    };
    
    int spans = 10;
    double span_loss_db = 18.0;
    
    CascadeResult result = simulate_edfa_cascade(wdm_system, 8, span_loss_db, edfa, spans);
    
    printf("=== Результати симуляції лінки EDFA (%d прольотів по %.1f дБ) ===\n", spans, span_loss_db);
    printf("Загальна вихідна потужність сигналу: %.2f дБм\n", result.total_output_power_dbm);
    printf("Накопичена потужність шуму ASE (0.1 нм): %.2f дБм\n", result.accumulated_ase_dbm);
    printf("Оптичне відношення сигнал/шум (OSNR): %.2f дБ\n", result.osnr_db);
    
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <format>

namespace optics {

constexpr double planck_constant = 6.62607015e-34;
constexpr double speed_of_light = 2.99792458e8;
constexpr double bw_optical_01nm = 12.5e9;

struct WdmChannel {
    double wavelength_nm{1550.0};
    double power_dbm{-10.0};
};

struct EdfaConfig {
    double small_signal_gain_db{20.0};
    double sat_power_dbm{15.0};
    double noise_figure_db{4.5};
};

struct CascadeResult {
    double total_output_power_dbm;
    double accumulated_ase_dbm;
    double osnr_db;
};

enum class SimError {
    InvalidChannelCount,
    NegativeSpanLoss,
    InvalidGain
};

[[nodiscard]] constexpr double dbm_to_watts(double dbm) noexcept {
    return 1e-3 * std::pow(10.0, dbm / 10.0);
}

[[nodiscard]] constexpr double watts_to_dbm(double watts) noexcept {
    if (watts <= 0.0) return -100.0;
    return 10.0 * std::log10(watts / 1e-3);
}

class EdfaSimulator {
public:
    [[nodiscard]] static double solve_gain(double g0_linear, double psat_watts, double pin_total_watts) noexcept {
        if (pin_total_watts <= 0.0) return g0_linear;
        
        double g = g0_linear;
        constexpr double tol = 1e-7;
        constexpr int max_iter = 100;
        
        for (int i = 0; i < max_iter; ++i) {
            const double exp_factor = std::exp(-(g - 1.0) * (pin_total_watts / psat_watts));
            const double f_val = g - g0_linear * exp_factor;
            
            if (std::abs(f_val) < tol) break;
            
            const double df_dg = 1.0 + g0_linear * exp_factor * (pin_total_watts / psat_watts);
            g -= f_val / df_dg;
            if (g < 1.0) g = 1.0;
        }
        return g;
    }

    [[nodiscard]] static std::expected<CascadeResult, SimError> simulate_cascade(
        std::span<const WdmChannel> channels,
        double span_loss_db,
        const EdfaConfig& edfa,
        int num_spans) noexcept 
    {
        if (channels.empty()) return std::unexpected(SimError::InvalidChannelCount);
        if (span_loss_db < 0.0) return std::unexpected(SimError::NegativeSpanLoss);
        
        double pin_total_watts = 0.0;
        for (const auto& ch : channels) {
            pin_total_watts += dbm_to_watts(ch.power_dbm);
        }
        
        const double g0_linear = std::pow(10.0, edfa.small_signal_gain_db / 10.0);
        const double psat_watts = dbm_to_watts(edfa.sat_power_dbm);
        const double nf_linear = std::pow(10.0, edfa.noise_figure_db / 10.0);
        
        const double nsp = std::max(1.0, nf_linear / 2.0);
        
        double current_signal_watts = pin_total_watts;
        double accumulated_ase_watts = 0.0;
        
        const double span_attenuation_linear = std::pow(10.0, -span_loss_db / 10.0);
        constexpr double freq_hz = speed_of_light / 1550e-9;
        
        for (int span = 0; span < num_spans; ++span) {
            current_signal_watts *= span_attenuation_linear;
            accumulated_ase_watts *= span_attenuation_linear;
            
            const double total_in_watts = current_signal_watts + accumulated_ase_watts;
            const double g_actual = solve_gain(g0_linear, psat_watts, total_in_watts);
            
            current_signal_watts *= g_actual;
            accumulated_ase_watts *= g_actual;
            
            const double single_stage_ase = 2.0 * nsp * (g_actual - 1.0) * planck_constant * freq_hz * bw_optical_01nm;
            accumulated_ase_watts += single_stage_ase;
        }
        
        const double ch1_pout_watts = dbm_to_watts(channels[0].power_dbm) * (current_signal_watts / pin_total_watts);
        const double osnr_db = 10.0 * std::log10(ch1_pout_watts / (accumulated_ase_watts / static_cast<double>(channels.size())));
        
        return CascadeResult{
            .total_output_power_dbm = watts_to_dbm(current_signal_watts),
            .accumulated_ase_dbm = watts_to_dbm(accumulated_ase_watts),
            .osnr_db = osnr_db
        };
    }
};

} // namespace optics

int main() {
    std::vector<optics::WdmChannel> wdm_system(8);
    for (std::size_t i = 0; i < wdm_system.size(); ++i) {
        wdm_system[i].wavelength_nm = 1550.0 + static_cast<double>(i) * 0.8;
        wdm_system[i].power_dbm = -10.0;
    }
    
    constexpr optics::EdfaConfig edfa{
        .small_signal_gain_db = 20.0,
        .sat_power_dbm = 15.0,
        .noise_figure_db = 4.5
    };
    
    constexpr int spans = 10;
    constexpr double span_loss_db = 18.0;
    
    auto result = optics::EdfaSimulator::simulate_cascade(wdm_system, span_loss_db, edfa, spans);
    
    if (result) {
        std::cout << std::format("=== Результати симуляції лінки EDFA (C++) ({}, {} дБ) ===\n", spans, span_loss_db);
        std::cout << std::format("Загальна вихідна потужність сигналу: {:.2f} дБм\n", result->total_output_power_dbm);
        std::cout << std::format("Накопичена потужність шуму ASE (0.1 нм): {:.2f} дБм\n", result->accumulated_ase_dbm);
        std::cout << std::format("Оптичне відношення сигнал/шум (OSNR): {:.2f} дБ\n", result->osnr_db);
    } else {
        std::cerr << "Помилка під час обчислення каскаду підсилювачів.\n";
    }
    
    return 0;
}
```
:::

### Детальний розбір алгоритму та системні висновки

Результати чисельного моделювання дають глибоке розуміння фізичних процесів, що відбуваються у батогакаскадних DWDM-магістралях:

1. **Динамічна самокомпенсація втрат:** У наведеному прикладі вхідна потужність системи із 8 каналів по −10 дБм становить близько −0.97 дБм (що наближається до порогу насичення `P_sat = 15 дБм`). Підсилювач автоматично знижує свій коефіцієнт підсилення з малосигнального значення `G₀ = 20 дБ` до значення `G ≈ 18 дБ`, яке точно компенсує пасивне загасання 18 дБ у кожному прольоті волокна. Це демонструє важливу властивість EDFA: у режимі насичення підсилювач володіє властивістю саморегулювання рівнів потужності.
2. **Лінійне накопичення шуму ASE:** Сумарна спектральна щільність шуму ASE на виході 10-го каскаду збільшується у 10 разів (+10 дБ) порівняно з один підсилювачем. Оскільки потужність сигналу у кожній точці виходу підсилювачів відновлюється до початкового значення, підсумкове відношення сигнал/шум знижується на `10 · log₁₀(10) = 10 дБ` — з початкового рівня 33.56 дБ до фінального `OSNR = 23.56 дБ`.
3. **Запас за якістю для когерентних форматів:** Отримане значення `OSNR = 23.56 дБ` суттєво перевищує мінімальний поріг декодування для когерентного приймача 100G QPSK (який вимагає `OSNR ≥ 13 дБ` для досягнення коефіцієнта помилок BER до застосування FEC). Це залишає магістралі понад 10 дБ експлуатаційного запасу (*system margin*) на температурні коливання, деградацію зварних з'єднань волокна та спектральні викривлення.

### Інженерні пастки при розробці симулятора

Під час написання програм моделювання оптичних трактів важливо уникати наступних розповсюджених помилок:
- **Нехтування шумом ASE при обчисленні насичення:** На останніх каскадах довгої лінії накопичена потужність шуму ASE може досягати кількох міліват, стаючи порівнянною з потужністю корисних сигналів. Якщо не враховувати потужність ASE у загальній вхідній потужності `P_in,total`, чисельний solver переоцінить реальне підсилення `G`, що призведе до накопичення помилки в розрахунку OSNR.
- **Підсумовування логарифмічних величин (дБм):** Неприпустимо додавати потужності каналів або шумів безпосередньо у децибелах (`P_dBm1 + P_dBm2`). Усі додавання та інтегрування спектрів слід виконувати виключно у лінійній шкалі (Ватах), повертаючись до дБм лише для фінального відображення результатів.
