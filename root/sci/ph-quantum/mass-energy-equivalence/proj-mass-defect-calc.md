# ⚙️ Обчислення дефекту маси, енергії зв'язку та кінематики ядерних реакцій

Практичне застосування співвідношення еквівалентності маси та енергії `E = m·c²` в ядерній фізиці, астрофізиці та фізиці високих енергій вимагає суворого чисельного аналізу дефекту маси, питомої енергії зв'язку нуклонів у ядрах та енергетичного виходу (Q-значення) ядерних реакцій. Створення спеціалізованого обчислювального інструменту дозволяє моделювати енергетичні баланси екзотермічних і ендотермічних реакцій (таких як термоядерний синтез дейтерію й тритію чи поділ урану-235), а також розраховувати порогові енергії народження нових елементарних частинок у релятивістських зіткненнях.

Цей документ містить повний математичний опис алгоритмів, аналіз фундаментальних фізичних констант, розбір крайових випадків чисельної точності та працездатні реалізації мовами C та C++ для інженерного використання.

## Теоретичні основи та системи одиниць вимірювання

При обчисленні енергетичних параметрів атомних ядер і ядерних реакцій стандартні одиниці системи SI (кілограми та джоулі) є незручними через надзвичайно малі значення вимірюваних величин. У ядерній фізиці використовується позасистемна одиниця маси — атомна одиниця маси (а. о. м. або `u`), яка визначається як точна `1/12` частина маси нейтрального атома вуглецю-12 (`¹²C`).

Один електронвольт (`еВ`) відповідає енергії, яку набуває один електрон при проходженні різниці потенціалів у 1 вольт. У ядерній фізиці зазвичай оперують мегаелектронвольтами (`1 МеВ = 10⁶ еВ = 1.602176634 × 10⁻¹³ Дж`).

Фундаментальні фізичні константи (згідно зі стандартами CODATA 2018):
- Швидкість світла у вакуумі: `c = 299 792 458 м/с`.
- Атомна одиниця маси у кілограмах: `1 u = 1.66053906660 × 10⁻²⁷ кг`.
- Енергетичний еквівалент 1 а. о. м.: `1 u · c² = 931.494102 МеВ`.
- Елементарний електричний заряд: `e = 1.602176634 × 10⁻¹⁹ Кл`.
- Маса вільного протона: `m_p = 1.007276466621 u = 938.272088 МеВ/c²`.
- Маса вільного нейтрона: `m_n = 1.00866491595 u = 939.565420 МеВ/c²`.
- Маса вільного електрона: `m_e = 0.000548579909 u = 0.510998950 МеВ/c²`.

### 1. Алгоритм розрахунку дефекту маси та енергії зв'язку ядра

Для довільного ядра з атомним номером `Z` (кількість протонів) та масовим числом `A` (сумарна кількість нуклонів) кількість нейтронів дорівнює `N = A - Z`. 

Дефект маси `Δm` обчислюється як різниця між сумарною масою всіх вільних нуклонів у незв'язаному стані та виміряною експериментальною масою зв'язаного ядра `m_nucleus`:

```
Δm = Z · m_p + (A - Z) · m_n - m_nucleus     [дефект маси ядра]
```

Оскільки виміряні значення у таблицях атомних мас (наприклад AME2020) зазвичай наводяться для нейтральних атомів `m_atom`, а не для голих ядер `m_nucleus`, вираз модифікується з урахуванням `Z` електронів:

```
Δm = Z · m_H + (A - Z) · m_n - m_atom        [дефект маси через маси нейтральних атомів]
```

де `m_H = 1.007825032 u` — маса нейтрального атома водню-1 (`¹H`). Помилка від неврахування енергії зв'язку електронів з ядром не перевищує кількох електронвольт, що для ядерних розрахунків є нехтовно малим.

Повна енергія зв'язку ядра `E_b` являє собою енергію, яку потрібно передати ядру ззовні для його розщеплення на окремі складові нуклони:

```
E_b = Δm (в u) · 931.494102 МеВ              [повна енергія зв'язку]
```

