# ⚙️ Символьний калькулятор кардинальної арифметики на C та C++

Кардинальна арифметика нескінченних множин принципово відрізняється від звичайної арифметики цілих та дійсних чисел. У той час як для скінченних величин додавання та множення збільшують результат (`2 + 3 = 5`, `2 · 3 = 6`), для трансфінітних кардиналів ці операції редукуються до знаходження максимуму:

```
κ + λ = max(κ, λ)    [для нескінченних кардиналів κ, λ]
κ · λ = max(κ, λ)    [для ненульових трансфінітних κ, λ]
```

Натомість операція піднесення до степеня `κ^λ = |A^B|` породжує справжній вибух потужності, розгортаючи нескінченні сходи від зліченної множини `ℵ_0` до континууму `c = 2^ℵ_0 = ℶ_1` та вищих рівнів булеанів.

Нижче спроектовано та реалізовано символьний рушій кардинальної арифметики, який дозволяє представляти трансфінітні кардинали, порівнювати їх між собою та обчислювати точні замкнені значення виразів без втрати точності.

### Архітектура символьного представлення

Комп'ютерне моделювання нескінченностей не може спиратися на числа з рухомою комою чи довгу арифметику, оскільки трансфінітні величини не мають числового еквівалента серед скінченних типів `uint64_t` або `double`. Їх необхідно моделювати як **алгебраїчні типи даних (ADT)** з явним синтаксичним деревом або тегованим об'єднанням.

У нашій системі кардинал `Cardinal` підтримує три ортогональні конструктори:
1. **`FINITE(n)`**: скінченні кардинали (натуральні числа `0, 1, 2, …`), які зберігаються як `uint64_t`. Вони обслуговують звичайну скінченну арифметику та крайові випадки (нульова основа, одиничний степінь).
2. **`ALEPH(α)`**: трансфінітні кардинали Алеф-ієрархії `ℵ_α`. Індекс `α` вказує номер початкового ординала: `ℵ_0` відповідає зліченній потужності натуральних чисел `|ℕ|`, `ℵ_1` — найменшій незліченній потужності, `ℵ_2` — наступному рівню.
3. **`BETH(β)`**: трансфінітні кардинали Бет-ієрархії `ℶ_β`, що виникають через послідовне піднесення двійки до степеня. Зокрема, `ℶ_0 = ℵ_0`, а `ℶ_1 = 2^ℵ_0 = c` представляє потужність континууму (множини дійсних чисел `ℝ`).

Така модель дозволяє представляти як канонічні початкові ординали, так і результати взяття булеана, не прив'язуючись до гіпотези континууму (CH).

### Правила спрощення та алгебраїчні інваріанти

Рушій реалізує повну таблицю редукції кардинальних операцій, засновану на аксіоматиці ZFC:

#### 1. Порівняння кардиналів (`cmp`)
- Будь-який скінченний кардинал строго менший за будь-який нескінченний кардинал:
  `FINITE(n) < ALEPH(α)` та `FINITE(n) < BETH(β)`.
- Кардинали одного типу порівнюються за своїми числовими індексами:
  `ALEPH(α) < ALEPH(β) ⟺ α < β`.
- Базовий зв'язок між ієрархіями: `ℵ_0` тотожний `ℶ_0` (зліченна потужність).
- За теоремою Кантора `2^κ > κ`, тому `ℶ_k ≥ ℵ_k` для всіх індексів.

#### 2. Додавання (`add`)
- Якщо обидва операнди скінченні: обчислюється точна сума `n + m`.
- Якщо один із доданків трансфінітний: скінченний доданок поглинається (`n + κ = κ`).
- Якщо обидва доданки трансфінітні: за теоремою Гессенберґа результат дорівнює їхньому максимуму `max(κ, λ)`.

#### 3. Множення (`mul`)
- Множення на нуль дає нуль: `0 · κ = 0`.
- Добуток скінченних чисел: `n · m`.
- Добуток ненульового скінченного числа та трансфінітного кардинала: `n · κ = κ`.
- Добуток двох трансфінітних кардиналів: `κ · λ = max(κ, λ)`.

