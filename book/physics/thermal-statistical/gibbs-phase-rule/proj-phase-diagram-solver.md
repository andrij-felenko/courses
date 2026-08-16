# ⚙️ Чисельний розрахунок ступенів вільності та класифікатор рівноважних станів

Ця проектна вставка містить практичну програмну реалізацію алгоритму обчислення числа незалежних компонентів, ступенів вільності та класифікації термодинамічного стану гетерогенної системи відповідно до правила фаз Гіббса мовами C та C++.

### Архітектура термодинамічних солверів та роль перевірки фазових обмежень

У сучасних програмних комплексах термодинамічного моделювання — таких як Thermo-Calc, FactSage, Cantera, Chemkin та OpenCALPHAD — обчислення фазових рівноваг виконується шляхом чисельної мінімізації сумарної енергії Гіббса системи `G_total` за умов збереження балансу маси елементів.

Процес чисельної мінімізації зазвичай спирається на нелінійні алгоритми оптимізації (наприклад, метод Ньютона — Рафсона з модифікаціями Лагранжа). Проте, якщо користувач або вхідний автоматичний модуль задає термодинамічні умови, які фізично суперечать правилу фаз Гіббса (наприклад, спробу зафіксувати 3 незалежні інтенсивні параметри для однокомпонентного середовища з 3 співіснуючими фазами, де `F = 0`), математична матриця Якобі нелінійної системи вироджується, і ітераційний процес Ньютона — Рафсона розбігається або призводить до ділення на нуль.

Саме тому перед запуском важкого числового оптимізатора завжди виконується **попередній етап фазово-топологічного аналізу** (препроцесинг). Цей легкий модуль перевіряє сумісність термодинамічних параметрів за правилом фаз Гіббса:
1. Визначає число незалежних хімічних компонентів `C = N - R - r`;
2. Обчислює вільні ступені вільності `F = C - P + 2 + m` (або `F' = C - P + 1 + m` для ізобарних умов);
3. Класифікує термодинамічний стан (нонваріантний, моноваріантний, біваріантний, мультиваріантний або фізично неможливий перевизначений стан з `F < 0`);
4. Повертає звіт або блокує запуск нелінійного солвера з видачею зрозумілої помилки користувачу.

### Покроковий розбір алгоритму та структури даних

Для побудови надійного препроцесора необхідно правильно організувати вхідні та вихідні структури даних.

#### Вхідні параметри структури `SystemInput`
- `system_name`: Текстова назва або ідентифікатор досліджуваної термодинамічної системи (наприклад, "Потрійна точка води" чи "Сплав Fe-C").
- `species_count` (`N`): Загальна кількість речовин у системі (молекулярних сполук чи іонів).
- `reactions_count` (`R`): Кількість незалежних хімічних реакцій між сполуками.
- `constraints_count` (`r`): Кількість додаткових співвідношень (електронейтральність розчину, початкове завантаження).
- `phases_count` (`P`): Кількість співіснуючих рівноважних фаз.
- `is_isobaric`: Булевий прапорець зафіксованого зовнішнього тиску (`P = const`). Якщо тиск зафіксовано, кількість вільних інтенсивних змінних зменшується на одиницю.
- `is_isothermal`: Булевий прапорець зафіксованої температури (`T = const`). Якщо температура зафіксована, вільні змінні зменшуються ще на одиницю.
- `external_fields` (`m`): Кількість додаткових зовнішніх інтенсивних полів (наприклад, магнітне чи електричне).

#### Вихідні параметри структури `CalculationResult`
- `independent_components` (`C`): Розрахована кількість незалежних компонентів `C = N - R - r`. Якщо `C < 1`, вхідні дані вважаються некоректними.
- `degrees_of_freedom` (`F`): Підсумкове число ступеней вільності.
- `state_class`: Перелічувальне значення категорії термодинамічного стану.
- `description`: Текстовий описовий рядок українською мовою для логування та виводу інженеру.

### Інтеграція з базами даних CALPHAD та ТDB-файлами

Бази даних термодинамічних властивостей матеріалів (у форматах TDB — *Thermo-Calc DataBase*) містять температурні та концентраційні коефіцієнти поліномів для обчислення мольної енергії Гіббса кожного фазового стану `G_m^α(T, P, x_i)`.

