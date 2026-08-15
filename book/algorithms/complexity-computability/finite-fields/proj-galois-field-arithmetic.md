# ⚙️ Практична реалізація арифметики полів Галуа GF(2^m)

Ця вставка містить перевірені на практиці реалізації основних арифметичних операцій у скінченному порі розширення Галуа `GF(2⁸)` з незвідним многочленом стандарту AES `f(x) = x⁸ + x⁴ + x³ + x + 1` (бітове представлення `0x11B`). Подані алгоритми охоплюють як базові низькорівневі операції додавання та безпереносного множення, так і табличні прискорювачі `O(1)` (таблиці Зеха) та розширений алгоритм Евкліда для обчислення мультиплікативно оберненого елемента, що є фундаментом симетричної криптографії та завадостійкого кодування.

## 1. Математичні основи представлення елементів та бітова обробка у GF(2^8)

Поле `GF(2⁸)` є дволакунарним розширенням простого поля `GF(2)` степеня `m = 8`. Кожен елемент `A ∈ GF(2⁸)` є многочленом степеня не вище 7 з бітовими коефіцієнтами `aᵢ ∈ {0, 1}`:

```
A(x) = a₇·x⁷ + a₆·x⁶ + a₅·x⁵ + a₄·x⁴ + a₃·x³ + a₂·x² + a₁·x + a₀
```

У комп'ютерній пам'яті коефіцієнти `(a₇, a₆, a₅, a₄, a₃, a₂, a₁, a₀)` упаковуються у стандартне 8-бітне число без знаку `uint8_t`. Оскільки коефіцієнти належать полю `GF(2)`, додавання коефіцієнтів виконується за модулем 2. Це означає, що `1 + 1 = 0` та `1 - 1 = 1`, тобто операції додавання та віднімання в `GF(2)` ідентичні і відповідають бітовій операції **XOR (`^`)**.

Стандартний канонічний многочлен AES має вигляд `f(x) = x⁸ + x⁴ + x³ + x + 1`. Бітове представлення даного многочлена вимагає 9 бітів (`100011011₂` або `0x11B`). Коли під час множення степінь добутку досягає або перевищує 8, виникає потреба в редукції (взятті залишку за модулем `f(x)`). Оскільки `f(x) = 0` у покроковому редукційному середовищі поля, старший член `x⁸` замінюється молодшою частиною:

```
x⁸ ≡ x⁴ + x³ + x + 1  (mod f(x))
```

Шістнадцяткове значення молодших 8 бітів `x⁴ + x³ + x + 1` становить `0x1B`. Таким чином, при виникненні переносу у 8-му біті (значення `0x80` перед зсувом вліво) редукція виконується відніманням (XOR) константи `0x1B`.

## 2. Реалізація базових операцій та генерація таблицій Зеха

У наведеному коді реалізовано два взаємодоповнюючі підходи: класичні процедури мовою C для низькорівневого вбудованого програмування (Embedded Systems) та ідіоматичний C++20 клас `GaloisField256`, який використовує статичну типобезпеку, розширені контейнери `std::array`, перелічення `std::optional` для безпечної обробки крайових випадків (ділення на нуль) та гарантує відсутність витоків пам'яті.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define AES_POLY 0x11B  /* Поліном AES: x^8 + x^4 + x^3 + x + 1 */
#define FIELD_SIZE 256

/* Таблиці логарифмів та експонент для GF(2^8) */
static uint8_t gf_exp[FIELD_SIZE * 2];
static uint8_t gf_log[FIELD_SIZE];
static bool tables_initialized = false;

/* Додавання та віднімання у GF(2^8) еквівалентні побітовому XOR */
uint8_t gf_add(uint8_t a, uint8_t b) {
    return a ^ b;
}

uint8_t gf_sub(uint8_t a, uint8_t b) {
    return a ^ b;
}