#### 4. Піднесення до степеня (`pow`)
Піднесення до степеня містить найбільшу кількість тонких крайових випадків:
- `κ^0 = 1` для будь-якого кардинала (множина функцій із порожньої множини в `A` містить рівно одну функцію — порожню).
- `0^λ = 0` для `λ > 0` (неможливо відобразити непорожню множину в порожню).
- `1^λ = 1` (існує рівно одна функція, що відображає кожен елемент у єдиний елемент `1`).
- Для `n, m ∈ ℕ`: звичайне цілочисельне піднесення `n^m`.
- Якщо основа скінченна `2 ≤ n < ℵ_0`, а показник трансфінітний `ℵ_α`: за правилами кардинальної арифметики `n^ℵ_α = 2^ℵ_α = ℶ_(α+1)`. Зокрема, `2^ℵ_0 = 10^ℵ_0 = ℶ_1 = c`.
- Якщо основа трансфінітна і `κ ≤ λ`, то `κ^λ = 2^λ = ℶ_(λ+1)`. Наприклад, `c^ℵ_0 = (2^ℵ_0)^ℵ_0 = 2^(ℵ_0 · ℵ_0) = 2^ℵ_0 = c`.

### Порівняння реалізацій: C проти C++

У мові C модель реалізовано через класичний підхід із тегованими структурами `struct Cardinal` та явними функціями-конструкторами. Пам'ять розміщується на стеку з нульовими накладними витратами, а порівняння виконується через цілочисельний тризначний індикатор `-1, 0, 1`.

У мові C++ використано сучасні ідіоми стандарту C++20:
- Тип `std::variant<Finite, Aleph, Beth>` забезпечує безпеку типів без використання сирих покажчиків і небезпечного приведення типів.
- Зіставлення шаблонів через `std::visit` та лямбда-вирази з `if constexpr` гарантує вичерпну обробку всіх комбінацій операндів під час компіляції.
- Трибічний оператор порівняння `operator<=>` автоматично генерує повний набір операцій `<, <=, >, >=, ==, !=` з поверненням `std::strong_ordering`.
- Перевантаження операторів `+` та `*` робить синтаксис виразів природним та читабельним.

:::tabs
@tab c
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>

typedef enum {
    CARD_FINITE,
    CARD_ALEPH,
    CARD_BETH
} CardKind;

typedef struct {
    CardKind kind;
    uint64_t val; /* Числове значення для FINITE або індекс для ALEPH/BETH */
} Cardinal;

/* Конструктори кардинальних чисел */
static inline Cardinal card_finite(uint64_t n) {
    return (Cardinal){.kind = CARD_FINITE, .val = n};
}

static inline Cardinal card_aleph(uint64_t idx) {
    return (Cardinal){.kind = CARD_ALEPH, .val = idx};
}

static inline Cardinal card_beth(uint64_t idx) {
    return (Cardinal){.kind = CARD_BETH, .val = idx};
}

static inline Cardinal card_continuum(void) {
    return card_beth(1);
}

/* Тризначне порівняння: -1 (a < b), 0 (a == b), 1 (a > b) */
int cardinal_cmp(Cardinal a, Cardinal b) {
    if (a.kind == CARD_FINITE && b.kind == CARD_FINITE) {
        if (a.val < b.val) return -1;
        if (a.val > b.val) return 1;
        return 0;
    }
    if (a.kind == CARD_FINITE) return -1;
    if (b.kind == CARD_FINITE) return 1;

    /* Спрощення: ℵ_0 тотожний ℶ_0 */
    if (a.val == 0 && b.val == 0) return 0;

    if (a.kind == b.kind) {
        if (a.val < b.val) return -1;
        if (a.val > b.val) return 1;
        return 0;
    }

    /* За теоремою Кантора ℶ_k >= ℵ_k */
    if (a.kind == CARD_ALEPH && b.kind == CARD_BETH) {
        return -1;
    }
    if (a.kind == CARD_BETH && b.kind == CARD_ALEPH) {
        return 1;
    }
    return 0;
}

/* Додавання кардиналів: κ + λ = max(κ, λ) для трансфінітних */
Cardinal cardinal_add(Cardinal a, Cardinal b) {
    if (a.kind == CARD_FINITE && b.kind == CARD_FINITE) {
        return card_finite(a.val + b.val);
    }
    return (cardinal_cmp(a, b) >= 0) ? a : b;
}

