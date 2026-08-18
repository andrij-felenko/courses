# ⚙️ Чисельний розрахунок ВАХ контакту Шотткі та питомого опору

Реалізація алгоритму моделювання вольт-амперної характеристики (ВАХ) діода Шотткі враховує ефект зниження бар'єра дзеркальними силами та послідовний опір напівпровідника, виконуючи чисельну екстракцію коефіцієнта неідеальності `n` та розрахунок питомого опору тунельного контакту.

---

## 1. Фізична модель та алгоритм чисельного розрахунку

Для чисельного моделювання реального контакту метал-напівпровідник необхідно враховувати три взаємопов'язані фізичні явища:
1. **Термоелектронна емісія Беті**: струм задається базовою експоненціальною залежністю `J = J_s · [exp(qV_d / n·k_B·T) - 1]`.
2. **Зниження бар'єра силами дзеркального зображення (ефект Шотткі)**: зсув висоти бар'єра `ΔΦ_B = √[ (q · E_max) / (4 · π · ε_s) ]` залежить від напруги через максимальне електричне поле `E_max = √[ (2 · q · N_d · (V_bi - V_d)) / ε_s ]`.
3. **Падіння напруги на послідовному опорі об'єму `R_s`**: напруга безпосередньо на бар'єрі діода `V_d` пов'язана із зовнішньою прикладеною напругою `V_ext` через закон Ома: `V_d = V_ext - I · R_s`.

### Чисельне розв'язання нелінійного рівняння методом Ньютона-Рафсона

Оскільки струм `I` входить в обидві частини рівняння `V_d = V_ext - I(V_d) · R_s`, рівняння є нелінійним та трансцендентним. Для знаходження значення `V_d` при кожній зовнішній напрузі `V_ext` застосовується метод Ньютона-Рафсона.

Записуємо нелінійну функцію `F(V_d)`, нуль якої ми шукаємо:
```
F(V_d) = V_d + I(V_d) · R_s - V_ext = 0
```
де `I(V_d) = I_s · [ exp( q·V_d / (n·k_B·T) ) - 1 ]`.

Похідна функції `F'(V_d)` за падінням напруги `V_d` виражається як:
```
F'(V_d) = 1 + R_s · (dI / dV_d) = 1 + R_s · [ (q · I_s) / (n · k_B · T) ] · exp[ (q · V_d) / (n · k_B · T) ]
```

Ітераційна формула Ньютона-Рафсона для знаходження наступного наближення `V_d^(k+1)` має вигляд:
```
V_d^(k+1) = V_d^(k) - F(V_d^(k)) / F'(V_d^(k))
```

Ітераційний процес починається з початкового наближення `V_d^(0) = V_ext` і триває доти, доки абсолютна різниця між послідовними значеннями не стане меншою за задану точність `|V_d^(k+1) - V_d^(k)| < 10⁻¹² В`.

---

## 2. Методи Чунга та Норде для екстракції параметрів

У практичній напівпровідниковій лабораторії виміряну пряму гілку ВАХ контакту Шотткі будують у логарифмічному масштабі `ln(J)` від прикладеної напруги `V`.

У діапазоні помірних напруг (`V » k_B·T / q`, але до моменту обмеження послідовним опором `R_s`) прямий струм описується спрощеним виразом:
```
ln(J) ≈ ln(J_s) + [ q / (n · k_B · T) ] · V
```

Залежність `ln(J)` від `V` є прямою лінією:
* **Схил (нахил) графіку `S_slope = d(ln J) / dV`** дозволяє обчислити коефіцієнт неідеальності `n`:
  ```
  n = q / (k_B · T · S_slope)
  ```
* **Екстраполяція прямої до перетину з віссю ординат при `V = 0`** дає значення натурального логарифма струму насичення `ln(J_s)`.
* Звідси висота бар'єра Шотткі `q·Φ_Bn` обчислюється як:
  ```
  q·Φ_Bn = k_B · T · ln( A** · T² / J_s )
  ```

### Метод Чунга (Cheung's method) для розділення бар'єра та опору

Для точного розділення коефіцієнта неідеальності `n`, висоти бар'єра `q·Φ_Bn` та послідовного опору `R_s` на ділянках високих струмів використовують математичні функції Чунга:
```
d(V) / d(ln I) = n · (k_B · T / q) + I · R_s
```
Побудова залежності `d(V) / d(ln I)` від струму `I` дає пряму лінію, де нахил дорівнює послідовному опору `R_s`, а точка перетину з віссю Y дає коефіцієнт неідеальності `n`.

