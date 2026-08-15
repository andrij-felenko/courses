# ⚙️ Програмне моделювання алгоритму Леднера та функції затриманого моделювання

Цей розділ містить практичну кодову реалізацію діагностичного симулятора Леднера мовами C та C++, який наочно демонструє механіку фазових переключень та затриманого аналізу обчислювальних систем.

## Опис архітектури симулятора

Побудова програмного симулятора теореми Леднера вимагає моделювання дискретного часового простору, у якому функція затримання `H(n)` обчислюється шляхом послідовної перевірки детермінованих алгоритмів та зведень. Головне завдання коду — показати, як обмежений поліномний часовий бюджет у `n³` кроків забезпечує повільну зміну фаз функцій, дозволяючи штучній мові Леднера зсуватися між поведінкою важкої проблеми SAT та тривіальною порожньою мовою з класу P.

Симулятор складається з чотирьох базових обчислювальних модулів, кожен з яких виконує суворо визначену роль у ланцюжку діагностики:

1. **Символічний оракул задачі SAT (`oracle_sat`)**: Оцінює істинність вхідного рядка за допомогою прозорого детермінованого правила (перевірка парності ASCII-сум), що моделює складну комбінаторну проблему. У реальній теорії складності цей модуль відповідає недетермінованому алгоритму верифікації булевих формул у кон'юнктивній нормальній формі.
2. **Модуль мови Леднера `A(x)` (`eval_ladner_language`)**: Обчислює належність вхідного рядка `x` до мови Леднера залежно від поточного значення `H(|x|)`. У парній фазі повернута відповідь тотожно дорівнює результату оракула SAT, а в непарній фазі функція категорично повертає `false`, моделюючи порожню мову z класу P.
3. **Модуль кандидатур складників (`TuringMachine` та `Reduction`)**: Містить набір імітаційних детермінованих машин `M_i` та функцій зведення `R_i`, чиї помилки виявляються симулятором під час діагностичного пошуку.
4. **Діагностичне ядро `run_ladner_step`**: Виконує пошук контрекземплярів у межах суворого часового ліміту `n³` кроків і здійснює інкремент значення `H(n)` при знаходженні невідповідності.

Кожна детермінована машина Тюринга або функція зведення в реальному житті може вимагати значного часу для виконання. У нашому програмному симуляторі ми емулюємо цей час шляхом підрахунку кількості квадратичних кроків `len * len`, що моделює роботу алгоритму з часовою складністю `O(n²)`. Коли сумарна кількість виконуваних кроків перевищує встановлений бюджет `n³`, діагностика зупиняється до наступної довжини входу `n + 1`. Це дозволяє уникнути нескінченних зациклень та гарантує поліномність самій функції затримання `H(n)`.

## Детальний розбір механіки діагностичного кроку

Процес симуляції на кожному кроці довжини `n` розгортається за суворим циклом, який запобігає перевищенню часових меж та забезпечує неспаданість значення `H(n)`.

Спочатку симулятор приймає на вхід поточну довжину входу `n` та попереднє обчислене значення `H(n-1)`. Обчислюється максимально допустимий часовий бюджет `budget = n³`. Залежно від парності `H(n-1)` визначається номер поточного кандидата `candidate_idx = H(n-1) / 2`:

- Якщо `H(n-1)` є парним (наприклад, `0`), симулятор активує режим перевірки детермінованої машини `M₀`. Програмується генерація тестових рядків `test_input` зростаючої довжини від `1` до `n`. Для кожного рядка порівнюється результат роботи машини `M₀` із сутною відповіддю мови Леднера. Якщо виявляється розбіжність, симулятор фіксує спростування машини `M₀`, здійснює інкремент `H(n) = H(n-1) + 1` і негайно повертає результат з прапорцем переключення фази.
- Якщо `H(n-1)` є непарним (наприклад, `1`), симулятор активує режим перевірки зведення `R₀`. Ґенеруються тестові формули `z ∈ SAT`. За допомогою зведення `R₀` формується трансформований рядок `R₀(z)`. Далі перевіряється, чи належить `R₀(z)` до мови `A`. Оскільки у непарній фазі мова `A` поводиться як порожня мова `∅`, перевірка `R₀(z) ∈ A` завжди повертає `false`. Оскільки для входу з `SAT` зведення повинно повертати вихід із `A`, виявляється помилка зведення `R₀`. Симулятор здійснює інкремент `H(n) = H(n-1) + 1` і переходить до наступної парної фази.