Питома енергія зв'язку на один нуклон `ε = E_b / A` слугує головним мірилом стійкості ядра проти ядерного розпаду чи трансмутації:

```
ε = E_b / A                                 [питома енергія зв'язку на нуклон]
```

### 2. Алгоритм розрахунку енергетичного виходу ядерних реакцій (Q-значення)

Розглядаємо ядерну реакцію у загальному вигляді:

```
R₁ + R₂ + ... → P₁ + P₂ + ...               [схема ядерної реакції]
```

де `R_i` — вхідні реагенти (ядра чи частинки), а `P_j` — утворені продукти реакції.

Енергетичний вихід (Q-значення) обчислюється як різниця сумарних мас реагентів до реакції та сумарних мас продуктів після реакції:

```
M_in = ∑ m(R_i)                              [сумарна початкова маса]
M_out = ∑ m(P_j)                             [сумарна кінцева маса]
Δm_reaction = M_in - M_out                  [зміна маси у реакції]
Q = Δm_reaction · 931.494102 МеВ            [Q-значення реакції]
```

Аналіз режимів перебігу реакції:
- **Екзотермічна реакція (`Q > 0`):** Початкова маса реагентів більша за кінцеву масу продуктів (`M_in > M_out`). Надлишок маси `Δm_reaction` вивільняється у формі кінетичної енергії розльоту продуктів або у формі гамма-квантів.
- **Ендотермічна реакція (`Q < 0`):** Початкова маса реагентів менша за кінцеву масу продуктів (`M_in < M_out`). Реакція принципово не може відбутися у стані спокою. Вона вимагає підведення зовнішньої кінетичної енергії від набігаючої частинки.

У разі ендотермічної реакції порогова кінетична енергія набігаючої частинки `E_threshold` у лабораторній системі відліку (де ядро-мішень масою `M_target` початково нерухоме) дорівнює:

```
E_threshold = |Q| · (1 + m_projectile / M_target)    [порогова енергія реакції]
```

Цей додатковий множник `(1 + m_projectile / M_target)` виникає через необхідність виконання закону збереження імпульсу: частина кінетичної енергії набігаючої частинки неминуче витрачається на поступальний рух центру мас всієї системи і не може бути використана на перетворення мас.

## Програмна реалізація мовами C та C++

Нижче наведено модульні реалізації обчислювального алгоритму з повним контролем помилок, валідацією вхідних даних та форматованим виведенням результатів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

/* Фізичні фундаментальні константи (CODATA 2018) */
#define AMU_TO_KG 1.66053906660e-27
#define AMU_TO_MEV 931.494102
#define SPEED_OF_LIGHT 299792458.0
#define PROTON_MASS_AMU 1.007276466621
#define NEUTRON_MASS_AMU 1.00866491595
#define HYDROGEN1_MASS_AMU 1.00782503207
#define ELECTRON_MASS_AMU 0.000548579909

/* Структура для опису атомного ядра */
typedef struct {
    const char* symbol;  /* Хімічний символ ядра */
    int Z;              /* Кількість протонів (заряд) */
    int A;              /* Масове число (протони + нейтрони) */
    double mass_amu;    /* Маса нейтрального атома у а. о. м. */
} Nucleus;

/* Результати розрахунку енергії зв'язку */
typedef struct {
    double mass_defect_amu;
    double mass_defect_kg;
    double binding_energy_mev;
    double binding_energy_joules;
    double binding_energy_per_nucleon_mev;
} BindingEnergyResult;

/* Структура для опису компонента реакції */
typedef struct {
    const char* name;
    double mass_amu;
    int count;
} ReactionComponent;

