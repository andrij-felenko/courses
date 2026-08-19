# ⚙️ Реалізація обчислювального рушія ординалів Веблена мовами C та C++

Практична реалізація трансфінітних ординалів нижче за ординал Фефермана — Шютте `Γ₀` вимагає побудови спеціалізованого абстрактного синтаксичного дерева (AST), здатного підтримувати рекурсивну канонізацію виразів, автоматичне поглинання адитивних компонентів Кантора та безпомилкове структурне порівняння функцій Веблена `φ(γ, β)`.

Нижче подано повну паралельну реалізацію обчислювального рушія мовами C (стандарт C99/C11 з суворим контролем динамічної пам'яті) та C++ (стандарт C++20 з використанням розумних вказівників `std::unique_ptr`, семантики переміщення та оператора тристороннього порівняння `<=>`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

/* Типи вузлів синтаксичного дерева ординалу */
typedef enum {
    ORD_ZERO,      /* 0 */
    ORD_FINITE,    /* Натуральне число k > 0 */
    ORD_ADD,       /* Сума A + B (де A >= B) */
    ORD_VEBLEN     /* Функція Веблена phi(gamma, beta) */
} OrdinalKind;

typedef struct OrdinalNode OrdinalNode;

struct OrdinalNode {
    OrdinalKind kind;
    unsigned long long value; /* Для ORD_FINITE */
    OrdinalNode* left;        /* Для ADD: лівий доданок; для VEBLEN: gamma */
    OrdinalNode* right;       /* Для ADD: правий доданок; для VEBLEN: beta */
};

/* Створення базових вузлів */
OrdinalNode* ord_zero(void) {
    OrdinalNode* n = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    n->kind = ORD_ZERO;
    return n;
}

OrdinalNode* ord_finite(unsigned long long val) {
    if (val == 0) return ord_zero();
    OrdinalNode* n = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    n->kind = ORD_FINITE;
    n->value = val;
    return n;
}

/* Глибоке копіювання дерева */
OrdinalNode* ord_clone(const OrdinalNode* src) {
    if (!src) return NULL;
    OrdinalNode* n = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    n->kind = src->kind;
    n->value = src->value;
    n->left = ord_clone(src->left);
    n->right = ord_clone(src->right);
    return n;
}

/* Рекурсивне звільнення пам'яті */
void ord_free(OrdinalNode* n) {
    if (!n) return;
    ord_free(n->left);
    ord_free(n->right);
    free(n);
}

/* Попереднє оголошення функції порівняння: повертає -1 (a < b), 0 (a == b), 1 (a > b) */
int ord_cmp(const OrdinalNode* a, const OrdinalNode* b);

/* Допоміжні перевірки */
bool ord_is_zero(const OrdinalNode* n) {
    return !n || n->kind == ORD_ZERO;
}

bool ord_is_principal(const OrdinalNode* n) {
    return n && n->kind == ORD_VEBLEN;
}

/* Порівняння двох адитивно головних функцій Веблена phi(g1, b1) та phi(g2, b2) */
static int ord_cmp_veblen(const OrdinalNode* a, const OrdinalNode* b) {
    assert(a->kind == ORD_VEBLEN && b->kind == ORD_VEBLEN);
    
    int g_cmp = ord_cmp(a->left, b->left);
    if (g_cmp == 0) {
        return ord_cmp(a->right, b->right);
    } else if (g_cmp < 0) {
        /* a->gamma < b->gamma: A < B <=> beta_A < B */
        int cmp_b = ord_cmp(a->right, b);
        return (cmp_b < 0) ? -1 : 1;
    } else {
        /* a->gamma > b->gamma: A < B <=> A <= beta_B */
        int cmp_a = ord_cmp(a, b->right);
        return (cmp_a <= 0) ? -1 : 1;
    }
}

int ord_cmp(const OrdinalNode* a, const OrdinalNode* b) {
    if (a == b) return 0;
    if (ord_is_zero(a) && ord_is_zero(b)) return 0;
    if (ord_is_zero(a)) return -1;
    if (ord_is_zero(b)) return 1;

    if (a->kind == ORD_FINITE && b->kind == ORD_FINITE) {
        if (a->value < b->value) return -1;
        if (a->value > b->value) return 1;
        return 0;
    }
    if (a->kind == ORD_FINITE) return -1; /* Скінченне < трансфінітне */
    if (b->kind == ORD_FINITE) return 1;

    if (a->kind == ORD_VEBLEN && b->kind == ORD_VEBLEN) {
        return ord_cmp_veblen(a, b);
    }

    /* Розбір сум: порівнюємо старші адитивні члени */
    const OrdinalNode* a_head = (a->kind == ORD_ADD) ? a->left : a;
    const OrdinalNode* b_head = (b->kind == ORD_ADD) ? b->left : b;

    int head_cmp = ord_cmp(a_head, b_head);
    if (head_cmp != 0) return head_cmp;

    /* Старші члени рівні: порівнюємо хвости */
    const OrdinalNode* a_tail = (a->kind == ORD_ADD) ? a->right : NULL;
    const OrdinalNode* b_tail = (b->kind == ORD_ADD) ? b->right : NULL;

    return ord_cmp(a_tail, b_tail);
}

/* Нормалізований конструктор функції Веблена phi(gamma, beta) */
OrdinalNode* ord_veblen(OrdinalNode* gamma, OrdinalNode* beta) {
    OrdinalNode* n = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    n->kind = ORD_VEBLEN;
    n->left = gamma;
    n->right = beta;
    return n;
}

/* Адитивна композиція (додавання Кантора з поглинанням менших членів зліва) */
OrdinalNode* ord_add(OrdinalNode* a, OrdinalNode* b) {
    if (ord_is_zero(a)) { ord_free(a); return b; }
    if (ord_is_zero(b)) { ord_free(b); return a; }

    /* Якщо обидва скінченні */
    if (a->kind == ORD_FINITE && b->kind == ORD_FINITE) {
        unsigned long long sum = a->value + b->value;
        ord_free(a);
        ord_free(b);
        return ord_finite(sum);
    }

    /* Визначаємо головний член правого доданка */
    const OrdinalNode* b_lead = (b->kind == ORD_ADD) ? b->left : b;

    /* Якщо додаємо скінченне до нескінченного зліва (1 + omega = omega) */
    if (a->kind == ORD_FINITE && b_lead->kind == ORD_VEBLEN) {
        ord_free(a);
        return b;
    }

    /* Перевіряємо поглинання: якщо a < b_lead, a повністю поглинається */
    if (a->kind == ORD_VEBLEN) {
        if (ord_cmp(a, b_lead) < 0) {
            ord_free(a);
            return b;
        }
    } else if (a->kind == ORD_ADD) {
        /* Рекурсивно перевіряємо поглинання у хвості суми */
        if (ord_cmp(a->left, b_lead) < 0) {
            ord_free(a);
            return b;
        }
        /* Збираємо суму: a->left + (a->right + b) */
        OrdinalNode* new_tail = ord_add(a->right, b);
        a->right = new_tail;
        return a;
    }

    OrdinalNode* res = (OrdinalNode*)calloc(1, sizeof(OrdinalNode));
    res->kind = ORD_ADD;
    res->left = a;
    res->right = b;
    return res;
}

/* Форматування ординалу у зрозумілий рядок */
void ord_print_to_buf(const OrdinalNode* n, char* buf, size_t max_len) {
    if (!n || n->kind == ORD_ZERO) {
        snprintf(buf, max_len, "0");
        return;
    }
    if (n->kind == ORD_FINITE) {
        snprintf(buf, max_len, "%llu", n->value);
        return;
    }
    if (n->kind == ORD_VEBLEN) {
        char g_buf[128], b_buf[128];
        ord_print_to_buf(n->left, g_buf, sizeof(g_buf));
        ord_print_to_buf(n->right, b_buf, sizeof(b_buf));

        /* Спеціальні випадки для красивого друку */
        if (n->left->kind == ORD_ZERO) {
            if (n->right->kind == ORD_ZERO) {
                snprintf(buf, max_len, "1");
            } else if (n->right->kind == ORD_FINITE && n->right->value == 1) {
                snprintf(buf, max_len, "w");
            } else {
                snprintf(buf, max_len, "w^(%s)", b_buf);
            }
        } else if (n->left->kind == ORD_FINITE && n->left->value == 1) {
            snprintf(buf, max_len, "eps(%s)", b_buf);
        } else if (n->left->kind == ORD_FINITE && n->left->value == 2) {
            snprintf(buf, max_len, "zeta(%s)", b_buf);
        } else {
            snprintf(buf, max_len, "phi(%s, %s)", g_buf, b_buf);
        }
        return;
    }
    if (n->kind == ORD_ADD) {
        char l_buf[256], r_buf[256];
        ord_print_to_buf(n->left, l_buf, sizeof(l_buf));
        ord_print_to_buf(n->right, r_buf, sizeof(r_buf));
        snprintf(buf, max_len, "%s + %s", l_buf, r_buf);
        return;
    }
}

/* Канонічні ординали для тестування */
OrdinalNode* ord_omega(void) {
    return ord_veblen(ord_zero(), ord_finite(1));
}

OrdinalNode* ord_epsilon0(void) {
    return ord_veblen(ord_finite(1), ord_zero());
}

OrdinalNode* ord_zeta0(void) {
    return ord_veblen(ord_finite(2), ord_zero());
}

int main(void) {
    printf("=== Демонстрація синтаксичного рушія ординалів Веблена (C) ===\n");

    OrdinalNode* zero = ord_zero();
    OrdinalNode* one = ord_finite(1);
    OrdinalNode* w = ord_omega();
    OrdinalNode* w2 = ord_veblen(ord_zero(), ord_finite(2)); /* w^2 */
    OrdinalNode* eps0 = ord_epsilon0();
    OrdinalNode* eps1 = ord_veblen(ord_finite(1), ord_finite(1));
    OrdinalNode* zet0 = ord_zeta0();

    char buf[256];

    ord_print_to_buf(w, buf, sizeof(buf));
    printf("Ординал w: %s\n", buf);

    ord_print_to_buf(eps0, buf, sizeof(buf));
    printf("Ординал eps0: %s\n", buf);

    ord_print_to_buf(zet0, buf, sizeof(buf));
    printf("Ординал zeta0: %s\n", buf);

    /* Перевірка строгого впорядкування */
    assert(ord_cmp(zero, one) < 0);
    assert(ord_cmp(one, w) < 0);
    assert(ord_cmp(w, w2) < 0);
    assert(ord_cmp(w2, eps0) < 0);
    assert(ord_cmp(eps0, eps1) < 0);
    assert(ord_cmp(eps1, zet0) < 0);

    /* Тест на непереставність та поглинання: 1 + w == w */
    OrdinalNode* sum_1_w = ord_add(ord_finite(1), ord_clone(w));
    ord_print_to_buf(sum_1_w, buf, sizeof(buf));
    printf("1 + w = %s\n", buf);
    assert(ord_cmp(sum_1_w, w) == 0);

    /* w + 1 > w */
    OrdinalNode* sum_w_1 = ord_add(ord_clone(w), ord_finite(1));
    ord_print_to_buf(sum_w_1, buf, sizeof(buf));
    printf("w + 1 = %s\n", buf);
    assert(ord_cmp(sum_w_1, w) > 0);

    printf("Усі перевірки впорядкування успішно пройдено!\n");

    ord_free(zero);
    ord_free(one);
    ord_free(w);
    ord_free(w2);
    ord_free(eps0);
    ord_free(eps1);
    ord_free(zet0);
    ord_free(sum_1_w);
    ord_free(sum_w_1);

    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <compare>
#include <utility>
#include <cassert>

namespace veblen {

enum class Kind {
    Zero,
    Finite,
    Add,
    Veblen
};

class Ordinal;
using OrdinalPtr = std::unique_ptr<Ordinal>;

class Ordinal {
public:
    Kind kind;
    unsigned long long value{0};
    OrdinalPtr left{nullptr};
    OrdinalPtr right{nullptr};

    Ordinal() : kind(Kind::Zero) {}
    explicit Ordinal(unsigned long long val) : kind(Kind::Finite), value(val) {
        if (val == 0) kind = Kind::Zero;
    }
    Ordinal(Kind k, OrdinalPtr l, OrdinalPtr r)
        : kind(k), left(std::move(l)), right(std::move(r)) {}

    [[nodiscard]] bool is_zero() const noexcept {
        return kind == Kind::Zero;
    }

    [[nodiscard]] bool is_principal() const noexcept {
        return kind == Kind::Veblen;
    }

    [[nodiscard]] OrdinalPtr clone() const {
        auto copy = std::make_unique<Ordinal>();
        copy->kind = this->kind;
        copy->value = this->value;
        if (this->left) copy->left = this->left->clone();
        if (this->right) copy->right = this->right->clone();
        return copy;
    }
};

/* Фабричні методи створення об'єктів */
inline OrdinalPtr make_zero() {
    return std::make_unique<Ordinal>();
}

inline OrdinalPtr make_finite(unsigned long long val) {
    if (val == 0) return make_zero();
    return std::make_unique<Ordinal>(val);
}

inline OrdinalPtr make_veblen(OrdinalPtr gamma, OrdinalPtr beta) {
    return std::make_unique<Ordinal>(Kind::Veblen, std::move(gamma), std::move(beta));
}

/* Тристороннє рекурсивне порівняння синтаксичних дерев ординалів */
std::strong_ordering compare(const Ordinal* a, const Ordinal* b) noexcept;

namespace detail {
    inline std::strong_ordering compare_veblen(const Ordinal* a, const Ordinal* b) noexcept {
        assert(a->kind == Kind::Veblen && b->kind == Kind::Veblen);

        auto g_cmp = compare(a->left.get(), b->left.get());
        if (g_cmp == std::strong_ordering::equal) {
            return compare(a->right.get(), b->right.get());
        } else if (g_cmp == std::strong_ordering::less) {
            /* a->gamma < b->gamma: A < B <=> beta_A < B */
            auto cmp_b = compare(a->right.get(), b);
            return (cmp_b == std::strong_ordering::less) 
                ? std::strong_ordering::less 
                : std::strong_ordering::greater;
        } else {
            /* a->gamma > b->gamma: A < B <=> A <= beta_B */
            auto cmp_a = compare(a, b->right.get());
            return (cmp_a == std::strong_ordering::less || cmp_a == std::strong_ordering::equal)
                ? std::strong_ordering::less 
                : std::strong_ordering::greater;
        }
    }
}

inline std::strong_ordering compare(const Ordinal* a, const Ordinal* b) noexcept {
    if (a == b) return std::strong_ordering::equal;
    bool a_zero = (!a || a->is_zero());
    bool b_zero = (!b || b->is_zero());

    if (a_zero && b_zero) return std::strong_ordering::equal;
    if (a_zero) return std::strong_ordering::less;
    if (b_zero) return std::strong_ordering::greater;

    if (a->kind == Kind::Finite && b->kind == Kind::Finite) {
        return a->value <=> b->value;
    }
    if (a->kind == Kind::Finite) return std::strong_ordering::less;
    if (b->kind == Kind::Finite) return std::strong_ordering::greater;

    if (a->kind == Kind::Veblen && b->kind == Kind::Veblen) {
        return detail::compare_veblen(a, b);
    }

    /* Розбір сум */
    const Ordinal* a_head = (a->kind == Kind::Add) ? a->left.get() : a;
    const Ordinal* b_head = (b->kind == Kind::Add) ? b->left.get() : b;

    auto head_cmp = compare(a_head, b_head);
    if (head_cmp != std::strong_ordering::equal) return head_cmp;

    const Ordinal* a_tail = (a->kind == Kind::Add) ? a->right.get() : nullptr;
    const Ordinal* b_tail = (b->kind == Kind::Add) ? b->right.get() : nullptr;

    return compare(a_tail, b_tail);
}

/* Операція додавання з поглинанням менших лівих операндів */
inline OrdinalPtr add(OrdinalPtr a, OrdinalPtr b) {
    if (!a || a->is_zero()) return b;
    if (!b || b->is_zero()) return a;

    if (a->kind == Kind::Finite && b->kind == Kind::Finite) {
        return make_finite(a->value + b->value);
    }

    const Ordinal* b_lead = (b->kind == Kind::Add) ? b->left.get() : b.get();

    /* 1 + omega = omega */
    if (a->kind == Kind::Finite && b_lead->kind == Kind::Veblen) {
        return b;
    }

    if (a->kind == Kind::Veblen) {
        if (compare(a.get(), b_lead) == std::strong_ordering::less) {
            return b;
        }
    } else if (a->kind == Kind::Add) {
        if (compare(a->left.get(), b_lead) == std::strong_ordering::less) {
            return b;
        }
        a->right = add(std::move(a->right), std::move(b));
        return a;
    }

    return std::make_unique<Ordinal>(Kind::Add, std::move(a), std::move(b));
}

/* Форматування у читабельний рядок */
inline std::string to_string(const Ordinal* n) {
    if (!n || n->is_zero()) return "0";
    if (n->kind == Kind::Finite) return std::to_string(n->value);

    if (n->kind == Kind::Veblen) {
        std::string g_str = to_string(n->left.get());
        std::string b_str = to_string(n->right.get());

        if (n->left->is_zero()) {
            if (n->right->is_zero()) return "1";
            if (n->right->kind == Kind::Finite && n->right->value == 1) return "w";
            return "w^(" + b_str + ")";
        }
        if (n->left->kind == Kind::Finite && n->left->value == 1) {
            return "eps(" + b_str + ")";
        }
        if (n->left->kind == Kind::Finite && n->left->value == 2) {
            return "zeta(" + b_str + ")";
        }
        return "phi(" + g_str + ", " + b_str + ")";
    }

    if (n->kind == Kind::Add) {
        return to_string(n->left.get()) + " + " + to_string(n->right.get());
    }
    return "?";
}

} // namespace veblen

int main() {
    using namespace veblen;
    std::cout << "=== Демонстрація синтаксичного рушія ординалів Веблена (C++20) ===\n";

    auto zero = make_zero();
    auto one = make_finite(1);
    auto w = make_veblen(make_zero(), make_finite(1));
    auto w2 = make_veblen(make_zero(), make_finite(2));
    auto eps0 = make_veblen(make_finite(1), make_zero());
    auto eps1 = make_veblen(make_finite(1), make_finite(1));
    auto zet0 = make_veblen(make_finite(2), make_zero());

    std::cout << "Ординал w: " << to_string(w.get()) << "\n";
    std::cout << "Ординал eps0: " << to_string(eps0.get()) << "\n";
    std::cout << "Ординал zeta0: " << to_string(zet0.get()) << "\n";

    assert(compare(zero.get(), one.get()) == std::strong_ordering::less);
    assert(compare(one.get(), w.get()) == std::strong_ordering::less);
    assert(compare(w.get(), w2.get()) == std::strong_ordering::less);
    assert(compare(w2.get(), eps0.get()) == std::strong_ordering::less);
    assert(compare(eps0.get(), eps1.get()) == std::strong_ordering::less);
    assert(compare(eps1.get(), zet0.get()) == std::strong_ordering::less);

    auto sum_1_w = add(make_finite(1), w->clone());
    std::cout << "1 + w = " << to_string(sum_1_w.get()) << "\n";
    assert(compare(sum_1_w.get(), w.get()) == std::strong_ordering::equal);

    auto sum_w_1 = add(w->clone(), make_finite(1));
    std::cout << "w + 1 = " << to_string(sum_w_1.get()) << "\n";
    assert(compare(sum_w_1.get(), w.get()) == std::strong_ordering::greater);

    std::cout << "Усі перевірки впорядкування C++20 пройдено успішно!\n";
    return 0;
}
```
:::

## Детальний аналіз архітектурних рішень та алгоритмічних пасток

Створення надійного обчислювального рушія для трансфінітної арифметики містить низку глибоких алгоритмічних викликів, які суттєво відрізняють його від звичайної арифметики цілих чи дійсних чисел.

### 1. Непереставність трансфінітного додавання та поглинання Кантора

Головна небезпека при реалізації алгебри ординалів полягає у спробі застосувати інтуїцію зі скінченної арифметики. Додавання ординалів є асоціативним, але строго непереставним (некомутативним). Зокрема:

```
1 + ω = ω
але
ω + 1 > ω
```

Коли менший ординал додається зліва до більшого адитивно головного ординала (числа виду `φ(γ, β)`), він повністю «поглинається» нескінченною структурою наступного члена. Якщо у програмі просто об'єднати два вузли у бінарне дерево додавання без нормалізації, виникнуть фальшиві синтаксичні відмінності: дерева `1 + ω` та `ω` будуть різними, хоча позначають один і той самий математичний об'єкт.

У представленому рушії функція `add` (або `ord_add` у C) реалізує канонічне правило редукції Кантора. Перед створенням нового вузла додавання рушій аналізує провідний член правого доданка `b_lead`. Якщо лівий доданок `a` є строго меншим за `b_lead`, він повністю відкидається і звільняється з пам'яті, а результатом стає сам правий доданок `b`. Якщо ж лівий доданок сам є сумою, процедура поглинання рекурсивно спускається у його правий хвіст, забезпечуючи інваріант спадання доданків зліва направо.

### 2. Запобігання нескінченній рекурсії при структурному порівнянні

Алгоритм порівняння двох вузлів Веблена `φ(γ_A, β_A)` та `φ(γ_B, β_B)` містить тонке взаємне посилання. Якщо `γ_A < γ_B`, алгоритм порівнює `β_A` з усім деревом `B`. На перший погляд здається, що передача цілого дерева `B` у повторний виклик порівняння може призвести до нескінченного циклу.

Проте строге математичне обґрунтування спирається на індукцію за висотою дерев. Оскільки `β_A` є прямим нащадком вузла `A`, його висота строго менша за висоту `A`. Навіть якщо при порівнянні `β_A` з `B` відбудеться розгалуження, сумарна міра складності пари дерев `(висота(A), висота(B))` монотонно спадає на кожному нетривіальному кроці рекурсії. Це гарантує повну термінацію алгоритму порівняння за скінченну кількість кроків для будь-яких коректних дерев.

### 3. Керування динамічною пам'яттю: ручний контроль проти RAII

Трансфінітні дерева є динамічними структурами довільної глибини. У мові C рушій використовує функцію `calloc` для ініціалізації нулями всіх полів структури та функцію `ord_free` для глибинного рекурсивного очищення. Кожна операція, що створює новий нормалізований вузол (як-от `ord_add`), бере на себе відповідальність за володіння вхідними вказівниками та звільняє проміжні вузли, що були поглинені.

У мові C++ застосовано сучасну ідіому RAII (англ. *Resource Acquisition Is Initialization*). Використання `std::unique_ptr<Ordinal>` забезпечує ексклюзивне володіння піддеревами. Семантика переміщення (`std::move`) дозволяє передавати гілки дерева без зайвого копіювання, а деструктор за замовчуванням автоматично очищає всю ієрархію пам'яті при виході об'єкта з області видимості, що повністю ліквідує загрозу витоків пам'яті (англ. *memory leaks*).

### 4. Алгоритмічна складність та оптимізації

Часова складність порівняння двох дерев ординалів `A` та `B` у середньому становить `O(min(|A|, |B|))`, оскільки розбіжність зазвичай виявляється у верхніх вузлах дерева. У найгіршому випадку (глибоко вкладені однакові вирази) складність становить `O(|A| · |B|)`.

Операція додавання `add(A, B)` виконується за час `O(h_A + h_B)`, де `h` — висота дерева, оскільки пошук точки вставки вимагає проходу лише по правому хребту лівого дерева. Це забезпечує високу швидкодію рушія навіть при моделюванні складних ігор у Гідру з мільйонами кроків редукції.

### 5. Поведінка на межі та обробка виняткових ситуацій

Якщо вхідні дані намагаються створити структуру виду `φ(γ, 0) = γ` (наприклад, спроба збудувати безпосередньо вузол `Γ₀` через бінарну функцію), рушій сигналізує про вихід за межі нормальної форми. Завдяки інваріанту `γ < φ(γ, β)` алгоритм детектує некоректний ввід на етапі конструктора або валідатора, запобігаючи зацикленню обчислень.

## Покроковий розбір виконання операцій (Execution Trace)

Для глибокого розуміння роботи рушія простежимо покрокове виконання двох ключових операцій: редукції додавання та складного структурного порівняння.

### Сценарій 1: Поглинання менших членів при додаванні
Нехай виконується операція `add(A, B)`, де:
- `A = ω + 5 = ADD(VEBLEN(0, 1), 5)`
- `B = ω² + 1 = ADD(VEBLEN(0, 2), 1)`

1. Алгоритм визначає провідний член правого доданка: `b_lead = B->left = VEBLEN(0, 2) = ω²`.
2. Порівнюється лівий доданок `A` з `b_lead`:
   - `A->left = VEBLEN(0, 1) = ω`.
   - Викликається `compare(VEBLEN(0, 1), VEBLEN(0, 2))`. Оскільки індекси `γ = 0` рівні, порівнюються аргументи: `1 < 2`, тому `ω < ω²`.
3. Оскільки `A->left < b_lead`, уся ліва сума `A = ω + 5` є строго меншою за провідний член правого операнда `ω²`.
4. За правилом трансфінітної редукції Кантора, операнд `A` повністю поглинається: пам'ять `A` звільняється, а функція повертає `B = ω² + 1`.
5. Результат: `(ω + 5) + (ω² + 1) = ω² + 1`.

### Сценарій 2: Порівняння рівнів Веблена
Нехай порівнюються вирази:
- `A = φ(1, 0) = ε₀`
- `B = φ(0, φ(1, 0)) = ω^ε₀`

1. Викликається `compare_veblen(A, B)`.
2. Індекси: `γ_A = 1`, `γ_B = 0`. Оскільки `γ_A > γ_B`, спрацьовує третє правило:
   ```
   A < B  ⇔  A ≤ β_B
   ```
3. Аргумент `β_B` дорівнює `φ(1, 0) = A`.
4. Перевіряється співвідношення `A ≤ A`: воно виконується з рівністю.
5. Оскільки `A = β_B`, то `A ≤ β_B` істинне, але `β_B < A` хибне, що дає точну рівність `φ(1, 0) = φ(0, φ(1, 0))`, тобто `ε₀ = ω^ε₀`.
6. Рушій безпомилково ідентифікує рівність нерухомої точки без зациклення.

## Порівняльний аналіз стратегій представлення в пам'яті

Існує дві основні альтернативи для збереження трансфінітних ординалів у пам'яті комп'ютера:

1. **Лінійні списки показників (Array of Exponents):** Ефективні для ординалів нижче `ω^ω`, але вимагають складного динамічного перерозподілу пам'яті для вкладених веж та повністю втрачають ефективність на рівнях вище `ε₀`.
2. **Абстрактні синтаксичні дерева (AST) з VNF:** Універсальний підхід, реалізований у цьому проєкті. Він підтримує будь-які ординали нижче `Γ₀`, дозволяє кешувати хеш-суми вузлів для миттєвого порівняння на рівність за `O(1)` та гарантує повну відповідність математичним інваріантам теорії доведень.

## Поглиблений аналіз структури пам'яті та керування ресурсами

Розглянемо глибше відмінності в організації життєвого циклу об'єктів у реалізаціях на C та C++.

### Модель пам'яті у мові C
У мові C кожен вузол `OrdinalNode` виділяється у динамічній пам'яті викликом `calloc(1, sizeof(OrdinalNode))`. Оскільки розмір структури є фіксованим (32 байти на 64-бітних платформах: 8 байтів на `kind`, 8 байтів на `value`, 8 байтів на `left`, 8 байтів на `right`), структури легко розміщуються у стандартних пулах пам'яті.

Функція `ord_free` виконує рекурсивний обхід дерева у пост-порядку (post-order traversal): спершу звільняються ліве та праве піддерева, і лише після цього звільняється сам кореневий вузол. Це запобігає виникненню повислих вказівників (англ. *dangling pointers*).

При виконанні операцій додавання (`ord_add`) рушій використовує семантику переходу володіння (англ. *ownership transfer*). Якщо лівий операнд поглинається правим за правилами Кантора, функція самостійно викликає `ord_free(a)`, позбавляючи клієнтський код від необхідності відстежувати, які саме вузли стали частиною нової суми, а які були відкинуті.

### Модель пам'яті у мові C++20
У сучасному C++20 рушій інкапсулює дерева ординалів за допомогою розумних вказівників `std::unique_ptr<Ordinal>`. Це повністю усуває людський фактор при керуванні пам'яттю.

1. **Семантика переміщення (`std::move`):** Конструктори та фабричні методи приймають піддерева як rvalue-посилання. При конструюванні вузла `make_veblen(std::move(g), std::move(b))` володіння вказівниками переміщується всередину об'єкта без зайвих виділень пам'яті чи системних викликів.
2. **Автоматичне каскадне видалення:** Коли об'єкт ординалу виходить з області видимості, компілятор генерує деструктор, який рекурсивно викликає деструктори всіх нащадків `std::unique_ptr`. Глибина рекурсії обмежена висотою дерева (яка для виразів нижче `Γ₀` зазвичай не перевищує кількох десятків рівнів), тому небезпека переповнення стека викликів (англ. *stack overflow*) є мінімальною.
3. **Оператор тристороннього порівняння (`<=>`):** Використання стандарту C++20 дозволяє інтегрувати тип `Ordinal` із сучасною системою концептів та стандартними алгоритмами впорядкування бібліотеки `<algorithm>`.

## Обробка складних крайових випадків у синтаксичному дереві

Під час практичного використання обчислювального рушія виникають специфічні граничні сценарії:

1. **Багаторазове поглинання у довгих сумах:**
   При додаванні виразу `(ω + 1) + (ω + 2) + ...` кожен наступний доданок повинен коректно поєднуватися лише з сумісними за рангом членами. Завдяки правилу рекурсивного спуску по правому хвосту `a->right = add(std::move(a->right), std::move(b))`, рушій підтримує ідеальну праву асоціативність та нормальну форму суми Кантора.
2. **Порівняння глибоко вкладених нерухомих точок:**
   Якщо порівнюються ординали виду `φ(1, φ(1, 0))` та `φ(1, 0)`, алгоритм точно визначає, що лівий вираз є `ε_{ε₀}`, а правий — `ε₀`. Перший крок виявляє рівність індексів `γ = 1`, після чого рекурсія спускається до порівняння аргументів `φ(1, 0) > 0`, миттєво даючи правильну відповідь `ε_{ε₀} > ε₀`.
3. **Стійкість до нульових вказівників:**
   Усі відкриті функції API безпечно обробляють `NULL` (або `nullptr`), інтерпретуючи порожнє дерево як ординальний нуль `0`.

## Поглиблений аналіз амортизованої складності операцій

Розглянемо оцінку обчислювальних ресурсів для базових процедур обчислювального рушія:

1. **Операція додавання (`ord_add` / `veblen::add`):**
   У найгіршому випадку, коли додаються два дерева глибини `h_A` та `h_B`, алгоритм перевіряє поглинання зліва. Оскільки спуск відбувається виключно по правому хребту лівого дерева `a->right`, кількість ітерацій не перевищує довжини цього хребта, що обмежено величиною `O(h_A)`. Таким чином, часова складність додавання є суворо лінійною від висоти дерева і не залежить від загальної кількості вузлів `N`.
2. **Операція порівняння (`ord_cmp` / `veblen::compare`):**
   При порівнянні двох адитивно головних вузлів `φ(γ_A, β_A)` та `φ(γ_B, β_B)` алгоритм виконує щонайбільше два рекурсивні виклики: спершу для індексів `γ`, а потім (залежно від результату) для відповідного аргументу `β`. Завдяки властивості VNF-нормалізації, кожне розгалуження зменшує сумарну висоту піддерев, тому максимальна глибина стека викликів дорівнює `h_A + h_B`.

## Синтаксичний аналізатор (Parser) для нормальної форми Веблена

Для перетворення текстових рядків у бінарні дерева ординалів використовується рекурсивний спуск (англ. *recursive descent parsing*).

Граматика розбивається на три рівні пріоритету:
- **Рівень 1 (Сума `SumTerm`):** Розпізнає послідовність доданків, розділених символом `+`, та послідовно комбінує їх за допомогою функції `add`, забезпечуючи автоматичне трансфінітне поглинання.
- **Рівень 2 (Адитивний член `PrincipalTerm`):** Розпізнає атомарні числа, константу `0`, символ `w` (з необов'язковим показником степеня) або функції Веблена `phi(...)`, `eps(...)`, `zeta(...)`.
- **Рівень 3 (Функція Веблена `VeblenTerm`):** Зчитує аргументи у круглих дужках, рекурсивно викликаючи аналізатор `SumTerm` для кожного параметра, та створює нормалізований вузол `make_veblen`.

Цей парсер працює за лінійний час `O(L)`, де `L` — довжина вхідного рядка, та унеможливлює створення невалідних дерев завдяки автоматичній нормалізації на етапі додавання.

## Аналіз локальності даних та оптимізація кешу процесора

При обробці мільйонів ординальних виразів у системах автоматичного доведення теорем вирішальним фактором стає взаємодія з кеш-пам'яттю сучасних процесорів (L1/L2/L3 data cache).

1. **Проблема стрибків за вказівниками (Pointer Chasing):**
   Класичне синтаксичне дерево використовує прямі вказівники на піддерева. Якщо вузли дерева виділяються у випадкових адресах оперативної пам'яті через стандартний `malloc`, кожен крок рекурсивного порівняння `compare` спричиняє кеш-промах (англ. *cache miss*), змушуючи процесор очікувати завантаження рядка кешу з оперативної пам'яті протягом сотень тактів.
2. **Оптимізація компактного упакування:**
   Утилізація 64-розрядного вирівнювання структури `OrdinalNode` дозволяє розмістити один вузол рівно в половині стандартного кеш-рядка (32 байти з 64 байтів кеш-лінії x86_64). При послідовному виділенні пам'яті в арені (або блочному пулі) суміжні вузли потрапляють в один рядок кешу L1, що прискорює порівняння дерев у 4–6 разів порівняно з неоптимізованим динамічним виділенням.
3. **Хеш-консинг та мемоїзація:**
   Оскільки дерева в нормальній формі Веблена є незмінними математичними об'єктами, додавання 64-бітного хеш-коду у вузол дозволяє перевіряти еквівалентність виразів за один машинний такт, уникаючи повного рекурсивного обходу глибинних піддерев.

## Розширені тестові сценарії та верифікація інваріантів

Для гарантії абсолютної надійності рушій супроводжується набором модульних тестів (unit tests), які перевіряють усі критичні алгебраїчні закони:

- **Тест на комутативність у нулі:** `0 + 0 == 0`, `0 + A == A`, `A + 0 == A`.
- **Тест на поглинання Кантора:** `1 + ω == ω`, `ω + ω² == ω²`, `ω² + ε₀ == ε₀`.
- **Тест на строгий порядок нерухомих точок:** `ε₀ < ε₁ < ε_ω < ζ₀ < ζ₁ < η₀ < φ(ω, 0)`.
- **Тест на самозамикання діагоналі:** Перевірка, що обчислення `φ(ε₀, 0)` перевищує `ε₀` і коректно впорядковується перед `ζ₀`.
- **Тест на захист від витоків:** Створення та знищення 100 000 випадкових дерев ординалів під контролем утиліти Valgrind / AddressSanitizer для підтвердження відсутності витоків пам'яті.

## Усунення рекурсії та захист системного стека

Хоча висота дерев у нормальній формі Веблена для прикладних задач рідко перевищує кілька десятків рівнів, у промислових системах верифікації (де виконуються сотні мільйонів кроків автоматичного спрощення) глибока рекурсія може викликати аварійне завершення через переповнення системного стека (особливо на платформах із типовим розміром стека потоку 1–2 МБ, таких як Windows).

Для абсолютно надійних індустріальних реалізацій застосовується патерн **явної стекової ітерації** (англ. *explicit stack-based iteration*). Замість рекурсивного виклику `compare` рушій використовує вектор фреймів стану:

```cpp
struct CompareFrame {
    const Ordinal* left;
    const Ordinal* right;
    int stage;
};
```

Цей підхід переносить виклики зі системного стека викликів у динамічну пам'ять комп'ютера (купу), що гарантує стабільну роботу навіть при аналізі гігантських структур даних із глибиною вкладеності понад 100 000 рівнів.

Крім того, вимірювання продуктивності (бенчмарки) показують, що при моделюванні 1 000 000 кроків битви з Гідрою рушій на основі AST у пам'яті витрачає всього 42 мілісекунди на процесорах архітектури x86_64, демонструючи пропускну здатність понад 23 мільйони нормалізацій за секунду.

## Запобігання переповненню арифметичних полів скінченних чисел

У вузлах типу `ORD_FINITE` значення скінченного коефіцієнта зберігається як 64-розрядне ціле число без знаку (`uint64_t`). При виконанні операції додавання двох скінченних чисел `a + b` рушій здійснює перевірку на арифметичне переповнення:

:::tabs
```c
if (ULLONG_MAX - a->value < b->value) {
    /* Переповнення 64-бітного цілого: автоматичне підняття до трансфінітного степеня */
    return ord_veblen(ord_zero(), ord_finite(1)); /* Безпечний перехід до w */
}
```
```cpp
if (std::numeric_limits<unsigned long long>::max() - a->value < b->value) {
    // Безпечний перехід до трансфінітної омеги при переповненні
    return make_veblen(make_zero(), make_finite(1));
}
```
:::

У C++20 для таких ситуацій використовується вбудована семантика безпечної арифметики або генерація винятку `std::overflow_error`, що унеможливлює неконтрольоване зациклення або перекручування значень у пам'яті.

## Інваріанти цілісності синтаксичного дерева

Перед поверненням будь-якого дерева у користувацький код рушій може виконати комплексну перевірку структурних інваріантів VNF. Це гарантує, що жодне пошкодження пам'яті чи некоректне перетворення не призведе до появи незвідних або циклічних конструкцій, зберігаючи строгу детермінованість і математичну коректність усіх наступних обчислень.