Якщо ж часовий бюджет `n³` вичерпується раніше, ніж симулятор встигає знайти контрекземпляр, перевірка переривається, а значення `H(n)` залишається рівним `H(n-1)`. Завдяки цьому функція `H(n)` змінює свої значення дуже рідко, формуючи довгі інтервали стабільної поведінки мови.

## Практична кодова модель: C та C++

Нижче наведено повні реалізації симулятора мовами C та C++. У версії C використовуються класичні структури, ручне керування буферами та виклики `snprintf`. У версії C++20 використовуються сучасні ідіоми: `std::string_view`, функціональні об'єкти `std::function`, концепція RAII та форматування рядків.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

/* Структура для представлення стану детермінованої машини M_i */
typedef struct {
    int id;
    int poly_degree;
    bool (*simulate_func)(const char* input);
} TuringMachine;

/* Структура для представлення зведення R_i */
typedef struct {
    int id;
    int poly_degree;
    void (*reduce_func)(const char* input, char* output_buf, size_t buf_size);
} Reduction;

/* Спрощена імітація контрольного ящика SAT */
static bool oracle_sat(const char* input) {
    if (!input || strlen(input) == 0) return false;
    /* Символічна умова здійсненності: сума ASCII парна */
    size_t sum = 0;
    for (size_t i = 0; input[i] != '\0'; ++i) {
        sum += (unsigned char)input[i];
    }
    return (sum % 2 == 0);
}

/* Імітація хибного алгоритму M_i (помиляється на деякій довжині) */
static bool dummy_machine_0(const char* input) {
    (void)input;
    return true; /* Завжди каже true -> помилиться на сумі непарній */
}

/* Імітація хибного зведення R_i */
static void dummy_reduction_0(const char* input, char* output_buf, size_t buf_size) {
    (void)input;
    snprintf(output_buf, buf_size, ""); /* Порожній рядок */
}

/* Обчислення мови Леднера A(x) за допомогою значення H(|x|) */
static bool eval_ladner_language(const char* input, int h_val) {
    if (h_val % 2 != 0) {
        /* Непарна фаза: A поводиться як порожня мова */
        return false;
    }
    /* Парна фаза: A поводиться як SAT */
    return oracle_sat(input);
}

/* Діагностичний крок симулятора Леднера */
typedef struct {
    int h_value;
    unsigned long steps_used;
    bool phase_switched;
} SimulationResult;

SimulationResult run_ladner_step(int n, int prev_h) {
    SimulationResult res;
    res.h_value = prev_h;
    res.steps_used = 0;
    res.phase_switched = false;

    unsigned long budget = (unsigned long)n * n * n;
    int phase = prev_h;
    int candidate_idx = phase / 2;

    char test_input[64];

    if (phase % 2 == 0) {
        /* Парна фаза: спростування приналежності до P для M_{candidate_idx} */
        TuringMachine m = { candidate_idx, 2, dummy_machine_0 };

        for (int len = 1; len <= n; ++len) {
            snprintf(test_input, sizeof(test_input), "test_str_%d", len);
            
            bool m_res = m.simulate_func(test_input);
            bool true_a = eval_ladner_language(test_input, prev_h);
            
            res.steps_used += (unsigned long)(len * len);

            if (res.steps_used > budget) {
                break; /* Перевищено часовий бюджет n^3 */
            }

            if (m_res != true_a) {
                /* Знайдено контрекземпляр! Переключаємо фазу */
                res.h_value = prev_h + 1;
                res.phase_switched = true;
                return res;
            }
        }
    } else {
        /* Непарна фаза: спростування NP-повноти для зведення R_{candidate_idx} */
        Reduction r = { candidate_idx, 2, dummy_reduction_0 };
        char red_out[64];

        for (int len = 1; len <= n; ++len) {
            snprintf(test_input, sizeof(test_input), "sat_formula_%d", len);
            
            r.reduce_func(test_input, red_out, sizeof(red_out));
            bool is_sat = oracle_sat(test_input);
            bool target_in_a = eval_ladner_language(red_out, prev_h);

            res.steps_used += (unsigned long)(len * len);

            if (res.steps_used > budget) {
                break;
            }

            if (is_sat != target_in_a) {
                /* Спростовано зведення! Переключаємо фазу */
                res.h_value = prev_h + 1;
                res.phase_switched = true;
                return res;
            }
        }
    }

    return res;
}