/* Множення кардиналів: κ · λ = max(κ, λ) для трансфінітних ненульових */
Cardinal cardinal_mul(Cardinal a, Cardinal b) {
    if (a.kind == CARD_FINITE && a.val == 0) return card_finite(0);
    if (b.kind == CARD_FINITE && b.val == 0) return card_finite(0);
    if (a.kind == CARD_FINITE && b.kind == CARD_FINITE) {
        return card_finite(a.val * b.val);
    }
    return (cardinal_cmp(a, b) >= 0) ? a : b;
}

/* Піднесення до степеня: κ^λ */
Cardinal cardinal_pow(Cardinal base, Cardinal exp) {
    if (exp.kind == CARD_FINITE && exp.val == 0) return card_finite(1);
    if (base.kind == CARD_FINITE && base.val == 0) return card_finite(0);
    if (base.kind == CARD_FINITE && base.val == 1) return card_finite(1);

    if (base.kind == CARD_FINITE && exp.kind == CARD_FINITE) {
        uint64_t res = 1;
        for (uint64_t i = 0; i < exp.val; ++i) res *= base.val;
        return card_finite(res);
    }

    /* n^ℵ_α = ℶ_(α+1) при n >= 2 */
    if (base.kind == CARD_FINITE && base.val >= 2) {
        if (exp.kind == CARD_ALEPH) return card_beth(exp.val + 1);
        if (exp.kind == CARD_BETH)  return card_beth(exp.val + 1);
    }

    /* κ^λ = 2^λ при κ <= λ */
    if (cardinal_cmp(base, exp) <= 0) {
        if (exp.kind == CARD_ALEPH) return card_beth(exp.val + 1);
        if (exp.kind == CARD_BETH)  return card_beth(exp.val + 1);
    }

    return base;
}

void cardinal_print(Cardinal c) {
    switch (c.kind) {
        case CARD_FINITE:
            printf("%" PRIu64, c.val);
            break;
        case CARD_ALEPH:
            printf("Aleph_%" PRIu64, c.val);
            break;
        case CARD_BETH:
            if (c.val == 1) {
                printf("c (Beth_1)");
            } else {
                printf("Beth_%" PRIu64, c.val);
            }
            break;
    }
}

int main(void) {
    Cardinal aleph0 = card_aleph(0);
    Cardinal aleph1 = card_aleph(1);
    Cardinal c = card_continuum();
    Cardinal ten = card_finite(10);
    Cardinal two = card_finite(2);

    printf("1. Aleph_0 + 10 = ");
    cardinal_print(cardinal_add(aleph0, ten));
    printf("\n");

    printf("2. Aleph_0 * Aleph_1 = ");
    cardinal_print(cardinal_mul(aleph0, aleph1));
    printf("\n");

    printf("3. 2 ^ Aleph_0 = ");
    cardinal_print(cardinal_pow(two, aleph0));
    printf("\n");

    printf("4. c ^ Aleph_0 = ");
    cardinal_print(cardinal_pow(c, aleph0));
    printf("\n");

    printf("5. 2 ^ c = ");
    cardinal_print(cardinal_pow(two, c));
    printf("\n");

    return 0;
}
```
@tab cpp
```cpp
#include <iostream>
#include <variant>
#include <cstdint>
#include <string>
#include <compare>
#include <algorithm>

namespace cardinal {

struct Finite { uint64_t value; };
struct Aleph  { uint64_t index; };
struct Beth   { uint64_t index; };

class Cardinal {
public:
    using Repr = std::variant<Finite, Aleph, Beth>;

    constexpr Cardinal(uint64_t val) : repr_(Finite{val}) {}
    constexpr Cardinal(Repr repr) : repr_(repr) {}

    static constexpr Cardinal make_aleph(uint64_t idx) { return Cardinal(Aleph{idx}); }
    static constexpr Cardinal make_beth(uint64_t idx)  { return Cardinal(Beth{idx}); }
    static constexpr Cardinal continuum()             { return Cardinal(Beth{1}); }

    [[nodiscard]] const Repr& data() const noexcept { return repr_; }

    [[nodiscard]] std::string to_string() const {
        return std::visit([](const auto& v) -> std::string {
            using T = std::decay_t<decltype(v)>;
            if constexpr (std::is_same_v<T, Finite>) {
                return std::to_string(v.value);
            } else if constexpr (std::is_same_v<T, Aleph>) {
                return "Aleph_" + std::to_string(v.index);
            } else if constexpr (std::is_same_v<T, Beth>) {
                if (v.index == 1) return "c (Beth_1)";
                return "Beth_" + std::to_string(v.index);
            }
        }, repr_);
    }

