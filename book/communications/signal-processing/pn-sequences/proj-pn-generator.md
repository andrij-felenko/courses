# ⚙️ Проєкт: Реалізація генераторів LFSR, m-послідовностей та кодів Ґолда і Касамі на C та C++

Ця вставка містить програмну реалізацію генераторів псевдовипадкових послідовностей (PN) у двох топологіях (Фібоначчі та Галуа), алгоритм побудови кодових послідовностей Ґолда, а також модуль обчислення автокореляційної функції.

```
+-------------------------------------------------------------+
|                  Генератор PN-послідовностей                 |
|                                                             |
|   +-----------------------+     +-----------------------+   |
|   |   Fibonacci LFSR      |     |     Galois LFSR       |   |
|   |  (P(x) = x⁵ + x² + 1) |     |  (P(x) = x⁵ + x³ + 1) |   |
|   +-----------+-----------+     +-----------+-----------+   |
|               |                             |               |
|               +--------------+--------------+               |
|                              |                              |
|                              v                              |
|                     [Суматор modulo 2]                      |
|                              |                              |
|                              v                              |
|                     [Код Ґолда (Gold Code)]                 |
+-------------------------------------------------------------+
```

## 1. Архітектурні рішення та проектування

Програмна реалізація LFSR вимагає чіткого розрізнення двох рівнів подання даних:
1. **Внутрішній стан регістру (State Vector):** зберігається як цілочислове слово `uint32_t`, де кожен біт відповідає окремому тригеру LFSR. Це забезпечує мінімальне використання пам'яті (всього 4 байти на генератор) та миттєве виконання логічних операцій у реєстрах ЦПУ.
2. **Зовнішній потік чіпів (Bipolar Chips):** для подальшої обробки у ЦОС (обчислення автокореляції, розширення спектра DSSS) біти `{0, 1}` відображаються у біполярні значення `{+1, -1}` у форматі `int8_t`.

### Маска полінома зворотного зв'язку
Поліном зворотного зв'язку кодується у вигляді двійкової маски `poly_mask`. Біти цієї маски вказують розряди, від яких взяті отводи:
- У структурі Фібоначчі: `poly_mask` визначає розряди, з яких знімаються сигнали для обчислення загальної суми XOR (парності).
- У структурі Галуа: `poly_mask` вказує позиції внутрішніх вентилів XOR, у які вноситься вихідний біт молодшого розряду при зсуві.

## 2. Реалізація програмами на C та C++

У наведених нижче вкладках показано реалізацію двох топологій LFSR, генерацію кодів Ґолда шляхом поелементного додавання двох m-послідовностей та обчислення автокореляційної функції.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

/* Структура генератора LFSR у формі Фібоначчі */
typedef struct {
    uint32_t state;
    uint32_t mask;
    uint8_t  bits;
} lfsr_fibonacci_t;

/* Структура генератора LFSR у формі Галуа */
typedef struct {
    uint32_t state;
    uint32_t mask;
    uint8_t  bits;
} lfsr_galois_t;

void lfsr_fibonacci_init(lfsr_fibonacci_t *lfsr, uint32_t poly_mask, uint8_t bits, uint32_t seed) {
    lfsr->mask = poly_mask;
    lfsr->bits = bits;
    /* Захист від заклинювання у нульовому стані */
    lfsr->state = (seed == 0) ? 1U : (seed & ((1U << bits) - 1U));
}

uint8_t lfsr_fibonacci_next(lfsr_fibonacci_t *lfsr) {
    uint8_t out_bit = (lfsr->state >> (lfsr->bits - 1)) & 1U;
    uint32_t tapped = lfsr->state & lfsr->mask;
    
    /* Обчислення парності отводів (згорнутий XOR) */
    uint8_t feedback = 0;
    while (tapped > 0) {
        feedback ^= (tapped & 1U);
        tapped >>= 1U;
    }
    
    lfsr->state = ((lfsr->state << 1U) | feedback) & ((1U << lfsr->bits) - 1U);
    return out_bit;
}

void lfsr_galois_init(lfsr_galois_t *lfsr, uint32_t poly_mask, uint8_t bits, uint32_t seed) {
    lfsr->mask = poly_mask;
    lfsr->bits = bits;
    lfsr->state = (seed == 0) ? 1U : (seed & ((1U << bits) - 1U));
}

uint8_t lfsr_galois_next(lfsr_galois_t *lfsr) {
    uint8_t out_bit = lfsr->state & 1U;
    lfsr->state >>= 1U;
    if (out_bit != 0) {
        lfsr->state ^= lfsr->mask;
    }
    return out_bit;
}