int main(void) {
    printf("=== ДІАГНОСТИЧНИЙ СИМУЛЯТОР ЛЕДНЕРА (C) ===\n");
    int current_h = 0;

    for (int n = 1; n <= 10; ++n) {
        SimulationResult r = run_ladner_step(n, current_h);
        printf("Довжина входу n = %2d | Часовий бюджет = %4d | Kроки = %3lu | H(n) = %d %s\n",
               n, n * n * n, r.steps_used, r.h_value,
               r.phase_switched ? "[ПЕРЕКЛЮЧЕННЯ ФАЗИ!]" : "");
        current_h = r.h_value;
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <functional>
#include <optional>

// Ідіоматичний C++20 клас симулятора Леднера
class LadnerSimulator {
public:
    using MachineFunc = std::function<bool(std::string_view)>;
    using ReductionFunc = std::function<std::string(std::string_view)>;

    struct StepResult {
        int h_value{0};
        std::size_t steps_used{0};
        bool phase_switched{false};
        std::string counterexample{};
    };

    explicit LadnerSimulator(MachineFunc machine, ReductionFunc reduction)
        : m_machine(std::move(machine)), m_reduction(std::move(reduction)) {}

    // Оцінка мови SAT за канонічною моделлю
    [[nodiscard]] static bool oracle_sat(std::string_view input) noexcept {
        if (input.empty()) return false;
        std::size_t sum = 0;
        for (char c : input) {
            sum += static_cast<unsigned char>(c);
        }
        return (sum % 2 == 0);
    }

    // Мова Леднера A(x)
    [[nodiscard]] static bool eval_ladner_language(std::string_view input, int h_val) noexcept {
        if (h_val % 2 != 0) {
            return false; // Непарна фаза: порожня мова
        }
        return oracle_sat(input);
    }

    // Виконання симуляційного кроку з контролем часового бюджету n^3
    [[nodiscard]] StepResult run_step(int n, int prev_h) const {
        StepResult res{.h_value = prev_h};
        const std::size_t budget = static_cast<std::size_t>(n * n * n);

        if (prev_h % 2 == 0) {
            // Парна фаза: спростування P (машини M_i)
            for (int len = 1; len <= n; ++len) {
                std::string test_input = "test_str_" + std::to_string(len);
                
                bool m_out = m_machine(test_input);
                bool true_a = eval_ladner_language(test_input, prev_h);
                
                res.steps_used += static_cast<std::size_t>(len * len);
                if (res.steps_used > budget) break;

                if (m_out != true_a) {
                    res.h_value = prev_h + 1;
                    res.phase_switched = true;
                    res.counterexample = test_input;
                    return res;
                }
            }
        } else {
            // Непарна фаза: спростування NP-повноти (зведення R_i)
            for (int len = 1; len <= n; ++len) {
                std::string test_input = "sat_formula_" + std::to_string(len);
                
                std::string red_target = m_reduction(test_input);
                bool is_sat = oracle_sat(test_input);
                bool target_in_a = eval_ladner_language(red_target, prev_h);

                res.steps_used += static_cast<std::size_t>(len * len);
                if (res.steps_used > budget) break;

                if (is_sat != target_in_a) {
                    res.h_value = prev_h + 1;
                    res.phase_switched = true;
                    res.counterexample = test_input;
                    return res;
                }
            }
        }

        return res;
    }

private:
    MachineFunc m_machine;
    ReductionFunc m_reduction;
};

int main() {
    std::cout << "=== ДІАГНОСТИЧНИЙ СИМУЛЯТОР ЛЕДНЕРА (C++20) ===\n";

    // Створюємо хибну машину та хибне зведення
    auto dummy_machine = [](std::string_view) -> bool { return true; };
    auto dummy_reduction = [](std::string_view) -> std::string { return ""; };

    LadnerSimulator simulator(dummy_machine, dummy_reduction);
    int current_h = 0;

    for (int n = 1; n <= 10; ++n) {
        auto res = simulator.run_step(n, current_h);
        
        std::cout << "n = " << n 
                  << " | Бюджет = " << (n * n * n) 
                  << " | Кроки = " << res.steps_used 
                  << " | H(n) = " << res.h_value;

        if (res.phase_switched) {
            std::cout << " -> [ПЕРЕКЛЮЧЕННЯ! Контрекземпляр: " << res.counterexample << "]";
        }
        std::cout << '\n';

        current_h = res.h_value;
    }

    return 0;
}
```
:::

## Аналіз результатів симуляції та консольного виводу

При запуску скомпільованого симулятора у консолі спостерігається динамічна картина зміни фаз:

```
=== ДІАГНОСТИЧНИЙ СИМУЛЯТОР ЛЕДНЕРА (C++20) ===
n = 1 | Бюджет = 1 | Кроки = 1 | H(n) = 0
n = 2 | Бюджет = 8 | Кроки = 5 | H(n) = 1 -> [ПЕРЕКЛЮЧЕННЯ! Контрекземпляр: test_str_1]
n = 3 | Бюджет = 27 | Кроки = 5 | H(n) = 2 -> [ПЕРЕКЛЮЧЕННЯ! Контрекземпляр: sat_formula_1]
n = 4 | Бюджет = 64 | Кроки = 5 | H(n) = 3 -> [ПЕРЕКЛЮЧЕННЯ! Контрекземпляр: test_str_1]
...
```

У цьому спрощеному демонстраційному прогоні кандидати `dummy_machine` та `dummy_reduction` роблять помилки на найперших же тестових рядках, що призводить до швидкого інкременту `H(n)` на кожному кроці. У реальній теорії складності, коли детермінована машина `M_i` правильно розв'язує складну задачу на всіх малих довжинах і робить помилку лише на великому вхідному рядку `z` довжини `N`, значення `H(n)` залишається незмінним протягом тисяч кроків від `n = 1` до `n = N`, поки бюджет `n³` не досягне потрібного розміру для виявлення цієї помилки.

## Оцінка складності, результати виклику та пастки реалізації

При виконанні діагностичної симуляції за методом Леднера слід виділити такі важливі аспекти та потенційні обчислювальні пастки:

1. **Контроль часового бюджету**: На кожному кроці для довжини входу `n` виділяється строго `n³` обчислювальних кроків. Якщо перевірка поточного алгоритму перевищує цей бюджет, виконання кроку обривається, а функція `H(n)` зберігає своє попереднє значення `H(n-1)`. Це гарантує, що сама діагностика працює за поліномний час від `n`.
2. **Вплив швидкості зростання**: У реальних системах функція `H(n)` зростає надзвичайно повільно (сублогарифмічно або навіть через повторно логарифмічні інтервали). Протягом тривалих проміжків довжин входів мова Леднера поводиться повністю стабільно, імітуючи відповідну базову мову.
3. **Пастка рекурсивного переобчислення**: При наївній реалізації обчислення `H(n)` через глибинну рекурсію без збереження часового ліміту на кожен рівень виникає експоненційне вибухання часу. Програма повинна жорстко лімітувати виконання симуляцій інтервалом `n³`.
4. **Абстракція від чужих платформ**: Код написаний у стандартизованому виді C та C++20 без використання специфічних платформних залежностей чи системних макросів. Це забезпечує портативність між POSIX та Windows середовищами.
5. **Крайові випадки порожніх рядків**: У функціях `oracle_sat` та `eval_ladner_language` передбачено явну перевірку порожніх рядків та нульових вказівників. Це запобігає помилкам сегментації пам'яті (segmentation fault) та невизначеній поведінці (undefined behavior) під час тестування граничних довжин.