    friend auto operator<=>(const Cardinal& lhs, const Cardinal& rhs) noexcept {
        return std::visit([](const auto& x, const auto& y) -> std::strong_ordering {
            using Tx = std::decay_t<decltype(x)>;
            using Ty = std::decay_t<decltype(y)>;

            if constexpr (std::is_same_v<Tx, Finite> && std::is_same_v<Ty, Finite>) {
                return x.value <=> y.value;
            } else if constexpr (std::is_same_v<Tx, Finite>) {
                return std::strong_ordering::less;
            } else if constexpr (std::is_same_v<Ty, Finite>) {
                return std::strong_ordering::greater;
            } else if constexpr (std::is_same_v<Tx, Ty>) {
                return x.index <=> y.index;
            } else if constexpr (std::is_same_v<Tx, Aleph> && std::is_same_v<Ty, Beth>) {
                if (x.index == 0 && y.index == 0) return std::strong_ordering::equal;
                return std::strong_ordering::less;
            } else {
                if (x.index == 0 && y.index == 0) return std::strong_ordering::equal;
                return std::strong_ordering::greater;
            }
        }, lhs.repr_, rhs.repr_);
    }

    friend bool operator==(const Cardinal& lhs, const Cardinal& rhs) noexcept {
        return (lhs <=> rhs) == 0;
    }

private:
    Repr repr_;
};

/* Арифметичні операції */
inline Cardinal operator+(const Cardinal& a, const Cardinal& b) {
    if (std::holds_alternative<Finite>(a.data()) && std::holds_alternative<Finite>(b.data())) {
        return Cardinal(std::get<Finite>(a.data()).value + std::get<Finite>(b.data()).value);
    }
    return (a >= b) ? a : b;
}

inline Cardinal operator*(const Cardinal& a, const Cardinal& b) {
    if (std::holds_alternative<Finite>(a.data()) && std::get<Finite>(a.data()).value == 0) return Cardinal(0);
    if (std::holds_alternative<Finite>(b.data()) && std::get<Finite>(b.data()).value == 0) return Cardinal(0);

    if (std::holds_alternative<Finite>(a.data()) && std::holds_alternative<Finite>(b.data())) {
        return Cardinal(std::get<Finite>(a.data()).value * std::get<Finite>(b.data()).value);
    }
    return (a >= b) ? a : b;
}

inline Cardinal power(const Cardinal& base, const Cardinal& exp) {
    if (std::holds_alternative<Finite>(exp.data()) && std::get<Finite>(exp.data()).value == 0) return Cardinal(1);
    if (std::holds_alternative<Finite>(base.data()) && std::get<Finite>(base.data()).value == 0) return Cardinal(0);
    if (std::holds_alternative<Finite>(base.data()) && std::get<Finite>(base.data()).value == 1) return Cardinal(1);

    if (std::holds_alternative<Finite>(base.data()) && std::holds_alternative<Finite>(exp.data())) {
        uint64_t b = std::get<Finite>(base.data()).value;
        uint64_t e = std::get<Finite>(exp.data()).value;
        uint64_t res = 1;
        for (uint64_t i = 0; i < e; ++i) res *= b;
        return Cardinal(res);
    }

    if (std::holds_alternative<Finite>(base.data()) && std::get<Finite>(base.data()).value >= 2) {
        if (std::holds_alternative<Aleph>(exp.data())) {
            return Cardinal::make_beth(std::get<Aleph>(exp.data()).index + 1);
        }
        if (std::holds_alternative<Beth>(exp.data())) {
            return Cardinal::make_beth(std::get<Beth>(exp.data()).index + 1);
        }
    }

    if (base <= exp) {
        if (std::holds_alternative<Aleph>(exp.data())) {
            return Cardinal::make_beth(std::get<Aleph>(exp.data()).index + 1);
        }
        if (std::holds_alternative<Beth>(exp.data())) {
            return Cardinal::make_beth(std::get<Beth>(exp.data()).index + 1);
        }
    }

    return base;
}

} // namespace cardinal

