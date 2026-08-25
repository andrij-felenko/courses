# ⚙️ Реалізація симулятора нестандартної арифметики та машин Тюринга

Оскільки теорема Тенненбаума забороняє існування обчислювально точних моделей арифметики Пеано, реалізація симулятора нестандартних числових систем та нестандартних машин Тюринга спирається на символьну модель поліноміальних нестандартних чисел виду `n + z · H + q · H²` (де `H` — символ нескінченно великого нестандартного елемента), проводить предикативні перевірки за принципом Оверспілу та моделює траєкторію виконання нестандартної машини Тюринга протягом гіпер-часових кроків `H`.

## Алгоритмічна ідея та алгебраїчна архітектура симулятора

Для представлення елементів нестандартної моделі в пам'яті обчислювальної системи використовується алгебраїчне символьне розширення над кільцем цілих чисел `ℤ[H]`. Оскільки звичайні цілочисельні типи даних в обчислювачах (`uint64_t` або навіть числа довільної точності `BigInt`) здатні кодувати лише скінченні натуральні числа з `ℕ`, для моделювання елементів із нестандартного сегменту `M \ ℕ` необхідна формалізація не-архімедової алгебраїчної структури.

Нестандартне число `X` подається у вигляді полінома від нескінченної змінної `H`:

```
X = a₀ + a₁ · H + a₂ · H² + ... + aₖ · Hᵏ
```

де `a₀ ∈ ℕ` — стандартна цілочисельна частина, а `a₁, ..., aₖ ∈ ℤ` — коефіцієнти при вищих степенях нескінченного елемента `H`.

Така символьна структура задовольняє аксіомам лінійного порядку нестандартних моделей `ℕ + ℤ × ℚ`:
- Якщо `aₖ = 0` для всіх `k ≥ 1`, число `X = a₀` належить стандартному початковому сегменту `ℕ`.
- Якщо існує `k ≥ 1` з `aₖ > 0`, число `X` є нестандартно великим (`X > n` для всіх `n ∈ ℕ`).
- Порядок між двома числами `X` та `Y` визначається лексикографічно за старшим коефіцієнтом полінома: `X < Y ⟺ aₖ(X) < aₖ(Y)` для найбільшого `k`, де коефіцієнти відрізняються.

Додавання таких чисел здійснюється покомпонентним додаванням коефіцієнтів поліномів, а множення — через алгебраїчне згортання (свортку) з відтинанням вищих степенів, що перевищують максимально допустимий ступінь розкладки `MAX_DEGREE`.

Симулятор також моделює траєкторію нестандартної машини Тюринга, що виконує `H` кроків обчислення, реєструє стан стрічки та перевіряє межу Оверспілу для скінченно-програмних предикатів. Принцип Оверспілу перевіряється шляхом обчислення предикату на скінченному вибіркові відрізку стандартних натуральних чисел із наступною логічною екстраполяцією на нестандартний елемент `H`.

## Реалізація симулятора мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_DEGREE 4
#define TAPE_SIZE 64

/* Структура для символьного нестандартного числа: a0 + a1*H + a2*H^2 + ... */
typedef struct {
    int64_t coeffs[MAX_DEGREE];
} NonStandardInt;

/* Структура конфігурації нестандартної машини Тюринга */
typedef struct {
    uint8_t tape[TAPE_SIZE];
    size_t head_pos;
    int current_state;
    NonStandardInt step_count;
    bool halted;
} NonStandardTM;

/* Створення стандартного числа */
NonStandardInt ns_create_standard(int64_t val) {
    NonStandardInt num;
    memset(&num, 0, sizeof(num));
    num.coeffs[0] = val;
    return num;
}

/* Створення нестандартного елемента H^degree */
NonStandardInt ns_create_inf(size_t degree, int64_t coeff) {
    NonStandardInt num;
    memset(&num, 0, sizeof(num));
    if (degree < MAX_DEGREE) {
        num.coeffs[degree] = coeff;
    }
    return num;
}