/* Множення одного елемента на x (зсув вліво з маскою редукції 0x1B) */
uint8_t gf_mul_x(uint8_t a) {
    if (a & 0x80) {
        return (uint8_t)((a << 1) ^ 0x1B);
    } else {
        return (uint8_t)(a << 1);
    }
}

/* Поліноміальне множення "зсув-і-складання" без таблиць O(m) */
uint8_t gf_mul_slow(uint8_t a, uint8_t b) {
    uint8_t result = 0;
    uint8_t temp_a = a;
    uint8_t temp_b = b;

    while (temp_b > 0) {
        if (temp_b & 1) {
            result ^= temp_a;
        }
        temp_a = gf_mul_x(temp_a);
        temp_b >>= 1;
    }
    return result;
}

/* Генерація таблиць експонент та логарифмів за примітивним елементом alpha = 0x03 */
void gf_init_tables(void) {
    uint8_t x = 1;
    /* У полі AES з поліномом 0x11B елемент 0x03 є примітивним породжувачем */
    uint8_t primitive = 0x03;

    for (int i = 0; i < 255; i++) {
        gf_exp[i] = x;
        gf_exp[i + 255] = x;
        gf_log[x] = (uint8_t)i;
        x = gf_mul_slow(x, primitive);
    }
    gf_log[0] = 0; /* Дискретний логарифм нуля не визначений */
    tables_initialized = true;
}

/* Швидке множення O(1) за допомогою таблиць Зеха */
uint8_t gf_mul_fast(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    if (!tables_initialized) gf_init_tables();
    int log_sum = gf_log[a] + gf_log[b];
    return gf_exp[log_sum];
}

/* Швидке ділення O(1) за допомогою віднімання логарифмів */
uint8_t gf_div_fast(uint8_t a, uint8_t b) {
    if (b == 0) return 0; /* Ділення на нуль повертає 0 як індикатор помилки */
    if (a == 0) return 0;
    if (!tables_initialized) gf_init_tables();
    int log_diff = gf_log[a] - gf_log[b] + 255;
    return gf_exp[log_diff % 255];
}
```
@tab C++
```cpp
#include <iostream>
#include <array>
#include <cstdint>
#include <span>
#include <optional>
#include <stdexcept>

namespace galois {

/**
 * @brief Ідіоматичний C++20 клас для виконання арифметики у полі GF(2^8) AES
 */
class GaloisField256 {
public:
    static constexpr uint16_t AES_POLYNOMIAL = 0x11B;
    static constexpr size_t ORDER = 256;

    constexpr GaloisField256() noexcept {
        init_tables();
    }

    [[nodiscard]] constexpr uint8_t add(uint8_t a, uint8_t b) const noexcept {
        return a ^ b;
    }

    [[nodiscard]] constexpr uint8_t subtract(uint8_t a, uint8_t b) const noexcept {
        return a ^ b;
    }

    [[nodiscard]] constexpr uint8_t mul_x(uint8_t a) const noexcept {
        return (a & 0x80) ? static_cast<uint8_t>((a << 1) ^ 0x1B) 
                          : static_cast<uint8_t>(a << 1);
    }

    [[nodiscard]] constexpr uint8_t multiply_slow(uint8_t a, uint8_t b) const noexcept {
        uint8_t res = 0;
        uint8_t cur_a = a;
        uint8_t cur_b = b;

        while (cur_b > 0) {
            if (cur_b & 1) {
                res ^= cur_a;
            }
            cur_a = mul_x(cur_a);
            cur_b >>= 1;
        }
        return res;
    }

    [[nodiscard]] uint8_t multiply(uint8_t a, uint8_t b) const noexcept {
        if (a == 0 || b == 0) return 0;
        const size_t log_sum = static_cast<size_t>(log_table_[a]) + log_table_[b];
        return exp_table_[log_sum];
    }

    [[nodiscard]] std::optional<uint8_t> divide(uint8_t a, uint8_t b) const noexcept {
        if (b == 0) return std::nullopt;
        if (a == 0) return 0;
        const int log_diff = static_cast<int>(log_table_[a]) - static_cast<int>(log_table_[b]) + 255;
        return exp_table_[static_cast<size_t>(log_diff % 255)];
    }