int main() {
    using namespace cardinal;

    auto aleph0 = Cardinal::make_aleph(0);
    auto aleph1 = Cardinal::make_aleph(1);
    auto c = Cardinal::continuum();
    auto ten = Cardinal(10);
    auto two = Cardinal(2);

    std::cout << "1. Aleph_0 + 10 = " << (aleph0 + ten).to_string() << "\n";
    std::cout << "2. Aleph_0 * Aleph_1 = " << (aleph0 * aleph1).to_string() << "\n";
    std::cout << "3. 2 ^ Aleph_0 = " << power(two, aleph0).to_string() << "\n";
    std::cout << "4. c ^ Aleph_0 = " << power(c, aleph0).to_string() << "\n";
    std::cout << "5. 2 ^ c = " << power(two, c).to_string() << "\n";

    return 0;
}
```
:::

### Покроковий аналіз результатів тестування

Розглянемо вивід наведеної програми та детально простежимо внутрішню механіку кожного обчислення:

1. **`Aleph_0 + 10 = Aleph_0`**:
   Скінченний доданок `10` порівнюється з `ℵ_0`. Оскільки будь-який скінченний кардинал менший за трансфінітний, спрацьовує правило `max(10, ℵ_0) = ℵ_0`. У теоретико-множинному сенсі це відповідає готелю Гільберта: додавання скінченної кількості гостей до нескінченної кількості зайнятих номерів не вимагає побудови нового готелю — достатньо зсунути кожного мешканця на 10 кімнат уперед.

2. **`Aleph_0 * Aleph_1 = Aleph_1`**:
   Множення зліченного кардинала `ℵ_0` на найменший незліченний кардинал `ℵ_1`. За теоремою Гессенберґа декартовий добуток двох нескінченних множин має потужність старшого множника: `ℵ_0 · ℵ_1 = max(ℵ_0, ℵ_1) = ℵ_1`. Об'єднання зліченної родини множин потужності `ℵ_1` не виходить за межі `ℵ_1`.

3. **`2 ^ Aleph_0 = c (Beth_1)`**:
   Піднесення двійки до зліченного степеня. Множина всіх нескінченних бітових послідовностей `{0, 1}^ℕ` за теоремою Кантора має потужність строго більшу за `ℵ_0`. Вона визначає перший рівень Бет-ієрархії `ℶ_1`, який тотожний потужності континууму `c` (множині дійсних чисел `ℝ`).

4. **`c ^ Aleph_0 = c (Beth_1)`**:
   Обчислення потужності множини всіх послідовностей дійсних чисел `ℝ^ℕ`. Застосовуючи кардинальну алгебру степенів:
   ```
   c^ℵ_0 = (2^ℵ_0)^ℵ_0 = 2^(ℵ_0 · ℵ_0) = 2^ℵ_0 = c
   ```
   Потужність простору всіх збіжних і розбіжних числових послідовностей не перевищує потужність однієї числової прямої: дійсних послідовностей рівно стільки ж, скільки самих дійсних чисел.

5. **`2 ^ c = Beth_2`**:
   Піднесення двійки до степеня континууму. Множина всіх підмножин числової прямої `P(ℝ)` або множина всіх довільних функцій `ℝ → ℝ` має потужність `ℶ_2 = 2^c`. Це строго більша нескінченність, ніж континуум, яка не може бути бієктивно зіставлена з точками геометричного простору `ℝⁿ`.

### Оцінка складності та інваріанти пам'яті

Розроблений алгоритм має такі обчислювальні характеристики:
- **Часова складність**: усі операції порівняння, додавання та множення виконуються за константний час `O(1)`, оскільки зводяться до побітових операцій та порівняння 64-бітних цілих чисел. Операція піднесення до степеня для скінченних чисел займає `O(exp)` множень, а для трансфінітних — `O(1)` конструювання дескриптора.
- **Просторова складність**: `O(1)` пам'яті на стеку. Ані C-, ані C++-версії не виконують динамічного виділення пам'яті на купі (`heap`) і не потребують механізмів збирання сміття. Розмір структури становить 16 байтів у C та 24 байти у C++ (з урахуванням вирівнювання тегу `std::variant`).
- **Стійкість до переповнення**: оскільки індекси алефів та бетів зберігаються як цілі числа `uint64_t`, переповнення можливе лише при роботі з астрономічними вежами степенів глибиною понад `2^64` шарів, що багаторазово перекриває будь-які практичні потреби комп'ютерної логіки.