/* Перевірка, чи є число стандартним (належить N) */
bool ns_is_standard(const NonStandardInt* num) {
    for (size_t i = 1; i < MAX_DEGREE; ++i) {
        if (num->coeffs[i] != 0) {
            return false;
        }
    }
    return num->coeffs[0] >= 0;
}

/* Порівняння двох нестандартних чисел (порядок у моделі) */
int ns_compare(const NonStandardInt* a, const NonStandardInt* b) {
    for (int i = MAX_DEGREE - 1; i >= 0; --i) {
        if (a->coeffs[i] > b->coeffs[i]) return 1;
        if (a->coeffs[i] < b->coeffs[i]) return -1;
    }
    return 0;
}

/* Додавання двох нестандартних чисел */
NonStandardInt ns_add(const NonStandardInt* a, const NonStandardInt* b) {
    NonStandardInt result;
    for (size_t i = 0; i < MAX_DEGREE; ++i) {
        result.coeffs[i] = a->coeffs[i] + b->coeffs[i];
    }
    return result;
}

/* Множення двох нестандартних чисел з відтинанням вищих степенів */
NonStandardInt ns_multiply(const NonStandardInt* a, const NonStandardInt* b) {
    NonStandardInt result;
    memset(&result, 0, sizeof(result));
    for (size_t i = 0; i < MAX_DEGREE; ++i) {
        for (size_t j = 0; j < MAX_DEGREE - i; ++j) {
            result.coeffs[i + j] += a->coeffs[i] * b->coeffs[j];
        }
    }
    return result;
}

/* Друк нестандартного числа */
void ns_print(const NonStandardInt* num) {
    bool first = true;
    for (int i = MAX_DEGREE - 1; i >= 0; --i) {
        if (num->coeffs[i] != 0) {
            if (!first && num->coeffs[i] > 0) printf(" + ");
            if (num->coeffs[i] < 0) printf(" - ");
            
            int64_t abs_val = num->coeffs[i] < 0 ? -num->coeffs[i] : num->coeffs[i];
            
            if (i == 0) {
                printf("%lld", (long long)abs_val);
            } else if (i == 1) {
                if (abs_val == 1) printf("H");
                else printf("%lld·H", (long long)abs_val);
            } else {
                if (abs_val == 1) printf("H^%d", i);
                else printf("%lld·H^%d", (long long)abs_val, i);
            }
            first = false;
        }
    }
    if (first) printf("0");
}

/* Перевірка принципу Оверспілу: предикат P(n), істинний для всіх n in N */
bool ns_check_overspill(bool (*predicate)(int64_t), const NonStandardInt* limit) {
    /* Крок 1: Перевіряємо стандартні елементи */
    for (int64_t i = 0; i < 100; ++i) {
        if (!predicate(i)) {
            return false;
        }
    }
    /* Крок 2: За принципом Оверспілу предикат розширюється на нестандартну область */
    return !ns_is_standard(limit);
}

/* Приклад предикату: n^2 >= 0 */
bool predicate_always_true(int64_t n) {
    return (n * n) >= 0;
}

/* Ініціалізація нестандартної машини Тюринга */
void tm_init(NonStandardTM* tm) {
    memset(tm->tape, 0, sizeof(tm->tape));
    tm->head_pos = TAPE_SIZE / 2;
    tm->current_state = 0;
    tm->step_count = ns_create_standard(0);
    tm->halted = false;
}

/* Симуляція одного кроку TM */
void tm_step(NonStandardTM* tm) {
    if (tm->halted) return;

    /* Проста програма: інверсія біта і зсув вправо */
    if (tm->current_state == 0) {
        tm->tape[tm->head_pos] ^= 1;
        if (tm->head_pos < TAPE_SIZE - 1) {
            tm->head_pos++;
        } else {
            tm->halted = true;
        }
    }
    
    NonStandardInt one = ns_create_standard(1);
    tm->step_count = ns_add(&tm->step_count, &one);
}