У процесі фазового розрахунку алгоритм спочатку зчитує перелік можливих фаз із TDB-файла. Наприклад, для трикомпонентної системи залізо-хром-нікель (`Fe-Cr-Ni`) база даних може пропонувати 5 потенційних фаз: рідкий розплав (Liquid), феріт (BCC_A2), аустеніт (FCC_A1), сигма-фаза (Sigma) та карбіди.

Модуль правил фаз отримує це число `P = 5` і зіставляє його з `C = 3`. Оскільки за постійного тиску `F' = 3 - 5 + 1 = -1`, солвер миттєво робить висновок: **усі 5 фаз одночасно в рівновазі перебувати не можуть**. Далі чисельний оптимізатор перебирає підмножини співіснуючих фаз із `P ≤ 4`, мінімізуючи спільний дотичний гіперпростір (концепція спільних дотичних — *common tangent construction*) до тих пір, поки `F'` не стане більшим або рівним 0.

### Тестування та верифікація граничних випадків

Під час розробки та модульного тестування (unit testing) даного розрахункового компонента особлива увага приділяється граничним та нестандартним термодинамічним ситуаціям:

1. **Багатокомпонентні розчини електролітів зі складними комплексоутвореннями:**
   Коли у водній фазі одночасно перебувають іони `Fe³⁺`, `Fe²⁺`, `FeOH²⁺`, `Fe(OH)₂⁺`, `H⁺`, `OH⁻` та аніони `SO₄²⁻`, кількість хімічних речовин `N` може сягати 10 і більше. Проте наявність кількох рівноважних реакцій гідролізу (`R`) та двох умов (електронейтральності розчину та збереження мольного співвідношення `Fe/S`) редукують кількість незалежних компонентів до `C = 2` (вода та сульфат заліза). Якщо тестовий модуль не врахує співвідношення `r`, солвер видасть помилкову кількість ступеней вільності.

2. **Системи з фазовим розшаруванням у рідкому стані (несмишуваність рідин):**
   У таких системах, як вода-бутанол чи вода-бензол, рідина розшаровується на дві окремі рідкі фази `L₁` та `L₂`. Кожна з цих фаз містить обидва компоненти, але в різних концентраціях. Програма повинна правильно підраховувати `P = 2` для рідкої частини системи, що при `P = const` дає `F' = 2 - 2 + 1 = 1` (система є моноваріантною: вибір температури однозначно визначає склад обох рівноважних рідких шарів за лінією бінодалі).

### Реалізація алгоритму в коді

Нижче наведено дві повноцінні, ідіоматичні реалізації модулю: сучасною мовою C++ (C++20 з використанням `std::expected`, `std::string_view` та `std::format`) та чистою мовою C (C99 з використанням строгої перевірки вказівників, кодами помилок та C-структурами).

:::tabs
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <expected>
#include <format>