/* Обчислення дефекту маси та енергії зв'язку ядра */
bool calculate_binding_energy(const Nucleus* n, BindingEnergyResult* res) {
    if (!n || !res || n->Z <= 0 || n->A < n->Z || n->mass_amu <= 0.0) {
        return false;
    }
    
    int N = n->A - n->Z;
    /* Використовуємо маси атома водню-1 для точного урахування електронів */
    double sum_free_components = n->Z * HYDROGEN1_MASS_AMU + N * NEUTRON_MASS_AMU;
    
    res->mass_defect_amu = sum_free_components - n->mass_amu;
    if (res->mass_defect_amu < 0.0) {
        return false; /* Нестабільний стан / помилка даних */
    }
    
    res->mass_defect_kg = res->mass_defect_amu * AMU_TO_KG;
    res->binding_energy_mev = res->mass_defect_amu * AMU_TO_MEV;
    res->binding_energy_joules = res->mass_defect_kg * SPEED_OF_LIGHT * SPEED_OF_LIGHT;
    res->binding_energy_per_nucleon_mev = res->binding_energy_mev / n->A;
    
    return true;
}

/* Обчислення Q-значення та порогової енергії для ядерної реакції */
bool analyze_reaction(const ReactionComponent reactants[], size_t num_reactants,
                      const ReactionComponent products[], size_t num_products,
                      double* q_value_mev, double* threshold_mev) {
    if (!reactants || !products || num_reactants == 0 || num_products == 0 || !q_value_mev) {
        return false;
    }
    
    double m_in = 0.0;
    for (size_t i = 0; i < num_reactants; ++i) {
        if (reactants[i].mass_amu <= 0.0 || reactants[i].count <= 0) return false;
        m_in += reactants[i].mass_amu * reactants[i].count;
    }
    
    double m_out = 0.0;
    for (size_t j = 0; j < num_products; ++j) {
        if (products[j].mass_amu <= 0.0 || products[j].count <= 0) return false;
        m_out += products[j].mass_amu * products[j].count;
    }
    
    double delta_m = m_in - m_out;
    *q_value_mev = delta_m * AMU_TO_MEV;
    
    if (threshold_mev) {
        if (*q_value_mev < 0.0 && num_reactants >= 2) {
            /* Поріг для ендотермічної реакції: E_th = |Q| * (1 + m_proj / M_target) */
            double m_proj = reactants[0].mass_amu;
            double m_target = reactants[1].mass_amu;
            *threshold_mev = fabs(*q_value_mev) * (1.0 + m_proj / m_target);
        } else {
            *threshold_mev = 0.0; /* Екзотермічна реакція не має кінематичного порогу */
        }
    }
    
    return true;
}

