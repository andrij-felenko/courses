# ⚙️ Реалізація арифметики полів Галуа GF(2^8) та GF(2^4)

Арифметика скінченних полів характеристики `p = 2` лежить в основі симетричної криптографії (зокрема блока замін S-Box у стандарті шифрування AES) та кодів захисту від помилок (Ріда — Соломона, CRC). Кожен елемент поля `GF(2^8)` подається у вигляді одного байта (`uint8_t`), де окремі біти відповідають коефіцієнтам полінома:

```
b_7 x^7 + b_6 x^6 + b_5 x^5 + b_4 x^4 + b_3 x^3 + b_2 x^2 + b_1 x + b_0
```

Усі обчислення виконуються за модулем незвідного многочлена AES:

```
f(x) = x^8 + x^4 + x^3 + x + 1   [шістнадцятковий код 0x11B]
```

## Механізм базових операцій над поліномами

Операція додавання двох елементів поля є найпростішою: оскільки коефіцієнти належать базовому полю `F_2`, додавання коефіцієнтів при однакових степенях змінної `x` виконується за модулем 2 (`0 + 0 = 0`, `0 + 1 = 1`, `1 + 0 = 1`, `1 + 1 = 0`). На рівні апаратного процесора це відповідає одній машинній інструкції побітового виключного «АБО» (XOR). Віднімання повністю тотожне додаванню, оскільки в характеристиці 2 кожен елемент є своїм власним адитивним протилежним (`-a = a`).

Множення на змінну `x` (в криптографічній літературі відоме як функція `xtime`) реалізується зсувом байта вліво на одну позицію. Якщо до зсуву старший сьомий біт `b_7` дорівнював нулю, результуючий многочлен має степінь не більше 7 і не потребує редукції. Якщо ж біт `b_7` дорівнював одиниці, після зсуву виникає член `x^8`, який редукується за модулем `f(x)`: оскільки `x^8 ≡ x^4 + x^3 + x + 1 (mod f(x))`, до результату зсуву додається маска `0x1B` (молодші 8 бітів многочлена `0x11B`).

Множення двох довільних елементів поля `a(x)` та `b(x)` будується за принципом «множення російських селян» (або алгоритмом зсуву та додавання). Ми послідовно перевіряємо молодший біт другого множника `b`: якщо він дорівнює одиниці, поточне значення першого множника `a` додається через XOR до накопичувального результату. Після цього перший множник множиться на `x` за допомогою `xtime`, а другий множник зсувається вправо на один біт. Процес повторюється рівно 8 разів.

### Покрокове простеження множення 0x57 · 0x83

Розглянемо виконання функції `gf28_mul(0x57, 0x83)` крок за кроком:
1. `a = 0x57` (`01010111_2`), `b = 0x83` (`10000011_2`), накопичувач `res = 0x00`.
2. Крок 0: молодший біт `b` дорівнює 1 ⇒ `res = res ^ a = 0x57`. Потім `a = xtime(0x57) = 0xAE` (старший біт був 0, маска не потрібна), `b = 0x41`.
3. Крок 1: молодший біт `b` дорівнює 1 ⇒ `res = 0x57 ^ 0xAE = 0xF9`. Потім `a = xtime(0xAE) = (0xAE << 1) ^ 0x1B = 0x5C ^ 0x1B = 0x47` (старший біт був 1), `b = 0x20`.
4. Кроки 2–6: біти `b` дорівнюють 0 ⇒ `res` не змінюється, значення `a` послідовно проходить через `xtime`: `0x8E`, `0x07`, `0x0E`, `0x1C`, `0x38`.
5. Крок 7: молодший біт `b` дорівнює 1 (старший біт початкового `0x83`) ⇒ `res = 0xF9 ^ 0x38 = 0xC1`.
6. Підсумок: `0x57 · 0x83 = 0xC1`, що точно відповідає теоретичному множенню поліномів.

## Табличне множення та безпека до атак за часом

Оскільки мультиплікативна група `(GF(2^8))^*` є циклічною групою порядку 255, існує первісний елемент `g` (генератор), послідовні степені якого `g^0, g^1, ..., g^{254}` покривають усі ненульові байти поля. Для AES-полінома `0x11B` найменшим генератором є многочлен `g = x + 1` (байт `0x03`).

Це дозволяє замінити множення додаванням логарифмів за модулем 255:

```
a · b = g^{log_g(a) + log_g(b) mod 255}
```