namespace Gibbs {

// Перелічувач класифікації термодинамічного стану системи
enum class StateClass {
    ImpossibleOverconstrained, // F < 0: перевизначена система (фізично неможлива)
    Nonvariant,               // F == 0: нонваріантний стан (строго фіксована точка)
    Univariant,               // F == 1: моноваріантний стан (рівноважна лінія)
    Bivariant,                // F == 2: біваріантний стан (рівноважна область)
    Multivariant              // F > 2: мультиваріантний стан (багатовимірний простір)
};

// Вхідна конфігурація гетерогенної системи
struct SystemInput {
    std::string_view system_name;
    int species_count{1};     // N: загальне число хімічних речовин
    int reactions_count{0};   // R: число незалежних хімічних реакцій
    int constraints_count{0}; // r: число додаткових обмежень (заряд тощо)
    int phases_count{1};      // P: число рівноважних фаз
    bool is_isobaric{false};   // P = const
    bool is_isothermal{false}; // T = const
    int external_fields{0};   // m: додаткові зовнішні поля
};

// Результат фазового аналізу
struct CalculationResult {
    int independent_components{0}; // C = N - R - r
    int degrees_of_freedom{0};     // F
    StateClass state_class{StateClass::Nonvariant};
    std::string_view description;
};

// Коди помилок валідації вхідних даних
enum class ValidationError {
    InvalidSpeciesCount,
    InvalidPhaseCount,
    InvalidReactionsOrConstraints
};

class PhaseRuleSolver {
public:
    [[nodiscard]] static std::expected<CalculationResult, ValidationError> 
    solve(const SystemInput& input) noexcept {
        if (input.species_count < 1) {
            return std::unexpected(ValidationError::InvalidSpeciesCount);
        }
        if (input.phases_count < 1) {
            return std::unexpected(ValidationError::InvalidPhaseCount);
        }

        // Обчислюємо кількість незалежних компонентів C
        const int C = input.species_count - input.reactions_count - input.constraints_count;
        if (C < 1) {
            return std::unexpected(ValidationError::InvalidReactionsOrConstraints);
        }

        // Базовий зсув параметрів (за замовчуванням 2: T та P)
        int pressure_temperature_offset = 2;
        if (input.is_isobaric) {
            --pressure_temperature_offset;
        }
        if (input.is_isothermal) {
            --pressure_temperature_offset;
        }

        // Формула правила фаз Гіббса: F = C - P + offset + m
        const int F = C - input.phases_count + pressure_temperature_offset + input.external_fields;

        StateClass classification = StateClass::ImpossibleOverconstrained;
        std::string_view desc = "Перевизначена система (термодинамічно неможливий стан, F < 0)";

        if (F == 0) {
            classification = StateClass::Nonvariant;
            desc = "Нонваріантний стан (F = 0, параметри строго зафіксовані природою)";
        } else if (F == 1) {
            classification = StateClass::Univariant;
            desc = "Моноваріантний стан (F = 1, один вільний параметр)";
        } else if (F == 2) {
            classification = StateClass::Bivariant;
            desc = "Біваріантний стан (F = 2, два вільні параметри)";
        } else if (F > 2) {
            classification = StateClass::Multivariant;
            desc = "Мультиваріантний стан (F > 2, багато вільних параметрів)";
        }

        return CalculationResult{
            .independent_components = C,
            .degrees_of_freedom = F,
            .state_class = classification,
            .description = desc
        };
    }
};

} // namespace Gibbs

int main() {
    const std::vector<Gibbs::SystemInput> test_cases = {
        { "Потрійна точка води (H2O)", 1, 0, 0, 3, false, false, 0 },
        { "Рідина + Пара води (P варіюється)", 1, 0, 0, 2, false, false, 0 },
        { "Дисоціація CaCO3 (CaCO3, CaO, CO2)", 3, 1, 0, 3, false, false, 0 },
        { "Подвійний евтоктичний сплав (P = const)", 2, 0, 0, 3, true, false, 0 },
        { "Неможлива трифазна вода при P = const", 1, 0, 0, 3, true, false, 0 },
        { "Феромагнітний сплав у магнітному полі (m = 1)", 2, 0, 0, 2, true, false, 1 }
    };

    std::cout << "=== ТЕРМОДИНАМІЧНИЙ КАЛЬКУЛЯТОР ПРАВИЛА ФАЗ ГІББСА (C++) ===\n\n";

    for (const auto& test : test_cases) {
        auto res = Gibbs::PhaseRuleSolver::solve(test);
        if (res.has_value()) {
            std::cout << std::format("Система: {}\n", test.system_name);
            std::cout << std::format("  Незалежні компоненти (C): {}\n", res->independent_components);
            std::cout << std::format("  Ступені вільності (F): {}\n", res->degrees_of_freedom);
            std::cout << std::format("  Статус: {}\n\n", res->description);
        } else {
            std::cout << std::format("Помилка валідації вхідних даних для {}\n\n", test.system_name);
        }
    }

    return 0;
}
```
```c
#include <stdio.h>
#include <stdbool.h>

typedef enum {
    GIBBS_OK = 0,
    GIBBS_ERR_SPECIES = -1,
    GIBBS_ERR_PHASES = -2,
    GIBBS_ERR_COMPONENTS = -3
} GibbsErrorCode;

typedef enum {
    STATE_OVERCONSTRAINED = -1,
    STATE_NONVARIANT = 0,
    STATE_UNIVARIANT = 1,
    STATE_BIVARIANT = 2,
    STATE_MULTIVARIANT = 3
} SystemStateClass;

typedef struct {
    const char* system_name;
    int species_count;     /* N */
    int reactions_count;   /* R */
    int constraints_count; /* r */
    int phases_count;      /* P */
    bool is_isobaric;      /* P = const */
    bool is_isothermal;    /* T = const */
    int external_fields;   /* m */
} GibbsSystemInput;

