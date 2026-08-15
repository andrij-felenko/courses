# ⚙️ Реалізація розкладу Цекендорфа та фібоначчієвої арифметики

Ця вставка містить практичну реалізацію алгоритмів кодування та декодування Цекендорфа, генерації самосинхронізовного бітового потоку з маркером `11`, а також пряме додавання чисел у фібоначчієвій системі числення мовами C та C++.

## Основні алгоритми та структури даних

Для подання числа у системі Цекендорфа використовується бітовий вектор, у якому `i`-й біт вказує на наявність числа Фібоначчі `Fᵢ₊₂` (де `F₂ = 1, F₃ = 2, F₄ = 3, F₅ = 5, F₆ = 8, …`).

Правило відсутності сусідніх одиниць означає, що у масиві бітів ніколи не зустрічаються два підряд встановлених біти `11`.

Нижче наведено реалізацію двох незалежних модулів кодування: низькорівневого сишного модуля з фіксованими масивами для вбудованих систем, та високорівневого C++20 об'єкта із контейнерами `std::vector`, `std::span` та перевіркою виняткових ситуацій.

```
:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_FIB_INDEX 90

static uint64_t g_fib[MAX_FIB_INDEX];
static bool g_fib_initialized = false;

static void init_fibonacci(void) {
    if (g_fib_initialized) return;
    g_fib[0] = 1; /* F_2 */
    g_fib[1] = 2; /* F_3 */
    for (size_t i = 2; i < MAX_FIB_INDEX; ++i) {
        g_fib[i] = g_fib[i - 1] + g_fib[i - 2];
    }
    g_fib_initialized = true;
}

typedef struct {
    uint8_t bits[MAX_FIB_INDEX];
    size_t length;
} ZeckendorfRep;

/* Жадібний алгоритм розкладу Цекендорфа */
ZeckendorfRep zeckendorf_encode(uint64_t n) {
    init_fibonacci();
    ZeckendorfRep rep;
    for (size_t i = 0; i < MAX_FIB_INDEX; ++i) rep.bits[i] = 0;
    rep.length = 0;

    if (n == 0) return rep;

    /* Знаходимо найбільше F_k <= n */
    int max_idx = 0;
    while (max_idx < MAX_FIB_INDEX - 1 && g_fib[max_idx + 1] <= n) {
        max_idx++;
    }

    rep.length = (size_t)(max_idx + 1);

    uint64_t remainder = n;
    for (int i = max_idx; i >= 0; --i) {
        if (g_fib[i] <= remainder) {
            rep.bits[i] = 1;
            remainder -= g_fib[i];
            i--; /* Пропускаємо сусідній біт (гарантія 0) */
        }
    }

    return rep;
}

uint64_t zeckendorf_decode(const ZeckendorfRep *rep) {
    init_fibonacci();
    uint64_t sum = 0;
    for (size_t i = 0; i < rep->length; ++i) {
        if (rep->bits[i]) {
            sum += g_fib[i];
        }
    }
    return sum;
}

/* Кодування у самосинхронізовний потік (додаємо маркер 1 на кінець) */
size_t build_fibonacci_code(uint64_t n, uint8_t *out_stream) {
    ZeckendorfRep rep = zeckendorf_encode(n);
    if (rep.length == 0) {
        out_stream[0] = 1;
        out_stream[1] = 1;
        return 2;
    }
    for (size_t i = 0; i < rep.length; ++i) {
        out_stream[i] = rep.bits[i];
    }
    out_stream[rep.length] = 1; /* Завершальний маркер 11 */
    return rep.length + 1;
}

int main(void) {
    uint64_t number = 100;
    ZeckendorfRep rep = zeckendorf_encode(number);

    printf("Число %glu в системі Цекендорфа: ", (unsigned long long)number);
    for (int i = (int)rep.length - 1; i >= 0; --i) {
        printf("%d", rep.bits[i]);
    }
    printf(" (Fib)\n");

    uint64_t decoded = zeckendorf_decode(&rep);
    printf("Декодоване значення: %glu\n", (unsigned long long)decoded);

    uint8_t stream[128];
    size_t stream_len = build_fibonacci_code(number, stream);
    printf("Фібоначчієвий префіксний код з маркером 11: ");
    for (size_t i = 0; i < stream_len; ++i) {
        printf("%d", stream[i]);
    }
    printf("\n");

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <cstdint>
#include <algorithm>
#include <stdexcept>
#include <span.hpp> // або std::span у C++20

class ZeckendorfEncoder {
public:
    ZeckendorfEncoder() {
        m_fib.push_back(1); // F_2
        m_fib.push_back(2); // F_3
        while (true) {
            uint64_t next = m_fib[m_fib.size() - 1] + m_fib[m_fib.size() - 2];
            if (next < m_fib.back()) break; // Overflow protection
            m_fib.push_back(next);
        }
    }

    [[nodiscard]] std::vector<uint8_t> encode(uint64_t n) const {
        if (n == 0) return {0};

        auto it = std::upper_bound(m_fib.begin(), m_fib.end(), n);
        size_t max_idx = std::distance(m_fib.begin(), it) - 1;

        std::vector<uint8_t> bits(max_idx + 1, 0);
        uint64_t remainder = n;

        for (int i = static_cast<int>(max_idx); i >= 0; --i) {
            if (m_fib[static_cast<size_t>(i)] <= remainder) {
                bits[static_cast<size_t>(i)] = 1;
                remainder -= m_fib[static_cast<size_t>(i)];
                --i; // Пропускаємо сусідній розряд
            }
        }
        return bits;
    }

    [[nodiscard]] uint64_t decode(std::span<const uint8_t> bits) const {
        uint64_t sum = 0;
        for (size_t i = 0; i < bits.size(); ++i) {
            if (bits[i]) {
                if (i >= m_fib.size()) throw std::out_of_range("Fibonacci index out of range");
                sum += m_fib[i];
            }
        }
        return sum;
    }

    [[nodiscard]] std::string to_fibstream(uint64_t n) const {
        auto bits = encode(n);
        std::string stream;
        stream.reserve(bits.size() + 1);
        for (uint8_t b : bits) {
            stream.push_back(b ? '1' : '0');
        }
        stream.push_back('1'); // Маркер завершення 11
        return stream;
    }

private:
    std::vector<uint64_t> m_fib;
};

int main() {
    ZeckendorfEncoder encoder;
    uint64_t val = 100;

    auto bits = encoder.encode(val);
    std::cout << "Число " << val << " у фібоначчієвому розкладі: ";
    for (auto it = bits.rbegin(); it != bits.rend(); ++it) {
        std::cout << static_cast<int>(*it);
    }
    std::cout << " (Fib)\n";

    std::cout << "Кодований самосинхронізовний потік: " << encoder.to_fibstream(val) << "\n";
    std::cout << "Перевірка декодування: " << encoder.decode(bits) << "\n";

    return 0;
}
```
:::