Заздалегідь обчислені таблиці логарифмів `log_table` та експонент `exp_table` розміром по 256 байтів зводять операцію множення до двох читань із пам'яті, одного додавання з перевіркою межі та одного фінального читання. Це дає найвищу швидкодію в софтверних реалізаціях загального призначення.

Проте в сучасній криптографії використання таблиць заміни створює вразливість до атак за часом виконання (cache-timing attacks), оскільки час звернення до кеш-пам'яті залежить від секретних індексів. Коли ключ шифрування або відкритий текст визначає індекс таблиці, зловмисник може виміряти затримки доступу до ліній процесорного кешу L1/L2 і відновити секретний ключ. Тому сучасні захищені криптографічні бібліотеки використовують апаратні векторні інструкції безпереносного множення (CLMUL, PCLMULQDQ) або константні за часом біт-слайсингові алгоритми.

## Мультиплікативне обернення та розширений алгоритм Евкліда

Для знаходження мультиплікативного оберненого елемента `a^{-1}(x)` розв'язується поліноміальне рівняння Безу:

```
u(x) · a(x) + v(x) · f(x) = 1
```

Оскільки степінь незвідного многочлена `f(x)` дорівнює 8, а степінь `a(x)` не перевищує 7, алгоритм Евкліда над полем `F_2` послідовно ділить поліноми зі зсувом старших членів до отримання нульового залишку. Останній ненульовий коефіцієнт Безу `u(x)` стає шуканим оберненим елементом.

Альтернативний метод — піднесення до степеня за малою теоремою Ферма: `a^{-1} = a^{254} = a^{2^8 - 2}`. Цей підхід часто реалізують за схемою Іто — Цудзі (Itoh — Tsujii), де степінь 254 розкладається на ланцюжок операцій Фробеніуса `a ↦ a^2` та кількох множень, що ідеально лягає на логіку конвеєризованих апаратних схем.

## Баштові розширення GF((2^4)^2) для апаратної оптимізації

У мікроконтролерах та криптопроцесорах пряма реалізація інверсії в `GF(2^8)` вимагає значної площі кремнію (близько 300–400 вентилів NAND/XOR). Для зменшення площі використовують конструкцію баштових полів (tower fields) Дейвіда Кенрайта (David Canright):

```
GF(2) ⊂ GF(2^2) ⊂ GF((2^2)^2) = GF(2^4) ⊂ GF((2^4)^2) = GF(2^8)
```

Елемент `GF(2^8)` розглядається як лінійний поліном `y_1 z + y_0`, де `y_1, y_0 ∈ GF(2^4)`. Тоді обернення 8-бітного елемента зводиться до обчислення визначника `d = y_1^2 ν + y_1 y_0 + y_0^2` у полі `GF(2^4)` (де `ν` — константа розширення), знаходження оберненого до `d` у 4-бітному полі та двох множень у `GF(2^4)`. Це зменшує апаратну площу S-Box до рекордно малих 100–120 еквівалентних вентилів без використання таблиць у пам'яті.

## Повний сирцевий код на C та C++