int main(void) {
    printf("=====================================================\n");
    printf("  ЯДЕРНИЙ КАЛЬКУЛЯТОР ДЕФЕКТУ МАСИ ТА РЕАКЦІЙ (C)\n");
    printf("=====================================================\n\n");
    
    /* 1. Розрахунок енергії зв'язку ядра Гелію-4 (4He) */
    Nucleus he4 = {"4He", 2, 4, 4.002603}; /* Маса атома 4He */
    BindingEnergyResult res_he4;
    
    if (calculate_binding_energy(&he4, &res_he4)) {
        printf("--- Аналіз ядра %s ---\n", he4.symbol);
        printf("  Протонів Z:     %d, Нейтронів N: %d\n", he4.Z, he4.A - he4.Z);
        printf("  Дефект маси:   %.6f u (%.6e кг)\n", res_he4.mass_defect_amu, res_he4.mass_defect_kg);
        printf("  Енергія зв'язку: %.3f МеВ (%.6e Дж)\n", res_he4.binding_energy_mev, res_he4.binding_energy_joules);
        printf("  Питома енергія:  %.3f МеВ/нуклон\n\n", res_he4.binding_energy_per_nucleon_mev);
    }
    
    /* 2. Аналіз реакції термоядерного синтезу: 2H + 3H -> 4He + n */
    ReactionComponent reactants[] = {
        {"Deuterium (2H)", 2.014102, 1},
        {"Tritium (3H)", 3.016049, 1}
    };
    
    ReactionComponent products[] = {
        {"Helium-4 (4He)", 4.001506, 1},
        {"Neutron (n)", 1.008665, 1}
    };
    
    double q_val = 0.0, e_th = 0.0;
    if (analyze_reaction(reactants, 2, products, 2, &q_val, &e_th)) {
        printf("--- Реакція синтезу D + T -> 4He + n ---\n");
        printf("  Q-значення реакції: %+.3f МеВ\n", q_val);
        if (q_val > 0.0) {
            printf("  Режим: Екзотермічний (виділення %.3f МеВ кінетичної енергії)\n", q_val);
        } else {
            printf("  Режим: Ендотермічний (порогова енергія: %.3f МеВ)\n", e_th);
        }
    }
    
    return 0;
}
```

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <iomanip>
#include <cmath>

namespace physics::nuclear {

/* Фізичні константи */
constexpr double AMU_TO_KG = 1.66053906660e-27;
constexpr double AMU_TO_MEV = 931.494102;
constexpr double SPEED_OF_LIGHT = 299792458.0;
constexpr double HYDROGEN1_MASS_AMU = 1.00782503207;
constexpr double NEUTRON_MASS_AMU = 1.00866491595;

struct NucleusSpec {
    std::string symbol;
    int Z{0};
    int A{0};
    double mass_amu{0.0};
};

struct BindingEnergyReport {
    double mass_defect_amu{0.0};
    double mass_defect_kg{0.0};
    double binding_energy_mev{0.0};
    double binding_energy_joules{0.0};
    double binding_energy_per_nucleon_mev{0.0};
};

struct ParticleSpec {
    std::string name;
    double mass_amu{0.0};
    int count{1};
};

struct ReactionAnalysisReport {
    double q_value_mev{0.0};
    double threshold_energy_mev{0.0};
    bool is_exothermic{true};
};

class NuclearPhysicsEngine {
public:
    static std::optional<BindingEnergyReport> compute_binding_energy(const NucleusSpec& spec) {
        if (spec.Z <= 0 || spec.A < spec.Z || spec.mass_amu <= 0.0) {
            return std::nullopt;
        }

        const int N = spec.A - spec.Z;
        const double sum_free = spec.Z * HYDROGEN1_MASS_AMU + N * NEUTRON_MASS_AMU;
        const double defect_amu = sum_free - spec.mass_amu;

        if (defect_amu < 0.0) {
            return std::nullopt;
        }

        BindingEnergyReport report;
        report.mass_defect_amu = defect_amu;
        report.mass_defect_kg = defect_amu * AMU_TO_KG;
        report.binding_energy_mev = defect_amu * AMU_TO_MEV;
        report.binding_energy_joules = report.mass_defect_kg * SPEED_OF_LIGHT * SPEED_OF_LIGHT;
        report.binding_energy_per_nucleon_mev = report.binding_energy_mev / spec.A;

        return report;
    }

    static std::optional<ReactionAnalysisReport> analyze_reaction(
        const std::vector<ParticleSpec>& reactants,
        const std::vector<ParticleSpec>& products) {
        
        if (reactants.empty() || products.empty()) {
            return std::nullopt;
        }

        double m_in = 0.0;
        for (const auto& r : reactants) {
            if (r.mass_amu <= 0.0 || r.count <= 0) return std::nullopt;
            m_in += r.mass_amu * r.count;
        }

        double m_out = 0.0;
        for (const auto& p : products) {
            if (p.mass_amu <= 0.0 || p.count <= 0) return std::nullopt;
            m_out += p.mass_amu * p.count;
        }

        const double delta_m = m_in - m_out;
        ReactionAnalysisReport report;
        report.q_value_mev = delta_m * AMU_TO_MEV;
        report.is_exothermic = (report.q_value_mev >= 0.0);

        if (!report.is_exothermic && reactants.size() >= 2) {
            const double m_proj = reactants[0].mass_amu;
            const double m_target = reactants[1].mass_amu;
            report.threshold_energy_mev = std::abs(report.q_value_mev) * (1.0 + m_proj / m_target);
        } else {
            report.threshold_energy_mev = 0.0;
        }

        return report;
    }
};

} // namespace physics::nuclear

int main() {
    using namespace physics::nuclear;

    std::cout << "=====================================================\n"
              << "  ЯДЕРНИЙ КАЛЬКУЛЯТОР ДЕФЕКТУ МАСИ ТА РЕАКЦІЙ (C++)\n"
              << "=====================================================\n\n";

    /* Аналіз ядра Урану-235 */
    NucleusSpec u235{"235U", 92, 235, 235.043930};
    auto report_u235 = NuclearPhysicsEngine::compute_binding_energy(u235);

    if (report_u235) {
        std::cout << "--- Аналіз ядра " << u235.symbol << " ---\n"
                  << std::fixed << std::setprecision(6)
                  << "  Дефект маси:   " << report_u235->mass_defect_amu << " u (" 
                  << std::scientific << report_u235->mass_defect_kg << " kg)\n"
                  << std::fixed << std::setprecision(3)
                  << "  Енергія зв'язку: " << report_u235->binding_energy_mev << " MeV (" 
                  << std::scientific << report_u235->binding_energy_joules << " J)\n"
                  << std::fixed << std::setprecision(3)
                  << "  Питома енергія:  " << report_u235->binding_energy_per_nucleon_mev << " MeV/nucleon\n\n";
    }

    /* Аналіз виходу реакції поділу урану-235: n + 235U -> 92Kr + 141Ba + 3n */
    std::vector<ParticleSpec> reactants = {
        {"Neutron (n)", 1.008665, 1},
        {"Uranium-235 (235U)", 235.043930, 1}
    };

    std::vector<ParticleSpec> products = {
        {"Krypton-92 (92Kr)", 91.926156, 1},
        {"Barium-141 (141Ba)", 140.914411, 1},
        {"Neutron (n)", 1.008665, 3}
    };

    auto reaction_report = NuclearPhysicsEngine::analyze_reaction(reactants, products);
    if (reaction_report) {
        std::cout << "--- Реакція поділу: n + 235U -> 92Kr + 141Ba + 3n ---\n"
                  << std::fixed << std::setprecision(3)
                  << "  Q-значення реакції: " << reaction_report->q_value_mev << " MeV\n";
        if (reaction_report->is_exothermic) {
            std::cout << "  Режим: Екзотермічний (виділення енергії)\n";
        } else {
            std::cout << "  Режим: Ендотермічний (поріг: " << reaction_report->threshold_energy_mev << " MeV)\n";
        }
    }

    return 0;
}
```
:::

