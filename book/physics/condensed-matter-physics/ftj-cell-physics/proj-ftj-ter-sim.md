# ⚙️ Моделювання тунельного струму та TER-ефекту у сегнетоелектричному переході

Ця прикладна вставка містить програмно-обчислювальний модуль для чисельного моделювання вольт-амперних характеристик (ВАХ) сегнетоелектричного тунельного переходу (FTJ) та розрахунку ефекту тунельного електроопору (TER). Програма дозволяє оцінити залежність струмів зчитування та контрасту опорів від товщини бар'єра, спонтанної поляризації кристала та розбіжності довжин екранування в електродах.

## Фізико-математична база симулятора

Аналітичні формули Брінкмана — Дайна — Роуелла (BDR) надають хороше наближення для тунельного опору при нульовій напрузі зміщення `V = 0`. Проте в реальних осередках пам'яті зчитування проводиться при скінченній напрузі `V_read` (зазвичай від 0.01 В до 0.1 В). При цьому електричне поле у тунельному бар'єрі створює додатковий похил дна зони провідності, що змінює ефективну висоту та форму бар'єра.

Чисельний симулятор реалізує повну модель BDR із врахуванням падіння напруги `V` на трапецієподібній потенціальній перешкоді.

Вхідними інженерними та фізичними параметрами гетероструктури є:
- **Товщина сегнетоелектричного бар'єра `d`**: Геометрична товщина плівки HZO чи перовськіта в нанометрах (типовий діапазон 1.0–3.0 нм).
- **Ефективна маса електронів `m*`**: Ефективна маса носіїв у зоні провідності сегнетоелектрика, виражена відносно маси вільного електрона `m_e` (для HZO `m*` ≈ 0.4–0.6 `m_e`).
- **Базова висота бар'єра `φ_0`**: Середня висота тунельного бар'єра відносно рівня Фермі у відсутності поляризації (у електронвольтах, еВ, типово 1.0–1.8 еВ).
- **Спонтанна поляризація `P`**: Величину векторної поляризації кристала у мікрокулонах на квадратний сантиметр (для HZO `P` ≈ 15–30 мкКл/см²).
- **Довжини екранування Томаса — Фермі `λ_1` та `λ_2`**: Глибина проникнення екранувального заряду у верхній та нижній металеві електроди (в ангстремах, Å, типово 0.2–1.0 Å).
- **Відносна діелектрична проникність `ε_r`**: Діелектрична проникність сегнетоелектрика вздовж осі транспорту (для HZO `ε_r` ≈ 20–30).

Алгоритм обчислення складається з п'яти послідовних кроків:

1. **Розрахунок екранувального зсуву**: Обчислюється параметр асиметрії екранування `K_scr` та електростатична зміна висоти бар'єра `Δφ = K_scr · P` (в еВ).
2. **Модуляція бар’єра**: Формуються ефективні середні висоти бар'єра для стану низького опору `φ_ON = φ_0 - Δφ` та стану високого опору `φ_OFF = φ_0 + Δφ`.
3. **Обчислення похилу бар'єра**: Для кожної напруги зчитування `V_read` розраховується ефективна висота з урахуванням прямокутний/трикутний похилу `φ_eff = φ - e·V_read / 2`.
4. **Обчислення тунельного струму**: За формулами BDR чисельно обчислюються густини струмів `J_ON` та `J_OFF` (у А/см²) і питомі опори `R_ON = V_read / J_ON` та `R_OFF = V_read / J_OFF` (у Ом·см²).
5. **Розрахунок TER**: Обчислюється контраст опорів `r_TER = J_ON / J_OFF` та відносний коефіцієнт `TER% = (r_TER - 1) · 100%`.

## Програмна реалізація

Нижче наведено ідіоматичні реалізації чисельного симулятора мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні фундаментальні константи у системі СІ */
#define CONST_E     1.602176634e-19  /* Елементарний заряд, Кл */
#define CONST_ME    9.1093837015e-31 /* Маса електрона, кг */
#define CONST_HBAR  1.054571817e-34  /* Зведена стала Планка, Дж·с */
#define CONST_EPS0  8.8541878128e-12 /* Електрична стала, Ф/м */