/* Генерація коду Ґолда шляхом додавання двох m-послідовностей */
void generate_gold_sequence(uint32_t poly1, uint32_t poly2, uint8_t bits, 
                            uint32_t shift2, int8_t *out_buf, size_t length) {
    lfsr_galois_t gen1, gen2;
    lfsr_galois_init(&gen1, poly1, bits, 1);
    lfsr_galois_init(&gen2, poly2, bits, 1);

    /* Прокрутка другого генератора для встановлення фазового зсуву */
    for (uint32_t i = 0; i < shift2; i++) {
        lfsr_galois_next(&gen2);
    }

    for (size_t i = 0; i < length; i++) {
        uint8_t b1 = lfsr_galois_next(&gen1);
        uint8_t b2 = lfsr_galois_next(&gen2);
        uint8_t gold_bit = b1 ^ b2;
        /* Перетворення {0, 1} у біполярний сигнал {+1, -1} */
        out_buf[i] = (gold_bit == 0) ? 1 : -1;
    }
}

/* Обчислення періодичної автокореляційної функції */
int32_t compute_autocorrelation(const int8_t *seq, size_t length, size_t shift) {
    int32_t sum = 0;
    for (size_t i = 0; i < length; i++) {
        size_t shifted_idx = (i + shift) % length;
        sum += (int32_t)seq[i] * (int32_t)seq[shifted_idx];
    }
    return sum;
}