    [[nodiscard]] const std::array<uint8_t, ORDER>& get_log_table() const noexcept {
        return log_table_;
    }

    [[nodiscard]] const std::array<uint8_t, ORDER * 2>& get_exp_table() const noexcept {
        return exp_table_;
    }

private:
    std::array<uint8_t, ORDER * 2> exp_table_{};
    std::array<uint8_t, ORDER> log_table_{};

    constexpr void init_tables() noexcept {
        uint8_t val = 1;
        constexpr uint8_t primitive = 0x03;

        for (size_t i = 0; i < 255; ++i) {
            exp_table_[i] = val;
            exp_table_[i + 255] = val;
            log_table_[val] = static_cast<uint8_t>(i);
            val = multiply_slow(val, primitive);
        }
        log_table_[0] = 0;
    }
};

} // namespace galois
```
:::

### Детальний розбір алгоритмічних блоків та особливості оптимізації

1. **Функція `gf_mul_x` (Множення на `x` / `0x02`):**
   Ця процедура виконує фундаментальну крокову дію в полі. Вона перевіряє старший біт числа `a & 0x80`. Якщо старший біт дорівнює 1, зсув вліво `a << 1` призведе до виходу за межі 8 бітів (переповнення 8-го степеня `x⁸`). Тому після зсуву виконується побітовий XOR з константою `0x1B`, що реалізує тотожність `x⁸ ≡ x⁴ + x³ + x + 1`. Якщо старший біт дорівнює 0, переповнення не виникає, і повертається звичайний зсув вліво.

2. **Процедура `gf_mul_slow` (Алгоритм селянського множення):**
   Алгоритм реалізує поліноміальне множення «зсув-і-складання» over `GF(2)`. Він перебирає біти розряду `b`. Якщо поточний молодший біт `temp_b & 1` є одиницею, поточне значення `temp_a` додається (XOR) до проміжної суми `result`. На кожному кроці циклу `temp_a` множиться на `x` через функцію `gf_mul_x`, а `temp_b` зсувається вправо на 1 біт. Складність процедури становить 8 ітерацій (`O(m)` бітових кроків).

3. **Ініціалізація `gf_init_tables`:**
   Для прискорення обчислень створюються дві таблиці. Примітивний елемент `α = 0x03` (що відповідає многочлену `x + 1`) послідовно підноситься до степенів від 0 до 254. Значення `exp_table` заповнюється на 512 елементів (дублюється другу половину), що дозволяє уникнути обчислення операції модуля `% 255` при додаванні двох логарифмів під час множення: `exp_table[log_a + log_b]` працює напряму.

4. **Апаратне прискорення та константність за часом:**
   У високопродуктивних серверах замість програмного циклу `gf_mul_slow` розробники застосовують апаратну процесорну інструкцію `PCLMULQDQ` (команду безпереносного множення). Вона обчислює добуток двох 64-бітних слів у 128-бітному SSE/AVX регістрі за 1 системний такт. З іншого боку, для захисту від хронометричних атак (Cache-timing attacks) у криптографії застосовуються версії без умовних операторів `if` та без табличних вибірок.

5. **Векторизація SIMD для масивів даних:**
   У завадостійкому кодуванні Reed-Solomon або кодуванні RAID-6 множення масиву даних на один і той самий елемент поля Галуа є критичною операцією. При використанні SIMD інструкцій (AVX2 / AVX-512) 32 або 64 байти обробляються паралельно за один векторний крок, застосовуючи табличну векторну перестановку `_mm256_shuffle_epi8` для миттєвого множення без виходу в оперативну пам'ять.

## 3. Обчислення оберненого елемента через Розширений алгоритм Евкліда

Мультиплікативно обернений елемент `a⁻¹` задовольняє співвідношенню `a · a⁻¹ ≡ 1 (mod f(x))`. 
Розширений алгоритм Евкліда для многочленів шукає коефіцієнти `u(x)` та `v(x)` такі, що:

```
u(x) · a(x) + v(x) · f(x) = gcd(a(x), f(x)) = 1  ⇒  a⁻¹(x) = u(x) mod f(x)
```

Алгоритм послідовно виконує ділення залишком для двох поліномів `r₀` (початково `f(x) = 0x11B`) та `r₁` (початково `a`), одночасно оновлюючи вектор коефіцієнтів Безу `v₀` та `v₁`.

:::tabs
@tab C
```c
/* Допоміжна функція знаходження степеня многочлена (індекс найстаршого біта) */
static int poly_degree(uint16_t p) {
    int deg = -1;
    while (p > 0) {
        deg++;
        p >>= 1;
    }
    return deg;
}

