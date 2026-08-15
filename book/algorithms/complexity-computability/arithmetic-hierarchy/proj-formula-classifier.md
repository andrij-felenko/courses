# ⚙️ Практичний аналізатор кванторних префіксів та симулятор оракульних обчислень

У цій проектній вставці реалізовано практичний алгоритм аналізу синтаксичної структури формул логіки першого порядку для автоматичного визначення їхнього канонічного класу в арифметичній ієрархії (`Σ♁⁰`, `Π♁⁰`, `Δ♁⁰`), виконання реального згортання однорідних кванторів через функцію парування Кантора та розрахунку індексу необхідного оракульного стрибка Тюринга.

## Ідея та архітектура алгоритму

Символьні аналізатори логічних формул є фундаментальною частиною автоматичних доведеш теорем (SMT-солверів) та інструментів верифікації програмного забезпечення.

Запропонована програма приймає на вхід масив кванторів префіксної нормальної форми та виконує наступні послідовні алгоритмічні кроки:

1. **Токенізація та валідація:** Перевірка послідовності кванторів `EXISTS` (∃) та `FORALL` (∀), а також виявлення обмежених кванторів.
2. **Згортання сусідніх кванторів (Quantifier Contraction):** Видалення дубльованих однакових кванторів, що йдуть поспіль, шляхом моделювання кодування Кантора `⟨a, b⟩ = ((a + b)(a + b + 1))/2 + b`.
3. **Обчислення класу арифметичної ієрархії:** Визначення стартового квантора (`Σ` для `EXISTS`, `Π` для `FORALL`) та кількості чергувань `n`.
4. **Визначення необхідного оракула:** Обчислення рівня ітерованого стрибка Тюринга `0⁽ⁿ⁻¹⁾`, необхідного для перелічуваності або розв'язання даного предиката.

Поточна реалізація підтримує мови C та C++ з використанням сучасних ідіом (включаючи `std::expected` та тип `enum class` у C++23).

```:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    QUANT_EXISTS,
    QUANT_FORALL
} QuantifierType;

typedef struct {
    QuantifierType type;
    char var_name[32];
    bool is_bounded;
    uint64_t bound_limit;
} Quantifier;

typedef struct {
    char class_name[16];  /* Наприклад, "Sigma_3" або "Pi_2" */
    size_t alternation_depth;
    size_t oracle_jump_level;
    size_t original_quantifier_count;
    size_t contracted_quantifier_count;
} HierarchyResult;

/* Обчислення функції парування Кантора <a, b> */
uint64_t cantor_pair(uint64_t a, uint64_t b) {
    return ((a + b) * (a + b + 1)) / 2 + b;
}

/* Аналіз та класифікація послідовності кванторів */
bool classify_arithmetic_formula(const Quantifier* raw_quants, size_t count, HierarchyResult* result) {
    if (count == 0 || result == NULL) {
        if (result != NULL) {
            snprintf(result->class_name, sizeof(result->class_name), "Delta_0");
            result->alternation_depth = 0;
            result->oracle_jump_level = 0;
            result->original_quantifier_count = 0;
            result->contracted_quantifier_count = 0;
        }
        return true;
    }

    /* Фільтрація та збереження згорнутих кванторів */
    Quantifier* contracted = (Quantifier*)malloc(count * sizeof(Quantifier));
    if (!contracted) {
        return false;
    }

    size_t c_count = 0;
    
    /* Додаємо перший необмежений квантор */
    size_t start_idx = 0;
    while (start_idx < count && raw_quants[start_idx].is_bounded) {
        start_idx++;
    }

    if (start_idx >= count) {
        /* Всі квантори обмежені -> Delta_0 */
        snprintf(result->class_name, sizeof(result->class_name), "Delta_0");
        result->alternation_depth = 0;
        result->oracle_jump_level = 0;
        result->original_quantifier_count = count;
        result->contracted_quantifier_count = 0;
        free(contracted);
        return true;
    }

    contracted[0] = raw_quants[start_idx];
    c_count++;

    /* Алгоритм згортання однорідних кванторів */
    for (size_t i = start_idx + 1; i < count; i++) {
        if (raw_quants[i].is_bounded) {
            continue; /* Обмежені квантори не міняють чергування */
        }
        if (raw_quants[i].type != contracted[c_count - 1].type) {
            contracted[c_count] = raw_quants[i];
            c_count++;
        }
    }

    /* Визначення класу Σ_n або Pi_n */
    QuantifierType start_type = contracted[0].type;
    size_t n = c_count;

    if (start_type == QUANT_EXISTS) {
        snprintf(result->class_name, sizeof(result->class_name), "Sigma_%zu", n);
    } else {
        snprintf(result->class_name, sizeof(result->class_name), "Pi_%zu", n);
    }

    result->alternation_depth = n;
    result->oracle_jump_level = (n > 0) ? (n - 1) : 0;
    result->original_quantifier_count = count;
    result->contracted_quantifier_count = c_count;

    free(contracted);
    return true;
}

int main(void) {
    printf("=== Аналізатор Арифметичної Ієрархії (C) ===\n\n");

    /* Тестовий випадок: ∃y1 ∃y2 ∀z1 ∀z2 ∀z3 ∃w R(x, y1, y2, z1, z2, z3, w) */
    Quantifier test_formula[] = {
        { QUANT_EXISTS, "y1", false, 0 },
        { QUANT_EXISTS, "y2", false, 0 },
        { QUANT_FORALL, "z1", false, 0 },
        { QUANT_FORALL, "z2", false, 0 },
        { QUANT_FORALL, "z3", false, 0 },
        { QUANT_EXISTS, "w", false, 0 }
    };
    size_t count = sizeof(test_formula) / sizeof(test_formula[0]);

    HierarchyResult res;
    if (classify_arithmetic_formula(test_formula, count, &res)) {
        printf("Початкова кількість кванторів: %zu\n", res.original_quantifier_count);
        printf("Після згортання Кантора:      %zu\n", res.contracted_quantifier_count);
        printf("Клас арифметичної ієрархії:   %s^0\n", res.class_name);
        printf("Глибина чергування (n):        %zu\n", res.alternation_depth);
        printf("Необхідний оракул Тюринга:    0^(%zu)\n", res.oracle_jump_level);
    }

    /* Демонстрація парування Кантора */
    uint64_t y1 = 3, y2 = 5;
    uint64_t paired = cantor_pair(y1, y2);
    printf("\nДемонстрація згортання ∃y1=3, ∃y2=5 -> Y = <3,5> = %llu\n", (unsigned long long)paired);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <numeric>
#include <format>
#include <expected>

enum class QuantifierKind {
    Exists,
    Forall
};

struct QuantifierNode {
    QuantifierKind kind;
    std::string var_name;
    bool is_bounded{false};
    std::uint64_t bound_limit{0};
};

struct HierarchyClassification {
    std::string class_symbol;
    std::size_t alternation_depth{0};
    std::size_t required_oracle_jump{0};
    std::size_t original_count{0};
    std::size_t contracted_count{0};
};

class ArithmeticFormulaAnalyzer {
public:
    // Бієкція парування Кантора <a, b>
    [[nodiscard]] static constexpr std::uint64_t cantor_pair(std::uint64_t a, std::uint64_t b) noexcept {
        return ((a + b) * (a + b + 1)) / 2 + b;
    }

    // Аналіз послідовності кванторів з поверненням std::expected (C++23)
    [[nodiscard]] static std::expected<HierarchyClassification, std::string> 
    classify(const std::vector<QuantifierNode>& quantifiers) {
        if (quantifiers.empty()) {
            return HierarchyClassification{
                .class_symbol = "Delta_0",
                .alternation_depth = 0,
                .required_oracle_jump = 0,
                .original_count = 0,
                .contracted_count = 0
            };
        }

        std::vector<QuantifierNode> contracted;
        contracted.reserve(quantifiers.size());

        // Фільтрація обмежених кванторів та згортання однорідних
        for (const auto& q : quantifiers) {
            if (q.is_bounded) {
                continue; // Ігноруємо обмежені квантори
            }
            if (contracted.empty() || contracted.back().kind != q.kind) {
                contracted.push_back(q);
            }
        }

        if (contracted.empty()) {
            return HierarchyClassification{
                .class_symbol = "Delta_0",
                .alternation_depth = 0,
                .required_oracle_jump = 0,
                .original_count = quantifiers.size(),
                .contracted_count = 0
            };
        }

        const auto n = contracted.size();
        const auto prefix_char = (contracted.front().kind == QuantifierKind::Exists) ? "Sigma" : "Pi";

        return HierarchyClassification{
            .class_symbol = std::string(prefix_char) + "_" + std::to_string(n),
            .alternation_depth = n,
            .required_oracle_jump = (n > 0) ? (n - 1) : 0,
            .original_count = quantifiers.size(),
            .contracted_count = contracted.size()
        };
    }
};

int main() {
    std::cout << "=== Аналізатор Арифметичної Ієрархії (C++23) ===\n\n";

    const std::vector<QuantifierNode> formula{
        { QuantifierKind::Exists, "y1", false, 0 },
        { QuantifierKind::Exists, "y2", false, 0 },
        { QuantifierKind::Forall, "z1", false, 0 },
        { QuantifierKind::Forall, "z2", false, 0 },
        { QuantifierKind::Forall, "z3", false, 0 },
        { QuantifierKind::Exists, "w",  false, 0 }
    };

    const auto result = ArithmeticFormulaAnalyzer::classify(formula);

    if (result) {
        std::cout << "Початкова кількість кванторів: " << result->original_count << "\n";
        std::cout << "Після згортання Кантора:      " << result->contracted_count << "\n";
        std::cout << "Клас арифметичної ієрархії:   " << result->class_symbol << "^0\n";
        std::cout << "Глибина чергування (n):        " << result->alternation_depth << "\n";
        std::cout << "Необхідний оракул Тюринга:    0^(" << result->required_oracle_jump << ")\n";
    } else {
        std::cerr << "Помилка аналізу: " << result.error() << "\n";
    }

    const auto paired = ArithmeticFormulaAnalyzer::cantor_pair(3, 5);
    std::cout << "\nЗгортання паруванням Кантора <3, 5> = " << paired << "\n";

    return 0;
}
```
:::