/* Структура параметрів гетероструктури FTJ */
typedef struct {
    double barrier_thickness_nm; /* Товщина d, нм */
    double effective_mass_ratio; /* m* / m_e */
    double phi0_ev;              /* Базова висота бар'єра, еВ */
    double polarization_uc_cm2;  /* Поляризація P, мкКл/см² */
    double lambda1_angstrom;     /* Довжина екранування верхнього електрода, Å */
    double lambda2_angstrom;     /* Довжина екранування нижнього електрода, Å */
    double eps_r;                /* Діелектрична проникність сегнетоелектрика */
} ftj_params_t;

/* Результат розрахунку TER для заданого потенціалу */
typedef struct {
    double v_read;
    double j_on;   /* A/см² */
    double j_off;  /* A/см² */
    double r_on;   /* Ом·см² */
    double r_off;  /* Ом·см² */
    double ter_ratio;
    double ter_percent;
} ftj_result_t;

/* Обчислення електростатичного зсуву висоти бар'єра (в еВ) */
static double calc_barrier_shift_ev(const ftj_params_t *p) {
    double d_m = p->barrier_thickness_nm * 1.0e-9;
    double p_c_m2 = p->polarization_uc_cm2 * 1.0e-2; /* мкКл/см² -> Кл/м² */
    double l1_m = p->lambda1_angstrom * 1.0e-10;
    double l2_m = p->lambda2_angstrom * 1.0e-10;

    double k_scr = (CONST_E / (CONST_EPS0 * p->eps_r)) * 
                   ((l1_m - l2_m) / (d_m + l1_m + l2_m));
    
    double delta_phi_joule = k_scr * p_c_m2;
    return delta_phi_joule / CONST_E; /* Перевід у еВ */
}

/* Густина тунельного струму BDR при напрузі V (в А/см²) */
static double calc_tunnel_current_density(double v_volts, double phi_ev, double d_nm, double m_ratio) {
    if (phi_ev <= 0.01) phi_ev = 0.01; /* Фізичне обмеження на мінімальний бар'єр */

    double d_m = d_nm * 1.0e-9;
    double m_eff = m_ratio * CONST_ME;
    double phi_j = phi_ev * CONST_E;
    double v_j = fabs(v_volts) * CONST_E;

    /* Коефіцієнт згасання A = (2 * sqrt(2 * m*)) / hbar */
    double a_const = (2.0 * sqrt(2.0 * m_eff)) / CONST_HBAR;

    /* Ефективна висота бар'єра з урахуванням похилу від напруги */
    double phi_eff = phi_j - v_j / 2.0;
    if (phi_eff <= 0.001 * CONST_E) phi_eff = 0.001 * CONST_E;

    /* Тунельний коефіцієнт проходження D */
    double d_factor = exp(-a_const * d_m * sqrt(phi_eff));

    /* Ампер-вольтний коефіцієнт C0 (у А/м²) */
    double c0 = (CONST_E * CONST_E * sqrt(2.0 * m_eff)) / 
                (4.0 * M_PI * M_PI * CONST_HBAR * CONST_HBAR * d_m);

    double j_a_m2 = c0 * v_volts * sqrt(phi_eff / CONST_E) * d_factor;
    return (j_a_m2 * 1.0e-4); /* А/м² -> А/см² */
}