/* Знаходження мультиплікативно оберненого елемента у GF(2^8) через розширений алгоритм Евкліда */
uint8_t gf_inverse_eea(uint8_t a) {
    if (a == 0) return 0; /* Оберненого для нуля не існує */

    uint32_t r0 = AES_POLY; /* 0x11B (степінь 8) */
    uint32_t r1 = a;        /* степінь < 8 */
    uint32_t v0 = 0;
    uint32_t v1 = 1;

    while (r1 > 1) {
        int deg0 = poly_degree((uint16_t)r0);
        int deg1 = poly_degree((uint16_t)r1);
        int shift = deg0 - deg1;

        if (shift < 0) {
            /* Обмін місцями r0 та r1 */
            uint32_t tmp_r = r0; r0 = r1; r1 = tmp_r;
            uint32_t tmp_v = v0; v0 = v1; v1 = tmp_v;
            shift = -shift;
        }

        r0 ^= (r1 << shift);
        v0 ^= (v1 << shift);
    }

    return (uint8_t)v1;
}
```
@tab C++
```cpp
#include <cstdint>
#include <optional>
#include <utility>

namespace galois {

/**
 * @brief Обчислення мультиплікативно оберненого елемента у GF(2^8) за допомогою Евкліда
 * @param a Вхідний ненульовий елемент
 * @return std::optional<uint8_t> Обернений елемент або std::nullopt для 0
 */
[[nodiscard]] constexpr std::optional<uint8_t> gf_inverse(uint8_t a) noexcept {
    if (a == 0) return std::nullopt;

    auto poly_deg = [](uint32_t p) noexcept -> int {
        int deg = -1;
        while (p > 0) {
            deg++;
            p >>= 1;
        }
        return deg;
    };

    uint32_t r0 = 0x11B; // Незвідний багаточлен AES
    uint32_t r1 = a;
    uint32_t v0 = 0;
    uint32_t v1 = 1;

    while (r1 > 1) {
        int deg0 = poly_deg(r0);
        int deg1 = poly_deg(r1);
        int shift = deg0 - deg1;

        if (shift < 0) {
            std::swap(r0, r1);
            std::swap(v0, v1);
            shift = -shift;
        }

        r0 ^= (r1 << shift);
        v0 ^= (v1 << shift);
    }

    return static_cast<uint8_t>(v1);
}

} // namespace galois
```
:::

### Простеження кроків розширеного алгоритму Евкліда

Розглянемо процес інверсії для елемента `a = 0x02` (`x` у полі `GF(2⁸)`):
1. **Початковий стан:** `r₀ = 0x11B` (`x⁸ + x⁴ + x³ + x + 1`, deg=8), `r₁ = 0x02` (`x`, deg=1), `v₀ = 0`, `v₁ = 1`.
2. **Крок 1:** Різниця степенів `shift = 8 - 1 = 7`. 
   - `r₀` оновлюється: `r₀ ^= (0x02 << 7) = 0x11B ^ 0x100 = 0x1B` (`x⁴ + x³ + x + 1`, deg=4).
   - `v₀` оновлюється: `v₀ ^= (1 << 7) = 0x80` (`x⁷`).
3. **Крок 2:** Порівняння степеней: `deg(r₀) = 4`, `deg(r₁) = 1`. `shift = 4 - 1 = 3`.
   - `r₀ ^= (0x02 << 3) = 0x1B ^ 0x10 = 0x0B` (`x³ + x + 1`, deg=3).
   - `v₀ ^= (1 << 3) = 0x80 ^ 0x08 = 0x88` (`x⁷ + x³`).
4. **Крок 3:** `shift = 3 - 1 = 2`.
   - `r₀ ^= (0x02 << 2) = 0x0B ^ 0x08 = 0x03` (`x + 1`, deg=1).
   - `v₀ ^= (1 << 2) = 0x88 ^ 0x04 = 0x8C` (`x⁷ + x³ + x²`).
5. **Крок 4:** `shift = 1 - 1 = 0`.
   - `r₀ ^= (0x02 << 0) = 0x03 ^ 0x02 = 0x01` (deg=0, досягнуто залишку 1).
   - `v₀ ^= (1 << 0) = 0x8C ^ 0x01 = 0x8D` (`x⁷ + x³ + x² + 1`).
6. **Завершення:** Виконується swap, і значення `v₁` стає рівним `0x8D` (двійкове `10001101₂`).

Перевіримо добуток у полі: `0x02 · 0x8D = (0x8D << 1) ^ 0x1B = 0x11A ^ 0x1B`... тобто `(10001101₂ << 1) = 100011010₂`. Старший біт 1, тому `100011010₂ ^ 100011011₂ = 000000001₂ = 0x01`. Обернення обчислено абсолютно точно за 4 кроки!

## 4. Комплексний тестовий стенд та верифікація S-box AES

Наведений нижче драйвер перевіряє повне дотримання аксіом поля Галуа `GF(2⁸)` для всіх 255 ненульових елементів, гарантуючи відсутність критичних помилок чи безкінечних циклів.

:::tabs
@tab C
```c
int main(void) {
    gf_init_tables();
    printf("=== Перевірка коректності арифметики GF(2^8) ===\n");

    int errors = 0;
    for (int i = 1; i < 256; i++) {
        uint8_t elem = (uint8_t)i;
        uint8_t inv = gf_inverse_eea(elem);
        uint8_t prod = gf_mul_fast(elem, inv);

        if (prod != 1) {
            printf("ПОМИЛКА: i=%d (0x%02X), inv=0x%02X, prod=0x%02X\n", i, elem, inv, prod);
            errors++;
        }
    }

    if (errors == 0) {
        printf("УСПІХ: Усі 255 ненульових елементів задовольняють співвідношенню a * a^-1 = 1!\n");
    } else {
        printf("ЗБОЙ: Виявлено %d помилок при обчисленні обернених елементів.\n", errors);
    }
    return errors;
}
```
@tab C++
```cpp
int main() {
    galois::GaloisField256 gf;
    std::cout << "=== Перевірка C++ класу GaloisField256 ===\n";

    int errors = 0;
    for (uint32_t i = 1; i < 256; ++i) {
        const uint8_t elem = static_cast<uint8_t>(i);
        const auto inv_opt = galois::gf_inverse(elem);

        if (!inv_opt.has_value()) {
            std::cerr << "ПОМИЛКА: відсутній обернений елемент для " << i << "\n";
            errors++;
            continue;
        }

        const uint8_t prod = gf.multiply(elem, inv_opt.value());
        if (prod != 1) {
            std::cerr << "ПОМИЛКА: elem=0x" << std::hex << static_cast<int>(elem)
                      << ", inv=0x" << static_cast<int>(inv_opt.value())
                      << ", prod=0x" << static_cast<int>(prod) << "\n";
            errors++;
        }
    }

    if (errors == 0) {
        std::cout << "УСПІХ: C++20 реалізація пройшла всі 255 перевірок коректності без жодного збою!\n";
    } else {
        std::cerr << "ЗБОЙ: Тестовий стенд виявив " << errors << " помилок!\n";
    }
    return errors;
}
```
:::