## Аналіз пасток та типових помилок чисельного моделювання

При реалізації програмних інструментів для обчислень еквівалентності маси та енергії у релятивістській та ядерній фізиці виникають три характерні обчислювальні пастки:

1. **Втрата значущих цифр при відніманні близьких величин (Catastrophic Cancellation):**
   При обчисленні дефекту маси `Δm = ∑ m_free - m_bound` ми віднімаємо дві близькі величини, перші 3–4 значущі цифри яких збігаються. Якщо використовувати 32-бітні числа з плаваючою комою `float` (які мають лише 6–7 десяткових знаків точності), мантиса результату втрачає більшість значущих розрядів. Це призводить до похибок обчислення енергії зв'язку на рівні десятків відсотків. Для будь-які релятивістських та ядерних розрахунків обов'язковим є використання 64-бітних чисел подвійної точності `double` (15–17 значущих десяткових цифр).

2. **Неузгодженість масових шкал (Атомна маса проти ядерної):**
   У мас-спектрометрії та міжнародних таблицях (AME2020) наводяться маси **нейтральних атомів**, а не голих атомних ядер. Спроба обчислити дефект маси ядра шляхом віднімання мас вільних протонів `m_p` замість мас атомів водню `m(¹H)` дає систематичну похибку на масу `Z` електронів (`Z · m_e ≈ Z · 0.511 МеВ`). Це спотворює `Q`-значення бета-розпадів та реакцій захоплення електрона.

3. **Нерелятивістський розрахунок порогової енергії:**
   При аналізі ендотермічних реакцій або народження нових частинок (наприклад `p + p → p + p + π⁰`) недопустимо визначати поріг як `E_th = |Q|`. Частина кінетичної енергії набігаючої частинки неминуче іде на збереження імпульсу системи у формі кінетичної енергії руху центру мас. Розрахунок порогу повинен проводитися строго у релятивістській інваріантній формі через інваріантний квадрат маси `s = (p₁ + p₂)²`.