## Опис канонічних правил додавання у фібоначчієвій системі

Додавання двох чисел у системі Цекендорфа без проміжного перетворення у десяткову форму виконується за допомогою канонізації бітового вектора:

1. **Правило переносу сусідів (`011 → 100`):** Дві одиниці поспіль замінюються однією одиницею у вищому розряді, оскільки `Fₖ + Fₖ₋₁ = Fₖ₊₁`.
2. **Правило розщеплення двійки (`0200 → 1001`):** Два екземпляри одного доданка перетворюються у два вищі й нижчі доданки, оскільки `2 Fₖ = Fₖ₊₁ + Fₖ₋₂` для `k ≥ 3` (а для малих індексів `2 F₂ = F₃` та `2 F₃ = F₄ + F₂`).

Послідовне застосування цих двох правил гарантовано зводить результат до канонічного вигляду Цекендорфа за лінійний час від довжини розрядів.

## Особливості реалізації бітового потоку та оптимізації

У сишній реалізації алгоритму `build_fibonacci_code` бітовий потік формується безпосередньо у вихідному байтовому масиві, де кожен біт записується як окремий байт `0` або `1`. Для реальних мережевих протоколів використовується бітова упаковка (bit-packing), де 8 фібоначчієвих бітів упаковуються в один байт пам'яті за допомогою побітових зсувів `<<` та масок `|`.

Важливою деталлю декодера є обробка помилок термінації: якщо під час зчитування потоку бітів розпізнавач не знаходить парову комбінацію `11` протягом більше ніж 91 біта, потік вважається пошкодженим, оскільки для 64-бітових цілих чисел довжина розкладу Цекендорфа не може перевищувати 90 бітів.