Нижче наведено паралельні еталонні реалізації арифметики `GF(2^8)`: у стилі чистого C з відкритими функціями та в ідіоматичному C++ з типізованим класом, семантикою перевантаження операторів та попередньо згенерованими під час компіляції таблицями (`constexpr`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

/* Незвідний многочлен Rijndael для AES: x^8 + x^4 + x^3 + x + 1 = 0x11B */
#define AES_POLY 0x11B

/* Додавання та віднімання в характеристиці 2 — це побітове XOR */
static inline uint8_t gf28_add(uint8_t a, uint8_t b) {
    return a ^ b;
}

/* Множення на x (xtime): зсув вліво на 1 біт з редукцією за модулем 0x11B */
static inline uint8_t gf28_xtime(uint8_t a) {
    return (uint8_t)((a << 1) ^ ((a & 0x80) ? 0x1B : 0x00));
}

/* Множення методом зсуву та додавання (Russian Peasant Multiplication) */
uint8_t gf28_mul(uint8_t a, uint8_t b) {
    uint8_t res = 0;
    while (b > 0) {
        if (b & 1) {
            res ^= a;
        }
        a = gf28_xtime(a);
        b >>= 1;
    }
    return res;
}

/* Автоморфізм Фробеніуса: σ(a) = a^2 */
static inline uint8_t gf28_frobenius(uint8_t a) {
    return gf28_mul(a, a);
}

/* Обчислення сліду: Tr(a) = a + a^2 + a^4 + a^8 + a^16 + a^32 + a^64 + a^128 */
uint8_t gf28_trace(uint8_t a) {
    uint8_t tr = a;
    uint8_t cur = a;
    for (int i = 1; i < 8; ++i) {
        cur = gf28_frobenius(cur);
        tr ^= cur;
    }
    return tr; /* результат завжди 0 або 1 */
}

/* Обчислення норми: N(a) = a · a^2 · a^4 · ... · a^128 = a^255 */
uint8_t gf28_norm(uint8_t a) {
    if (a == 0) return 0;
    /* У GF(2^8) для будь-якого ненульового елемента a^255 = 1 */
    return 1;
}

/* Обчислення степеня полінома (індекс старшого встановленого біта) */
static int poly_degree(uint32_t p) {
    int deg = -1;
    while (p > 0) {
        deg++;
        p >>= 1;
    }
    return deg;
}

/* Обернений елемент за розширеним алгоритмом Евкліда над F_2[x] */
uint8_t gf28_inv(uint8_t a) {
    if (a == 0) return 0; /* нуль не має оберненого */

    uint32_t r0 = AES_POLY, r1 = a;
    uint32_t v0 = 0, v1 = 1;

    while (r1 > 0) {
        int d0 = poly_degree(r0);
        int d1 = poly_degree(r1);
        int shift = d0 - d1;

        if (shift < 0) {
            /* Обмін залишків та коефіцієнтів Безу */
            uint32_t tmp_r = r0; r0 = r1; r1 = tmp_r;
            uint32_t tmp_v = v0; v0 = v1; v1 = tmp_v;
            shift = -shift;
        }

        r0 ^= (r1 << shift);
        v0 ^= (v1 << shift);
    }

    return (uint8_t)v0;
}

/* Таблиці експоненти та логарифма для швидкого множення через генератор g = 0x03 */
static uint8_t exp_table[256];
static uint8_t log_table[256];
static bool tables_initialized = false;

void gf28_init_tables(void) {
    if (tables_initialized) return;
    
    uint8_t val = 1;
    for (int i = 0; i < 255; ++i) {
        exp_table[i] = val;
        log_table[val] = (uint8_t)i;
        val = gf28_mul(val, 0x03); /* 0x03 (x + 1) — первісний елемент */
    }
    exp_table[255] = exp_table[0];
    log_table[0] = 0; /* логарифм нуля формально не визначений */
    tables_initialized = true;
}

/* Швидке табличне множення за O(1) */
uint8_t gf28_mul_fast(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    if (!tables_initialized) gf28_init_tables();
    int sum = log_table[a] + log_table[b];
    if (sum >= 255) sum -= 255;
    return exp_table[sum];
}

int main(void) {
    gf28_init_tables();

    uint8_t a = 0x57; /* x^6 + x^4 + x^2 + x + 1 */
    uint8_t b = 0x83; /* x^7 + x + 1 */

    uint8_t p_slow = gf28_mul(a, b);
    uint8_t p_fast = gf28_mul_fast(a, b);
    uint8_t a_inv = gf28_inv(a);
    uint8_t prod_inv = gf28_mul(a, a_inv);
    uint8_t tr_a = gf28_trace(a);

    printf("a = 0x%02X, b = 0x%02X\n", a, b);
    printf("a * b (xtime) = 0x%02X (очікується 0xC1)\n", p_slow);
    printf("a * b (таблиця)= 0x%02X\n", p_fast);
    printf("inv(a)        = 0x%02X\n", a_inv);
    printf("a * inv(a)    = 0x%02X (має бути 0x01)\n", prod_inv);
    printf("Tr(a)         = %u\n", tr_a);

    return 0;
}
```
```cpp
#include <cstdint>
#include <array>
#include <iostream>
#include <iomanip>
#include <stdexcept>

class Gf28 {
public:
    uint8_t val;

    constexpr Gf28() noexcept : val(0) {}
    constexpr explicit Gf28(uint8_t v) noexcept : val(v) {}

    // Додавання та віднімання в GF(2^8) збігаються (XOR)
    constexpr Gf28 operator+(Gf28 other) const noexcept {
        return Gf28(val ^ other.val);
    }

    constexpr Gf28 operator-(Gf28 other) const noexcept {
        return Gf28(val ^ other.val);
    }

    // Множення на x (xtime) з редукцією за модулем x^8 + x^4 + x^3 + x + 1 (0x11B)
    static constexpr uint8_t xtime(uint8_t a) noexcept {
        return static_cast<uint8_t>((a << 1) ^ ((a & 0x80) ? 0x1B : 0x00));
    }

    // Звичайне множення поліномів через зсуви
    constexpr Gf28 operator*(Gf28 other) const noexcept {
        uint8_t res = 0;
        uint8_t a = val;
        uint8_t b = other.val;
        while (b > 0) {
            if (b & 1) {
                res ^= a;
            }
            a = xtime(a);
            b >>= 1;
        }
        return Gf28(res);
    }

    // Автоморфізм Фробеніуса σ(a) = a^2
    [[nodiscard]] constexpr Gf28 frobenius() const noexcept {
        return (*this) * (*this);
    }

    // Слід елемента Tr(a) = sum_{i=0}^7 a^{2^i}
    [[nodiscard]] constexpr uint8_t trace() const noexcept {
        Gf28 tr = *this;
        Gf28 cur = *this;
        for (int i = 1; i < 8; ++i) {
            cur = cur.frobenius();
            tr = tr + cur;
        }
        return tr.val;
    }

    // Норма елемента N(a) = prod_{i=0}^7 a^{2^i} = a^255
    [[nodiscard]] constexpr uint8_t norm() const noexcept {
        return (val == 0) ? 0 : 1;
    }

    // Мультиплікативне обернення через розширений алгоритм Евкліда
    [[nodiscard]] Gf28 inverse() const {
        if (val == 0) {
            throw std::domain_error("Division by zero in GF(2^8)");
        }

        uint32_t r0 = 0x11B, r1 = val;
        uint32_t v0 = 0, v1 = 1;

        auto poly_deg = [](uint32_t p) noexcept -> int {
            int deg = -1;
            while (p > 0) { deg++; p >>= 1; }
            return deg;
        };

        while (r1 > 0) {
            int d0 = poly_deg(r0);
            int d1 = poly_deg(r1);
            int shift = d0 - d1;

            if (shift < 0) {
                std::swap(r0, r1);
                std::swap(v0, v1);
                shift = -shift;
            }

            r0 ^= (r1 << shift);
            v0 ^= (v1 << shift);
        }

        return Gf28(static_cast<uint8_t>(v0));
    }

    Gf28 operator/(Gf28 other) const {
        return (*this) * other.inverse();
    }

    constexpr bool operator==(Gf28 other) const noexcept { return val == other.val; }
    constexpr bool operator!=(Gf28 other) const noexcept { return val != other.val; }
};

// Генерація таблиць логарифмів та експонент під час компіляції (constexpr)
struct Gf28Tables {
    std::array<uint8_t, 256> exp{};
    std::array<uint8_t, 256> log{};

    constexpr Gf28Tables() noexcept {
        uint8_t val = 1;
        for (int i = 0; i < 255; ++i) {
            exp[i] = val;
            log[val] = static_cast<uint8_t>(i);
            val = (Gf28(val) * Gf28(0x03)).val; // генератор g = 0x03
        }
        exp[255] = exp[0];
        log[0] = 0;
    }
};

inline constexpr Gf28Tables TABLES{};

// Швидке множення через попередньо обчислені таблиці
inline Gf28 mul_fast(Gf28 a, Gf28 b) noexcept {
    if (a.val == 0 || b.val == 0) return Gf28(0);
    int sum = TABLES.log[a.val] + TABLES.log[b.val];
    if (sum >= 255) sum -= 255;
    return Gf28(TABLES.exp[sum]);
}

int main() {
    Gf28 a(0x57); // x^6 + x^4 + x^2 + x + 1
    Gf28 b(0x83); // x^7 + x + 1

    Gf28 prod_slow = a * b;
    Gf28 prod_fast = mul_fast(a, b);
    Gf28 a_inv = a.inverse();
    Gf28 one = a * a_inv;
    uint8_t tr_a = a.trace();

    std::cout << std::hex << std::uppercase;
    std::cout << "a = 0x" << std::setw(2) << std::setfill('0') << static_cast<int>(a.val) << "\n";
    std::cout << "b = 0x" << std::setw(2) << std::setfill('0') << static_cast<int>(b.val) << "\n";
    std::cout << "a * b (xtime)  = 0x" << static_cast<int>(prod_slow.val) << " (очікується 0xC1)\n";
    std::cout << "a * b (fast)   = 0x" << static_cast<int>(prod_fast.val) << "\n";
    std::cout << "inv(a)         = 0x" << static_cast<int>(a_inv.val) << "\n";
    std::cout << "a * inv(a)     = 0x" << static_cast<int>(one.val) << " (очікується 0x01)\n";
    std::cout << std::dec;
    std::cout << "Tr(a)          = " << static_cast<int>(tr_a) << "\n";

    return 0;
}
```
:::