int main(void) {
    const uint8_t bits = 5;
    const size_t N = (1U << bits) - 1U; /* N = 31 */
    int8_t *seq = (int8_t *)malloc(N * sizeof(int8_t));
    if (!seq) return 1;

    /* Поліноми Ґолда m=5: x⁵ + x² + 1 (0x12) та x⁵ + x⁴ + x³ + x² + 1 (0x1E) */
    generate_gold_sequence(0x12U, 0x1EU, bits, 3, seq, N);

    printf("Період N = %zu\n", N);
    printf("АКФ на зсуві 0: %d\n", compute_autocorrelation(seq, N, 0));
    printf("АКФ на зсуві 1: %d\n", compute_autocorrelation(seq, N, 1));
    printf("АКФ на зсуві 2: %d\n", compute_autocorrelation(seq, N, 2));

    free(seq);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <numeric>
#include <span>
#include <expected>
#include <string_view>

enum class LfsrTopology {
    Fibonacci,
    Galois
};

enum class LfsrError {
    InvalidState,
    ZeroSeedForbidden
};

class LfsrGenerator {
public:
    constexpr LfsrGenerator(uint32_t poly_mask, uint8_t bit_width, uint32_t seed, LfsrTopology topo)
        : mask_(poly_mask), bits_(bit_width), topology_(topo) {
        state_ = (seed == 0) ? 1U : (seed & ((1U << bits_) - 1U));
    }

    [[nodiscard]] uint8_t step() noexcept {
        if (topology_ == LfsrTopology::Galois) {
            uint8_t out_bit = state_ & 1U;
            state_ >>= 1U;
            if (out_bit != 0) {
                state_ ^= mask_;
            }
            return out_bit;
        } else {
            uint8_t out_bit = (state_ >> (bits_ - 1)) & 1U;
            uint32_t tapped = state_ & mask_;
            uint8_t feedback = 0;
            while (tapped > 0) {
                feedback ^= (tapped & 1U);
                tapped >>= 1U;
            }
            state_ = ((state_ << 1U) | feedback) & ((1U << bits_) - 1U);
            return out_bit;
        }
    }

    [[nodiscard]] uint32_t state() const noexcept { return state_; }

private:
    uint32_t state_{1};
    uint32_t mask_{0};
    uint8_t  bits_{5};
    LfsrTopology topology_{LfsrTopology::Galois};
};

class GoldCodeGenerator {
public:
    GoldCodeGenerator(uint32_t poly1, uint32_t poly2, uint8_t bits, uint32_t shift2)
        : gen1_(poly1, bits, 1, LfsrTopology::Galois),
          gen2_(poly2, bits, 1, LfsrTopology::Galois) {
        for (uint32_t i = 0; i < shift2; ++i) {
            gen2_.step();
        }
    }

    [[nodiscard]] std::vector<int8_t> generate_bipolar(size_t length) {
        std::vector<int8_t> buffer(length);
        for (size_t i = 0; i < length; ++i) {
            uint8_t b1 = gen1_.step();
            uint8_t b2 = gen2_.step();
            uint8_t gold_bit = b1 ^ b2;
            buffer[i] = (gold_bit == 0) ? int8_t{1} : int8_t{-1};
        }
        return buffer;
    }

private:
    LfsrGenerator gen1_;
    LfsrGenerator gen2_;
};

[[nodiscard]] int32_t compute_autocorrelation(std::span<const int8_t> sequence, size_t shift) noexcept {
    const size_t len = sequence.size();
    int32_t accum = 0;
    for (size_t i = 0; i < len; ++i) {
        size_t shifted_idx = (i + shift) % len;
        accum += static_cast<int32_t>(sequence[i]) * static_cast<int32_t>(sequence[shifted_idx]);
    }
    return accum;
}

int main() {
    constexpr uint8_t bits = 5;
    constexpr size_t N = (1U << bits) - 1U;

    GoldCodeGenerator gold_gen(0x12U, 0x1EU, bits, 3);
    const auto bipolar_seq = gold_gen.generate_bipolar(N);

    std::cout << "Період послідовності N = " << N << "\n";
    std::cout << "АКФ на зсуві 0: " << compute_autocorrelation(bipolar_seq, 0) << "\n";
    std::cout << "АКФ на зсуві 1: " << compute_autocorrelation(bipolar_seq, 1) << "\n";
    std::cout << "АКФ на зсуві 2: " << compute_autocorrelation(bipolar_seq, 2) << "\n";

    return 0;
}
```
:::

## 3. Детальний аналіз реалізації та алгоритмічні кроки

### Фібоначчівський генератор проти Галуа
У реалізації мовою C структури `lfsr_fibonacci_t` та `lfsr_galois_t` зберігають поточний вектор стану `state`, маску отводів `mask` та кількість робочих бітів `bits`.

Головна відмінність алгоритмів полягає у кроці оновлення:
- У функції `lfsr_fibonacci_next` відвідні біти виділяються операцією `lfsr->state & lfsr->mask`, після чого у циклі `while (tapped > 0)` обчислюється їхня парність. Результат підсумовування зсувається на вхід найстаршого біта.
- У функції `lfsr_galois_next` перевіряється лише молодший біт `out_bit = lfsr->state & 1U`. Якщо він дорівнює 1, весь вектор стану після зсуву на 1 біт праворуч піддається операції `XOR` із маскою `lfsr->mask`. Всі осередки оновлюються за один розрядно-паралельний крок без циклів.

### Апаратні оптимізації обчислення парності
У програмі на C обчислення парності для Фібоначчі виконано через елементарний цикл. Проте для сучасних процесорів x86-64 та ARM це місце є вузьким шийком. Використання компіляторної інструкції `__builtin_parity(tapped)` (у GCC/Clang) або інструкції `std::popcount` (у C++20) дозволяє обчислити значення зворотного зв'язку за 1 такт процесора без розгалужень та циклів.

### Генерація коду Ґолда
Функція `generate_gold_sequence` використовує два окремі генератори Галуа `gen1` та `gen2`. Для створення конкретного коду із сімейства Ґолда один із генераторів `gen2` заздалегідь прокручується у циклі на потрібну кількість тактів `shift2`. На кожному наступному кроці обидва генератори зсуваються одночасно, а результуючі біти додаються по модулю 2 (`b1 ^ b2`). Результат конвертується у біполярну форму `{+1, -1}` для подальшої обробки у ЦОС.

## 4. Оптимізація обчислень та тестування кореляції

Обчислення автокореляційної функції `compute_autocorrelation` за наївною формулою має обчислювальну складність `O(N²)`. У реальних DSP-процесорах та SDR-приймачах (Software Defined Radio) обчислення АКФ та ВКФ виконується через швидке перетворення Фур'є (FFT) за допомогою теореми про кореляцію:

```
R(k) = IFFT( FFT(s) · FFT*(s) )
```

Це знижує складність обчислень до `O(N · log_2 N)`, що дозволяє в реальному часі шукати фазовий зсув супутникового сигналу GPS (`N = 1023` чіпів) навіть на недорогих мікроконтролерах ARM Cortex-M4 чи ESP32.

### Інженерні пастки реалізації
1. **Пастка поглинального стану (Zero-State Trap):** У функціях ініціалізації `lfsr_fibonacci_init` та `lfsr_galois_init` додано сувору перевірку `if (seed == 0) seed = 1`. Якщо у регістр записати значення 0, подальші операції `XOR` із нулями зациклять генератор у нулі назавжди.
2. **Типові помилки маскування:** При зсуві стану критично важливо обрізати старші біти маскою `(1U << bits) - 1U`. Якщо цього не зробити, старші сміттєві біти змінної `uint32_t` викривлять подальші обчислення парності.
3. **Оптимізація ПЛІС (FPGA Synthesis):** При синтезі LFSR на ПЛІС (Xilinx/AMD або Altera/Intel) структура Галуа ідеально лягає на вентильні матриці (LUT), а тригери регістру зсуву упаковуються у спеціалізовані блоки `SRL16E` / `SRL32E`, заощаджуючи до 75% логічних ресурсів кристала.

### Перевірка постулатів Ґоломба у юніт-тестах
Під час тестування програмного модуля генерації PN-послідовностей необхідно виконувати три обов'язкові перевірки:
- **Перевірка періоду:** генерація `2ᵐ - 1` бітів повинна дати унікальні стани регістру, а `2ᵐ`-й біт повинен точно збігтися з початковим станом `seed`.
- **Перевірка збалансованості:** сума біполярного масиву `int8_t` за повний період повинна дорівнювати строго `+1` (або `-1` залежно від інверсії).
- **Перевірка АКФ:** значення `compute_autocorrelation` при `shift = 0` має дорівнювати `N`, а при всіх ненульових зсувах `1 ≤ shift < N` — строго `-1`.