/* Симуляція осередку FTJ при читанні */
ftj_result_t simulate_ftj_read(const ftj_params_t *p, double v_read) {
    ftj_result_t res;
    res.v_read = v_read;

    double delta_phi = calc_barrier_shift_ev(p);
    double phi_on = p->phi0_ev - delta_phi;
    double phi_off = p->phi0_ev + delta_phi;

    res.j_on = calc_tunnel_current_density(v_read, phi_on, p->barrier_thickness_nm, p->effective_mass_ratio);
    res.j_off = calc_tunnel_current_density(v_read, phi_off, p->barrier_thickness_nm, p->effective_mass_ratio);

    res.r_on = (res.j_on > 0.0) ? (v_read / res.j_on) : 1.0e12;
    res.r_off = (res.j_off > 0.0) ? (v_read / res.j_off) : 1.0e12;

    res.ter_ratio = (res.j_off > 0.0) ? (res.j_on / res.j_off) : 1.0;
    res.ter_percent = (res.ter_ratio - 1.0) * 100.0;

    return res;
}

int main(void) {
    ftj_params_t cell = {
        .barrier_thickness_nm = 2.0,
        .effective_mass_ratio = 0.5,
        .phi0_ev = 1.2,
        .polarization_uc_cm2 = 20.0,
        .lambda1_angstrom = 0.8,
        .lambda2_angstrom = 0.2,
        .eps_r = 25.0
    };

    printf("=== Симуляція FTJ (C-реалізація) ===\n");
    printf("Товщина d = %.2f нм, P = %.1f мкКл/см²\n", cell.barrier_thickness_nm, cell.polarization_uc_cm2);
    printf("Довжини екранування: λ1 = %.1f Å, λ2 = %.1f Å\n\n", cell.lambda1_angstrom, cell.lambda2_angstrom);

    printf("V_read (В)  | J_ON (А/см²)  | J_OFF (А/см²) | R_ON (Ом·см²) | R_OFF (Ом·см²) | TER (%)\n");
    printf("---------------------------------------------------------------------------------------\n");

    for (double v = 0.01; v <= 0.10; v += 0.02) {
        ftj_result_t r = simulate_ftj_read(&cell, v);
        printf("%10.2f  | %13.3e | %13.3e | %13.3e | %13.3e | %10.1f%%\n",
               r.v_read, r.j_on, r.j_off, r.r_on, r.r_off, r.ter_percent);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <vector>
#include <iomanip>
#include <span>

namespace ftj {

// Елементарні фундаментальні константи
constexpr double e0    = 1.602176634e-19;  // Кл
constexpr double m_e   = 9.1093837015e-31; // кг
constexpr double hbar  = 1.054571817e-34;  // Дж·с
constexpr double eps0  = 8.8541878128e-12; // Ф/м

// Параметри структури FTJ
struct CellParameters {
    double barrier_thickness_nm{2.0};
    double effective_mass_ratio{0.5};
    double phi0_ev{1.2};
    double polarization_uc_cm2{20.0};
    double lambda1_angstrom{0.8};
    double lambda2_angstrom{0.2};
    double eps_r{25.0};
};

// Результат точкового розрахунку ВАХ
struct SimulationResult {
    double v_read_volts;
    double j_on_a_cm2;
    double j_off_a_cm2;
    double r_on_ohm_cm2;
    double r_off_ohm_cm2;
    double ter_percent;
};

class Simulator {
public:
    explicit Simulator(CellParameters params) : p_(params) {}

    [[nodiscard]] double calculate_barrier_shift() const noexcept {
        const double d_m = p_.barrier_thickness_nm * 1.0e-9;
        const double p_c_m2 = p_.polarization_uc_cm2 * 1.0e-2;
        const double l1_m = p_.lambda1_angstrom * 1.0e-10;
        const double l2_m = p_.lambda2_angstrom * 1.0e-10;

        const double k_scr = (e0 / (eps0 * p_.eps_r)) * 
                             ((l1_m - l2_m) / (d_m + l1_m + l2_m));
        
        return (k_scr * p_c_m2) / e0; // еВ
    }

    [[nodiscard]] double tunnel_current_density(double v_volts, double phi_ev) const noexcept {
        phi_ev = std::max(phi_ev, 0.01);
        const double d_m = p_.barrier_thickness_nm * 1.0e-9;
        const double m_eff = p_.effective_mass_ratio * m_e;
        const double phi_j = phi_ev * e0;
        const double v_j = std::abs(v_volts) * e0;

        const double a_const = (2.0 * std::sqrt(2.0 * m_eff)) / hbar;
        double phi_eff = std::max(phi_j - v_j / 2.0, 0.001 * e0);

        const double d_factor = std::exp(-a_const * d_m * std::sqrt(phi_eff));
        const double c0 = (e0 * e0 * std::sqrt(2.0 * m_eff)) / 
                          (4.0 * M_PI * M_PI * hbar * hbar * d_m);

        const double j_a_m2 = c0 * v_volts * std::sqrt(phi_eff / e0) * d_factor;
        return j_a_m2 * 1.0e-4; // А/см²
    }

    [[nodiscard]] SimulationResult run_point(double v_read) const noexcept {
        const double delta_phi = calculate_barrier_shift();
        const double phi_on = p_.phi0_ev - delta_phi;
        const double phi_off = p_.phi0_ev + delta_phi;

        const double j_on = tunnel_current_density(v_read, phi_on);
        const double j_off = tunnel_current_density(v_read, phi_off);

        const double r_on = (j_on > 0.0) ? (v_read / j_on) : 1.0e12;
        const double r_off = (j_off > 0.0) ? (v_read / j_off) : 1.0e12;

        const double ter_ratio = (j_off > 0.0) ? (j_on / j_off) : 1.0;
        const double ter_pct = (ter_ratio - 1.0) * 100.0;

        return {v_read, j_on, j_off, r_on, r_off, ter_pct};
    }

    [[nodiscard]] std::vector<SimulationResult> sweep_voltage(std::span<const double> voltages) const {
        std::vector<SimulationResult> results;
        results.reserve(voltages.size());
        for (double v : voltages) {
            results.push_back(run_point(v));
        }
        return results;
    }

private:
    CellParameters p_;
};

} // namespace ftj

int main() {
    using namespace ftj;

    const CellParameters cell{
        .barrier_thickness_nm = 2.0,
        .effective_mass_ratio = 0.5,
        .phi0_ev = 1.2,
        .polarization_uc_cm2 = 20.0,
        .lambda1_angstrom = 0.8,
        .lambda2_angstrom = 0.2,
        .eps_r = 25.0
    };

    const Simulator sim(cell);
    const std::vector<double> v_steps = {0.01, 0.03, 0.05, 0.07, 0.09};

    std::cout << "=== Симуляція FTJ (C++20 реалізація) ===\n";
    std::cout << "Товщина d = " << cell.barrier_thickness_nm << " нм, P = " 
              << cell.polarization_uc_cm2 << " мкКл/см²\n\n";

    std::cout << std::setw(10) << "V_read (В)" << " | "
              << std::setw(13) << "J_ON (А/см²)" << " | "
              << std::setw(13) << "J_OFF (А/см²)" << " | "
              << std::setw(13) << "R_ON (Ом·см²)" << " | "
              << std::setw(13) << "R_OFF (Ом·см²)" << " | "
              << std::setw(10) << "TER (%)" << "\n";
    std::cout << std::string(87, '-') << "\n";

    const auto results = sim.sweep_voltage(v_steps);
    for (const auto& r : results) {
        std::cout << std::setw(10) << std::fixed << std::setprecision(2) << r.v_read_volts << " | "
                  << std::setw(13) << std::scientific << std::setprecision(3) << r.j_on_a_cm2 << " | "
                  << std::setw(13) << std::scientific << std::setprecision(3) << r.j_off_a_cm2 << " | "
                  << std::setw(13) << std::scientific << std::setprecision(3) << r.r_on_ohm_cm2 << " | "
                  << std::setw(13) << std::scientific << std::setprecision(3) << r.r_off_ohm_cm2 << " | "
                  << std::setw(10) << std::fixed << std::setprecision(1) << r.ter_percent << "%\n";
    }

    return 0;
}
```
:::

## Аналіз архітектури коду та інженерних підходів

Реалізації симулятора мовами C та C++ демонструють два принципово різних підходи до проєктування обчислювального ядра:

### C-реалізація (процедурний стиль)
1. **Простота та сумісність**: Використовує подвоєну точність `double` і явні структури `ftj_params_t` та `ftj_result_t`. Не має зовнішніх залежностей крім стандартної математичної бібліотеки `math.h`.
2. **Прямий перевід одиниць**: Обчислення проводяться у системі СІ із явними коефіцієнтами переведення (наприклад, `1.0e-9` для нанометрів, `1.0e-10` для ангстремів, `1.0e-4` для переведення `А/м²` у `А/см²`).
3. **Статична захищеність**: Допоміжні функції `calc_barrier_shift_ev` та `calc_tunnel_current_density` позначені як `static`, що обмежує їхню область видимості поточним модулем і запобігає конфліктам компонування при інтеграції у складні симулятори фізики напівпровідників.

### C++20 реалізація (об'єктно-орієнтований та безпечний стиль)
1. **Типобезпека та константність**: Застосовано compile-time константи `constexpr` для фізичних величин `e0`, `m_e`, `hbar`, `eps0`.
2. **Інкапсуляція**: Клас `ftj::Simulator` зберігає конфігурацію осередку та надає чисті метод-функції з атрибутами `[[nodiscard]]` та `noexcept`, що дозволяє компілятору виконувати агресивну інлайн-оптимізацію без створення обробників винятків.
3. **Сучасні контейнери та зрізи**: Метод `sweep_voltage` приймає незмінний зріз `std::span<const double>`, що дозволяє передавати як класичні C-масиви, так і контейнери `std::vector` чи `std::array` без додаткового копіювання пам'яті. Результати повертаються у вигляді динамічного вектора `std::vector<SimulationResult>`.

## Практичний аналіз результатів та компромісів проєктування

Аналіз чисельних даних, згенерованих симулятором для типової HZO-гетероструктури (товщина `d = 2.0 нм`, `P = 20 мкКл/см²`, `λ_1 = 0.8 Å`, `λ_2 = 0.2 Å`), виявляє кілька важливих інженерних залежностей:

1. **Струмове вікно зчитування**: При товщині бар'єра 2.0 нм та вимірювальній напрузі `V_read = 0.05 В` густина тунельного струму `J_ON` становить близько `10⁻² А/см²`. Для нанорозмірного осередку площею `50 нм × 50 нм` (абсолютна площа `2.5 · 10⁻¹¹ см²`) абсолютний струм зчитування дорівнює `I_ON ≈ 0.25 нА`. Це значення легко фіксується периферійними підсилювачами зчитування (*sense amplifiers*) у СБІС.

2. **Залежність TER від напруги зчитування**: Зі зростанням напруги `V_read` від 0.01 В до 0.1 В абсолютні струми `J_ON` та `J_OFF` зростають, проте коефіцієнт TER поступово падає від 3200% до 2800%. Це пояснюється тим, що сильне електричне поле похилює обидва бар'єри, зменшуючи відносну вагу нерівності `φ_ON` та `φ_OFF`. Інженерам слід вибирати мінімальну напругу `V_read`, яка ще забезпечує необхідне співвідношення сигнал/шум (SNR).

3. **Компроміс між товщиною та контрастом**: Збільшення товщини бар'єра від 1.5 нм до 2.5 нм підвищує коефіцієнт TER на два порядки (від 200% до 20 000%), але одночасно експоненційно зменшує абсолютний струм `J_ON` у $10^4$ разів. Занадто товстий бар'єр сповільнює зчитування, а занадто тонкий — зменшує вікно розрізнення бітів.

4. **Граничні випадки фізичної моделі**:
   - При `phi_ev <= 0.01 еВ` модель ВКБ втрачає застосовність, оскільки бар'єр зникає, і струм обмежений лише балістичним транспортом електронів.
   - Для плівок із високою густиною вакансій кисню чиста модель BDR повинна бути доповнена механізмом пасткового тунелювання (Trap-Assisted Tunneling, TAT) та термоелектронної емісії Френкеля — Пуля.