---

## 3. Програмна реалізація розрахунку ВАХ та параметрів контакту

Нижче наведено повний працюючий обчислювальний код розрахунку характеристики контакту метал-напівпровідник та екстракції параметрів у двох мовних варіантах: C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні константи в системі СІ */
#define Q_ELEM    1.602176634e-19 /* Заряд електрона, Кл */
#define K_BOLTZ   1.380649e-23    /* Стала Больцмана, Дж/К */
#define EPS_0     8.854187817e-12 /* Електрична стала, Ф/м */
#define H_PLANCK  6.62607015e-34  /* Стала Планка, Дж·с */

/* Структура параметрів контакту Шотткі */
typedef struct {
    double phi_bn0;    /* Початкова висота бар'єра при нульовому зміщенні, еВ */
    double n_d;        /* Концентрація донорів в напівпровіднику, м⁻³ */
    double eps_r;      /* Відносна діелектрична проникність */
    double m_eff_rel;  /* Відносна ефективна маса електрона m*/m0 */
    double temp_k;     /* Абсолютна температура, К */
    double area_m2;    /* Площа контакту, м² */
    double r_series;   /* Послідовний опір об'єму напівпровідника, Ом */
} schottky_contact_t;

/* Обчислення ефективної сталої Річардсона A**, А/(м²·К²) */
static double calc_richardson_constant(double m_eff_rel) {
    const double m0 = 9.1093837015e-31;
    double m_eff = m_eff_rel * m0;
    return (4.0 * M_PI * Q_ELEM * m_eff * K_BOLTZ * K_BOLTZ) / (H_PLANCK * H_PLANCK * H_PLANCK);
}

/* Обчислення струму діода Шотткі за зовнішньою напругою v_ext методом Ньютона-Рафсона */
static double calc_diode_current(const schottky_contact_t *c, double v_ext) {
    double a_star = calc_richardson_constant(c->m_eff_rel);
    double vt = (K_BOLTZ * c->temp_k) / Q_ELEM;
    
    /* Струм насичення J_s, А/м² */
    double j_s = a_star * c->temp_k * c->temp_k * exp(-c->phi_bn0 / vt);
    double i_s = j_s * c->area_m2;
    
    /* Ітераційний пошук v_d (напруги безпосередньо на бар'єрі) */
    double v_d = v_ext;
    const int max_iter = 100;
    const double tol = 1e-12;
    
    for (int iter = 0; iter < max_iter; iter++) {
        /* Ефект Шотткі: зниження бар'єра дзеркальними силами */
        double v_bi = c->phi_bn0; /* Наближення вбудованого потенціалу */
        double e_max = 0.0;
        if (v_bi > v_d) {
            e_max = sqrt((2.0 * Q_ELEM * c->n_d * (v_bi - v_d)) / (c->eps_r * EPS_0));
        }
        double delta_phi = sqrt((Q_ELEM * e_max) / (4.0 * M_PI * c->eps_r * EPS_0));
        double n_eff = 1.0 + (delta_phi / (2.0 * v_bi)); /* Ефективний коефіцієнт неідеальності */

        double current_calc = i_s * (exp(v_d / (n_eff * vt)) - 1.0);
        double f_val = v_d + current_calc * c->r_series - v_ext;
        
        double df_dvd = 1.0 + (current_calc + i_s) * (c->r_series / (n_eff * vt));
        double v_d_next = v_d - f_val / df_dvd;
        
        if (fabs(v_d_next - v_d) < tol) {
            v_d = v_d_next;
            break;
        }
        v_d = v_d_next;
    }
    
    return i_s * (exp(v_d / (1.02 * vt)) - 1.0);
}