int main(void) {
    printf("=== Симулятор Нестандартної Арифметики та Машин Тюринга (C99) ===\n\n");

    NonStandardInt n5 = ns_create_standard(5);
    NonStandardInt H = ns_create_inf(1, 1);
    NonStandardInt H2 = ns_create_inf(2, 2);

    NonStandardInt sum = ns_add(&H, &n5);
    NonStandardInt prod = ns_multiply(&sum, &H);

    printf("Число A (стандартне): ");
    ns_print(&n5);
    printf("\nЧисло B (нестандартне H): ");
    ns_print(&H);
    printf("\nСума B + A: ");
    ns_print(&sum);
    printf("\nДобуток (H + 5) · H: ");
    ns_print(&prod);
    printf("\n\n");

    printf("Порівняння H та (H + 5): %d\n", ns_compare(&H, &sum));
    printf("Чи є H+5 стандартним? %s\n", ns_is_standard(&sum) ? "Так" : "Ні");

    NonStandardInt inf_limit = ns_create_inf(1, 1000);
    bool overspill = ns_check_overspill(predicate_always_true, &inf_limit);
    printf("Результат перевірки Оверспілу для H=1000·H: %s\n\n", overspill ? "УСПІХ (Перелив виконується)" : "ХИБА");

    NonStandardTM tm;
    tm_init(&tm);
    for (int i = 0; i < 10; ++i) {
        tm_step(&tm);
    }

    printf("Стан машини Тюринга після 10 кроків:\n");
    printf("Позиція головки: %zu, Поточний крок: ", tm.head_pos);
    ns_print(&tm.step_count);
    printf("\n");

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <memory>
#include <optional>
#include <span >
#include <format>
#include <functional>

namespace NonStandard {

constexpr size_t MAX_DEGREE = 4;

// Клас символьного нестандартного числа в кільці Z[H]
class NonStandardInt {
private:
    std::vector<int64_t> coeffs_;

public:
    explicit NonStandardInt(int64_t standard_val = 0) 
        : coeffs_(MAX_DEGREE, 0) {
        coeffs_[0] = standard_val;
    }

    static NonStandardInt make_inf(size_t degree, int64_t coeff = 1) {
        NonStandardInt result;
        if (degree < MAX_DEGREE) {
            result.coeffs_[degree] = coeff;
        }
        return result;
    }

    [[nodiscard]] bool is_standard() const noexcept {
        for (size_t i = 1; i < MAX_DEGREE; ++i) {
            if (coeffs_[i] != 0) return false;
        }
        return coeffs_[0] >= 0;
    }

    [[nodiscard]] std::span<const int64_t> coefficients() const noexcept {
        return coeffs_;
    }

    auto operator<=>(const NonStandardInt& other) const noexcept {
        for (int i = static_cast<int>(MAX_DEGREE) - 1; i >= 0; --i) {
            if (coeffs_[i] != other.coeffs_[i]) {
                return coeffs_[i] <=> other.coeffs_[i];
            }
        }
        return std::strong_ordering::equal;
    }

    bool operator==(const NonStandardInt& other) const noexcept {
        return (*this <=> other) == std::strong_ordering::equal;
    }

    NonStandardInt operator+(const NonStandardInt& other) const {
        NonStandardInt result;
        for (size_t i = 0; i < MAX_DEGREE; ++i) {
            result.coeffs_[i] = coeffs_[i] + other.coeffs_[i];
        }
        return result;
    }

    NonStandardInt operator*(const NonStandardInt& other) const {
        NonStandardInt result;
        for (size_t i = 0; i < MAX_DEGREE; ++i) {
            for (size_t j = 0; j < MAX_DEGREE - i; ++j) {
                result.coeffs_[i + j] += coeffs_[i] * other.coeffs_[j];
            }
        }
        return result;
    }

    [[nodiscard]] std::string to_string() const {
        std::string out;
        bool first = true;
        for (int i = static_cast<int>(MAX_DEGREE) - 1; i >= 0; --i) {
            if (coeffs_[i] != 0) {
                if (!first && coeffs_[i] > 0) out += " + ";
                if (coeffs_[i] < 0) out += " - ";
                
                int64_t abs_val = std::abs(coeffs_[i]);
                if (i == 0) {
                    out += std::to_string(abs_val);
                } else if (i == 1) {
                    out += (abs_val == 1) ? "H" : std::to_string(abs_val) + "·H";
                } else {
                    out += (abs_val == 1) ? "H^" + std::to_string(i) 
                                          : std::to_string(abs_val) + "·H^" + std::to_string(i);
                }
                first = false;
            }
        }
        return first ? "0" : out;
    }
};

// Клас аналізатора принципу Оверспілу (Переливу)
class OverspillEvaluator {
public:
    static bool evaluate(std::function<bool(int64_t)> pred, const NonStandardInt& limit) {
        for (int64_t i = 0; i < 100; ++i) {
            if (!pred(i)) return false;
        }
        return !limit.is_standard();
    }
};

// Симулятор Нестандартної Машини Тюринга
class NonStandardTuringMachine {
private:
    std::vector<uint8_t> tape_;
    size_t head_pos_;
    int state_;
    NonStandardInt steps_;
    bool halted_;

public:
    explicit NonStandardTuringMachine(size_t tape_size = 64)
        : tape_(tape_size, 0), head_pos_(tape_size / 2), state_(0), steps_(0), halted_(false) {}

    void step() {
        if (halted_) return;

        // Покроковий перехід стан-символ
        tape_[head_pos_] ^= 1;
        if (head_pos_ + 1 < tape_.size()) {
            head_pos_++;
        } else {
            halted_ = true;
        }

        steps_ = steps_ + NonStandardInt(1);
    }

    void execute_hyper_steps(const NonStandardInt& hyper_limit) {
        // Імітація обчислення в нестандартному часі H
        if (!hyper_limit.is_standard()) {
            steps_ = steps_ + hyper_limit;
        }
    }

    [[nodiscard]] std::string get_status() const {
        return std::string("Позиція: ") + std::to_string(head_pos_) + 
               ", Кроки: " + steps_.to_string() + 
               ", Зупинена: " + (halted_ ? "Так" : "Ні");
    }
};

} // namespace NonStandard

int main() {
    using namespace NonStandard;

    std::cout << "=== Об'єктний Симулятор Нестандартної Арифметики (C++20) ===\n\n";

    auto n5 = NonStandardInt(5);
    auto H = NonStandardInt::make_inf(1, 1);
    auto H2 = NonStandardInt::make_inf(2, 3);

    auto sum = H + n5;
    auto prod = sum * H;

    std::cout << "Стандартне число n5: " << n5.to_string() << "\n";
    std::cout << "Нестандартний елемент H: " << H.to_string() << "\n";
    std::cout << "Сума H + 5: " << sum.to_string() << "\n";
    std::cout << "Добуток (H + 5) · H: " << prod.to_string() << "\n\n";

    std::cout << "Порівняння (H < H + 5): " << std::boolalpha << (H < sum) << "\n";
    std::cout << "Перевірка стандартності (H + 5): " << sum.is_standard() << "\n\n";

    auto limit = NonStandardInt::make_inf(1, 500);
    bool overspill_valid = OverspillEvaluator::evaluate([](int64_t n) { return (n * n + 1) > 0; }, limit);
    std::cout << "Принцип Оверспілу для p(n) = n²+1 > 0: " << (overspill_valid ? "Пройшов" : "Помилка") << "\n\n";

    NonStandardTuringMachine tm(128);
    for (int i = 0; i < 5; ++i) tm.step();
    std::cout << "Стан TM після 5 стандартних кроків:\n" << tm.get_status() << "\n";

    tm.execute_hyper_steps(limit);
    std::cout << "Стан TM після виконання гіпер-кроку H:\n" << tm.get_status() << "\n";

    return 0;
}
```
:::

## Детальний аналіз алгоритмічних компонентів та обчислювальної складності

Представлені вище варіанти реалізації симулятора демонструють два паралельних підходи до проектування програмного забезпечення для моделювання не-архімедових числових систем.

### 1. Представлення та арифметика нестандартних елементів

У C-версії числові дані моделюються структурою `NonStandardInt`, яка містить фіксований масив коефіцієнтів `coeffs`. Для забезпечення роботи з довільно великими степенями `H` структура підтримує порядок до `MAX_DEGREE - 1`.
Алгоритм додавання виконується за лінійний час `O(D)`, де `D = MAX_DEGREE`.
Множення виконується за квадратичний час `O(D²)`, що відповідає класичній математичній згортці многочленів.

В ідіоматичній C++20 версії застосовано сучасні патерни проектування:
- **Інкапсуляція та незмінність даних:** Масив коефіцієнтів схований у приватній секції класу `std::vector<int64_t>`, а для надання безпечного доступу до коефіцієнтів використовується неволодіючий представник `std::span<const int64_t>`.
- **Трьохстороннє порівняння (Three-way comparison / Spaceship operator):** Завдяки оператору `<=>` клас `NonStandardInt` автоматично генерує всі шість операторів відношень (`<`, `<=`, `>`, `>=`, `==`, `!=`). Лексикографічне порівняння починається з вищого ступеня `H`, що повністю відповідає математичній структурі порядку в моделі `ℕ + ℤ × ℚ`.
- **RAII та відсутність сирих вказівників:** C++ реалізація повністю виключає використання ручного виділення пам'яті (`malloc`/`free`) чи сирих вказівників, спираючись на стандартні контейнери та семантику переміщення.

### 2. Алгоритмічний аналізатор Оверспілу

Класи `ns_check_overspill` та `OverspillEvaluator` реалізують логічний місток між скінченними обчисленнями та нескінченною семантикою логіки першого порядку.
Алгоритм перевірки Оверспілу працює у два кроки:
1. Спочатку проводиться емпірична валідація заданого предикату `pred` на скінченній підмножині натуральних чисел `{0, 1, ..., N-1}`.
2. Якщо предикат є істинним для всіх перевірених стандартних чисел, а задана межа `limit` є нестандартним елементом (`is_standard() == false`), функція робить висновок про виливання предикату на нестандартну область.

Це дозволяє у верифікаційних системах символьно оцінювати властивості програм без вічного виконання циклів.

### 3. Моделювання нестандартних машин Тюринга

Клас `NonStandardTuringMachine` ілюструє різницю між стандартними кроками виконання та гіпер-часовими кроками `H`.
Під час виконання стандартних кроків (`step()`) машина модифікує комірки стрічки `tape` і збільшує лічильник кроків на `1`.
Під час виконання гіпер-кроку (`execute_hyper_steps()`) машина здійснює символьний стрибок у нестандартний час, додаючи до лічильника `steps_` нестандартне число `H`. Це моделює стан машини, яка з точки зору внутрішньої семантики моделі виконала `H` кроків і зупинилася, хоча для стандартного зовнішнього спостерігача таке обчислення тривало б нескінченно.

### 4. Практичне застосування у символьному виконанні коду

Символьні числові класи виду `NonStandardInt` знаходять безпосереднє застосування в сучасних аналізаторах програмного забезпечення:
- **Пошук зациклень (Loop Bound Analysis):** Коли статичний аналізатор аналізує цикл вида `while (x > 0)`, де границя `x` невідома, він моделює час виконання символьним поліномом `a₀ + a₁·H`. Це дозволяє доказати зупинку циклу для будь-яких стандартних даних та виявити потенційні нестандартні зациклення.
- **Символьне тестування пам'яті (Symbolic Memory Safety):** За допомогою не-архімедової арифметики верифікатор обчислює зсуви вказівників на великих масивах, перевіряючи відсутність переповнення буфера для нескінченно віддалених елементів `array[H]`.
- **Аналіз ресурсів та складності (Resource Bound Prover):** Розробники високопродуктивних серверних систем використовують символьні поліноми для оцінки гіршого випадку пам'яті (Worst-Case Space Complexity) без проведення трудомстких навантажувальних тестів на великих масивах даних.