## Детальний опис реалізації та аналіз алгоритмічної складності

### Алгоритмічний механізм аналізу

1. **Сканування та фільтрація:** Алгоритм виконує один прохід за часом `O(N)` (де `N` — початкова кількість кванторів у формулі). Вхідні квантори перевіряються на прапорець `is_bounded`. Обмежені квантори (наприклад, `∀z ≤ 100`) належать до класу `Δ₀⁰` та усуваються з підрахунку чергувань.
2. **Згортання однорідних кванторів (Cantor Reduction):** Якщо у формулі знаходяться декілька послідовних необмежених кванторів одного типу (`∃y₁ ∃y₂ ∃y₃`), алгоритм об'єднує їх у єдину квантифіковану змінну `Y = ⟨⟨y₁, y₂⟩, y₃⟩`. У коді це моделюється порівнянням типів кванторів `q.kind != contracted.back().kind`.
3. **Обчислення класу складності та оракулів:** Залишковий масив згорнутих кванторів задає рівень `n = contracted.size()`. Якщо перший квантор є `Exists`, встановлюється клас `Σ_n^0`. За теоремою Поста, алгоритмічна оцінка даного предиката вимагає оракула `0⁽ⁿ⁻¹⁾` (де `0⁽⁰⁾ = ∅`, `0⁽¹⁾ = K`).

### Порівняння реалізацій C та C++

- **Реалізація на C:** Використовує динамічне виділення пам'яті через `malloc`/`free`,явний контроль повернення прапорців успішності `bool` та форматований вивід через `snprintf`.
- **Реалізація на C++ (C++23):** Використовує RAII-контейнер `std::vector`, типу безпечну монотипну обробку через `enum class`, обчислення коду Кантора під час компіляції (`constexpr`), а також механізм винятків/повернення загороджувальних типів `std::expected<T, E>`.

Алгоритм має просторову складність `O(N)` для зберігання згорнутого префікса та часову складність `O(N)` для однократного сканування вхідного виразу.