typedef struct {
    int independent_components; /* C */
    int degrees_of_freedom;     /* F */
    SystemStateClass state_class;
    const char* description;
} GibbsCalculationResult;

GibbsErrorCode gibbs_calculate(const GibbsSystemInput* input, GibbsCalculationResult* result) {
    if (!input || !result) return GIBBS_ERR_SPECIES;
    if (input->species_count < 1) return GIBBS_ERR_SPECIES;
    if (input->phases_count < 1) return GIBBS_ERR_PHASES;

    int C = input->species_count - input->reactions_count - input->constraints_count;
    if (C < 1) return GIBBS_ERR_COMPONENTS;

    int offset = 2;
    if (input->is_isobaric) --offset;
    if (input->is_isothermal) --offset;

    int F = C - input->phases_count + offset + input->external_fields;

    result->independent_components = C;
    result->degrees_of_freedom = F;

    if (F < 0) {
        result->state_class = STATE_OVERCONSTRAINED;
        result->description = "Перевизначена система (термодинамічно неможливий стан, F < 0)";
    } else if (F == 0) {
        result->state_class = STATE_NONVARIANT;
        result->description = "Нонваріантний стан (F = 0, параметри строго зафіксовані природою)";
    } else if (F == 1) {
        result->state_class = STATE_UNIVARIANT;
        result->description = "Моноваріантний стан (F = 1, один вільний параметр)";
    } else if (F == 2) {
        result->state_class = STATE_BIVARIANT;
        result->description = "Біваріантний стан (F = 2, два вільні параметри)";
    } else {
        result->state_class = STATE_MULTIVARIANT;
        result->description = "Мультиваріантний стан (F > 2, багато вільних параметрів)";
    }

    return GIBBS_OK;
}

int main(void) {
    GibbsSystemInput test_cases[] = {
        { "Потрійна точка води (H2O)", 1, 0, 0, 3, false, false, 0 },
        { "Рідина + Пара води (P варіюється)", 1, 0, 0, 2, false, false, 0 },
        { "Дисоціація CaCO3 (CaCO3, CaO, CO2)", 3, 1, 0, 3, false, false, 0 },
        { "Подвійний евтоктичний сплав (P = const)", 2, 0, 0, 3, true, false, 0 },
        { "Неможлива трифазна вода при P = const", 1, 0, 0, 3, true, false, 0 },
        { "Феромагнітний сплав у магнітному полі (m = 1)", 2, 0, 0, 2, true, false, 1 }
    };
    size_t count = sizeof(test_cases) / sizeof(test_cases[0]);

    printf("=== ТЕРМОДИНАМІЧНИЙ КАЛЬКУЛЯТОР ПРАВИЛА ФАЗ ГІББСА (C) ===\n\n");

    for (size_t i = 0; i < count; ++i) {
        GibbsCalculationResult res;
        GibbsErrorCode err = gibbs_calculate(&test_cases[i], &res);
        if (err == GIBBS_OK) {
            printf("Система: %s\n", test_cases[i].system_name);
            printf("  Незалежні компоненти (C): %d\n", res.independent_components);
            printf("  Ступені вільності (F): %d\n", res.degrees_of_freedom);
            printf("  Статус: %s\n\n", res.description);
        } else {
            printf("Помилка розрахунку код %d для %s\n\n", err, test_cases[i].system_name);
        }
    }

    return 0;
}
```
:::

### Обчислювальна складність та алгоритмічний аналіз

Обчислювальна складність даного алгоритму становить **`O(1)`** за часом та **`O(1)`** за пам'яттю. Функція виконує лише кілька базових цілочисельних операцій віднімання та порівняння, не містить циклів, рекурсій або динамічного виділення купи (`heap`).

Порівняно з чисельною мінімізацією енергії Гіббса методами нелінійного програмування, яка вимагає ітераційного обчислення матриць Якобі та Гессе розмірністю `N × N` зі складністю `O(N³)` на кожному кроці, даний препроцесор працює у мільйони разів швидше. Це дозволяє вбудовувати його у внутрішні цикли високопродуктивних розрахунків термодинамічних сіток та інтегрувати у мобільні чи веб-симулятори фізичної хімії.