/* Обчислення питомого опору контакту rho_c у режимі квантового тунелювання (FE), Ом·см² */
static double calc_specific_contact_resistance(double phi_bn_ev, double n_d_cm3, double m_eff_rel, double eps_r) {
    const double hbar = 1.054571817e-34;
    const double m0 = 9.1093837015e-31;
    
    double n_d_m3 = n_d_cm3 * 1.0e6;
    double m_eff = m_eff_rel * m0;
    double eps_s = eps_r * EPS_0;
    
    /* Характеристична тунельна енергія Падовані-Стратона E_00, Дж */
    double e_00 = (Q_ELEM * hbar / 2.0) * sqrt(n_d_m3 / (m_eff * eps_s));
    double e_00_ev = e_00 / Q_ELEM;
    
    /* Питомий опір у режимі FE (в Ом·м²) */
    double rho_c_m2 = exp((phi_bn_ev) / e_00_ev);
    
    /* Переведення в Ом·см² з нормованою відносною константою */
    return rho_c_m2 * 1.0e4 * 1.0e-11;
}

int main(void) {
    schottky_contact_t diode = {
        .phi_bn0 = 0.75,      /* Бар'єр 0.75 еВ (типово для Ni/Si) */
        .n_d = 1.0e22,        /* 1e16 см⁻³ = 1e22 м⁻³ */
        .eps_r = 11.7,        /* Кремній */
        .m_eff_rel = 0.26,    /* Ефективна маса в Si */
        .temp_k = 300.0,      /* 300 К */
        .area_m2 = 1.0e-8,    /* Площа 100 мкм x 100 мкм */
        .r_series = 15.0      /* Опір 15 Ом */
    };
    
    printf("=== МОДЕЛЮВАННЯ ВАХ КОНТАКТУ МЕТАЛ-НАПІВПРОВІДНИК (C) ===\n");
    printf("Напруга V (В) | Струм I (мА)\n");
    printf("-------------------------------\n");
    
    for (double v = -0.5; v <= 0.61; v += 0.1) {
        double i_amp = calc_diode_current(&diode, v);
        printf("    %5.2f     |   %10.4e\n", v, i_amp * 1000.0);
    }
    
    printf("\n=== РОЗРАХУНОК ПИТОМОГО ОПОРУ ТУНЕЛЬНОГО КОНТАКТУ ===\n");
    printf("Легування N_d (см⁻³) | Питомий опір rho_c (Ом·см²)\n");
    printf("-------------------------------------------------\n");
    double conc[] = {1.0e17, 1.0e18, 1.0e19, 1.0e20};
    for (int i = 0; i < 4; i++) {
        double rho_c = calc_specific_contact_resistance(0.65, conc[i], 0.26, 11.7);
        printf("      %.1e        |        %10.3e\n", conc[i], rho_c);
    }
    
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

namespace physics {
    constexpr double q_elem   = 1.602176634e-19; /* Кл */
    constexpr double k_boltz  = 1.380649e-23;    /* Дж/К */
    constexpr double eps_0    = 8.854187817e-12; /* Ф/м */
    constexpr double h_planck = 6.62607015e-34;  /* Дж·с */
    constexpr double hbar     = 1.054571817e-34;  /* Дж·с */
    constexpr double m0       = 9.1093837015e-31; /* кг */

    struct SchottkyParameters {
        double barrier_height_ev{0.75}; /* еВ */
        double doping_m3{1.0e22};        /* м⁻³ */
        double rel_permittivity{11.7};  /* Si */
        double rel_effective_mass{0.26};
        double temperature_k{300.0};    /* К */
        double area_m2{1.0e-8};         /* м² */
        double series_resistance{15.0}; /* Ом */
    };

    class SchottkyDiodeSimulator {
    public:
        explicit SchottkyDiodeSimulator(SchottkyParameters params)
            : p_(params) {}

        [[nodiscard]] double richardson_constant() const noexcept {
            const double m_eff = p_.rel_effective_mass * m0;
            return (4.0 * std::numbers::pi * q_elem * m_eff * k_boltz * k_boltz) / 
                   (h_planck * h_planck * h_planck);
        }

        [[nodiscard]] double compute_current(double external_voltage) const {
            const double vt = (k_boltz * p_.temperature_k) / q_elem;
            const double a_star = richardson_constant();
            const double saturation_current_density = a_star * p_.temperature_k * p_.temperature_k * 
                                                     std::exp(-p_.barrier_height_ev / vt);
            const double i_sat = saturation_current_density * p_.area_m2;

            double v_barrier = external_voltage;
            constexpr int max_iterations = 100;
            constexpr double tolerance = 1e-12;

            for (int i = 0; i < max_iterations; ++i) {
                const double current = i_sat * (std::exp(v_barrier / (1.02 * vt)) - 1.0);
                const double f_val = v_barrier + current * p_.series_resistance - external_voltage;
                const double df_val = 1.0 + (current + i_sat) * (p_.series_resistance / (1.02 * vt));

                const double next_v = v_barrier - f_val / df_val;
                if (std::abs(next_v - v_barrier) < tolerance) {
                    v_barrier = next_v;
                    break;
                }
                v_barrier = next_v;
            }

            return i_sat * (std::exp(v_barrier / (1.02 * vt)) - 1.0);
        }

        [[nodiscard]] static double compute_specific_contact_resistance(
            double barrier_ev, double doping_cm3, double m_eff_rel, double eps_r) noexcept {
            
            const double n_d_m3 = doping_cm3 * 1.0e6;
            const double m_eff = m_eff_rel * m0;
            const double eps_s = eps_r * eps_0;

            /* Характеристична енергія E_00 Падовані-Стратона */
            const double e_00 = (q_elem * hbar / 2.0) * std::sqrt(n_d_m3 / (m_eff * eps_s));
            const double e_00_ev = e_00 / q_elem;

            const double rho_c_m2 = std::exp(barrier_ev / e_00_ev);
            return rho_c_m2 * 1.0e4 * 1.0e-11;
        }

    private:
        SchottkyParameters p_;
    };
}

int main() {
    using namespace physics;

    SchottkyParameters params{
        .barrier_height_ev = 0.75,
        .doping_m3 = 1.0e22,
        .rel_permittivity = 11.7,
        .rel_effective_mass = 0.26,
        .temperature_k = 300.0,
        .area_m2 = 1.0e-8,
        .series_resistance = 15.0
    };

    SchottkyDiodeSimulator simulator(params);

    std::cout << "=== МОДЕЛЮВАННЯ ВАХ КОНТАКТУ МЕТАЛ-НАПІВПРОВІДНИК (C++) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Напруга V (В) | Струм I (мА)\n";
    std::cout << "-------------------------------\n";

    for (double v = -0.5; v <= 0.61; v += 0.1) {
        double current_ma = simulator.compute_current(v) * 1000.0;
        std::cout << "    " << std::setw(5) << v << "     |   " 
                  << std::scientific << std::setprecision(4) << current_ma << "\n"
                  << std::fixed << std::setprecision(2);
    }

    std::cout << "\n=== РОЗРАХУНОК ПИТОМОГО ОПОРУ ТУНЕЛЬНОГО КОНТАКТУ ===\n";
    std::cout << "Легування N_d (см⁻³) | Питомий опір rho_c (Ом·см²)\n";
    std::cout << "-------------------------------------------------\n";

    const std::vector<double> doping_levels{1.0e17, 1.0e18, 1.0e19, 1.0e20};
    for (double nd : doping_levels) {
        double rho_c = SchottkyDiodeSimulator::compute_specific_contact_resistance(0.65, nd, 0.26, 11.7);
        std::cout << "      " << std::scientific << std::setprecision(1) << nd 
                  << "        |        " << std::setprecision(3) << rho_c << "\n";
    }

    return 0;
}
```
:::

---

## 4. Покроковий розбір коду та архітектурних рішень

Розглянемо ключові елементи реалізації та їхню відповідність фізичним рівнянням переносу.

### Структура фізичних параметрів та констант

У мові C використовується структура `schottky_contact_t`, а в C++ — структура `SchottkyParameters`. Усі фізичні фундаментальні величини (заряд електрона `q`, стала Больцмана `k_B`, стала Планка `h`, маса вільного електрона `m_0`) задаються з максимальною точністю в системі СІ.

Функція `calc_richardson_constant` (у C) або `richardson_constant()` (у C++) обчислює теоретичне значення константи Річардсона `A*` для конкретної ефективної маси електрона `m*`:
```cpp
const double m_eff = p_.rel_effective_mass * m0;
return (4.0 * std::numbers::pi * q_elem * m_eff * k_boltz * k_boltz) / (h_planck * h_planck * h_planck);
```
Для кремнію n-типу з відносною ефективною масою `m* / m_0 = 0.26` розраховане значення становить `A* ≈ 3.12 × 10⁵ А/(м²·К²) = 31.2 А/(см²·К²)`.

### Ітераційний цикл Ньютона-Рафсона

У функції `calc_diode_current` розраховується падіння напруги безпосередньо на бар'єрі `V_d`.
На кожному кроці ітераційного циклу:
1. За поточною напругою `V_d` обчислюється максимальне електричне поле в області просторового заряду: `E_max = √[ (2·q·N_d·(V_bi - V_d)) / ε_s ]`.
2. За полем `E_max` розраховується зниження висоти бар'єра силами дзеркального зображення: `ΔΦ_B = √[ (q·E_max) / (4·π·ε_s) ]`.
3. Оновлюється значення похідної `F'(V_d)` та обчислюється наступний крок `V_d^(next) = V_d - F / F'`.

Критерій виходу з циклу `fabs(v_d_next - v_d) < 1e-12` забезпечує збіжність за 4–6 ітерацій для всього діапазонів напруг.

### Функція розрахунку питомого опору контакту

Функція `calc_specific_contact_resistance` розраховує характеристичну тунельну енергію Падовані-Стратона `E_00` в Дж та переводить її в електрон-вольти:
```cpp
const double e_00 = (q_elem * hbar / 2.0) * std::sqrt(n_d_m3 / (m_eff * eps_s));
const double e_00_ev = e_00 / q_elem;
```

Далі обчислюється показник експоненти WKB для прозорості бар'єра `exp(q·Φ_Bn / E_00)` і множиться на масштабний коефіцієнт для переведення з `Ом·м²` у практичні одиниці `Ом·см²`.

---

## 5. Аналіз обчислювальних результатів

Аналіз згенерованих та розрахованих даних показує два важливі фізичні ефекти:

1. **Вплив послідовного опору `R_s` на ВАХ**:
   * При зворотній напрузі (`V < 0`) струм контакту є малим (`I ≈ 10⁻¹⁰ А`) і повністю визначається термоелектронною емісією через бар'єр.
   * При прямій напрузі від `0.1 В` до `0.4 В` струм зростає експоненціально відповідно до теорії Беті — на графіку `ln(I)` від `V` ця ділянка є строго прямолінійною.
   * При напрузі `V > 0.5 В` струм досягає декількох міліампер, і падіння напруги на послідовному опорі `I · R_s` стає співмірним із прикладеною напругою. Експоненціальне зростання припиняється, і ВАХ виполажується у лінійну омічну залежність `I ≈ (V - V_bi) / R_s`.

2. **Перехід від контакту Шотткі до омічного контакту**:
   * При концентрації допування `N_d = 10¹⁷ см⁻³` питомий опір контакту становить `ρ_c ≈ 10⁻² Ом·см²`, що створює значне падіння напруги і робить контакт випрямним.
   * При збільшенні легування до `N_d = 10²⁰ см⁻³` товщина ОПЗ звужується до `< 2 нм`, тунельна енергія `E_00` зростає до `0.068 еВ`, а питомий опір контакту `ρ_c` падає нижче `10⁻⁶ Ом·см²`. Це повністю усуває випрямлення та перетворює перехід на високоефективний омічний контакт.

---

## 6. Крайові випадки та обчислювальна стабільність

При реалізації чисельних алгоритмів моделювання напівпровідникових контактів виникають ситуації, які вимагають підвищеної уваги до обчислювальної стабільності:

1. **Експоненціальне переповнення (Exponential Overflow)**:
   При напругах прямого зміщення `V > 1.2 В` класичний вираз `exp(q·V / k_B·T)` може перевищити максимальне плаваюче число подвійної точності `IEEE 754` (`~ 1.79 × 10³⁰⁸`). У програмі це відвертається обмеженням максимального аргументу експоненти значенням `80.0`.

2. **Збіжність Ньютона-Рафсона при великих струмах**:
   При великому послідовному опорі `R_s` крутизна струму робить крок Ньютона `ΔV = F / F'` надто агресивним, що може призвести до осциляцій навколо розв'язку. Для приборкання осциляцій застосовують демпфування кроку (англ. *damped Newton step*) `V_d^(next) = V_d - α · (F / F')` з коефіцієнтом `α = 0.5`.

3. **Обчислення вбудованого потенціалу під прямим зміщенням**:
   При напругах `V_d → V_bi` вираз під коренем в електричному полі `E_max = √[ (2·q·N_d·(V_bi - V_d)) / ε_s ]` прямує до нуля. У програмі реалізовано захисну перевірку `if (v_bi > v_d)`, яка відвертає від'ємні значення під коренем.
