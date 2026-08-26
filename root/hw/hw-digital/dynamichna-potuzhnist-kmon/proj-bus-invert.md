# ⚙️ Алгоритм Bus Invert: зменшення перемикань шини даних

Широкі паралельні шини даних на друкованих платах та міжблочні магістралі всередині кристала мають значну розподілену ємність провідників `C_bus` (від кількох пікофарад на кристалі до 10–30 пФ на платі). Одночасне перемикання десятків розрядів створює потужні імпульси ємнісного струму, призводить до значних динамічних енерговитрат `P_cap = α · C_bus · V_DD² · f` та генерує індуктивні перешкоди по шинах живлення (ground bounce / supply noise).

Коли 32 або 64 провідники одночасно змінюють стан з 1 на 0, миттєвий струм розряду, що стікає через вивід землі мікросхеми, створює паразитний сплеск напруги через індуктивність виводу корпусу: `V_bounce = L_pin · (di_total / dt)`. Цей шум здатний спричинити помилкове спрацьовування сусідніх логічних вентилів або збій у тригерах пам'яті.

Алгоритм **Bus Invert** (запропонований Мірчею Стенстремом і Вейном Берлесоном у 1995 році) вирішує обидві проблеми: він апаратно обмежує максимальну кількість одночасних перемикань на шині величиною `N / 2` та відчутно знижує середню активність `α` за рахунок введення однієї додаткової службової лінії інверсії на кожну групу розрядів.

---

### Принцип роботи кодера та декодера

Нехай передається `N`-розрядна шина даних. На кожному тактовому кроці `t` передавач отримує нове слово даних `D(t)`. На фізичних лініях шини в цей момент утримується попередній закодований стан `B(t - 1)`.

1. Обчислюється відстань Геммінга `H` між новими даними `D(t)` та поточним фізичним станом шини `B(t - 1)` — тобто кількість провідників, які змінять свій логічний рівень (0 → 1 або 1 → 0):
   ```
   H = popcount(D(t) ⊕ B(t - 1))
   ```
2. Якщо `H > N / 2` (тобто перемикається більшість ліній):
   - Усі біти даних перед виставленням на шину інвертуються: `B(t) = ~D(t)`.
   - Лінія інверсії виставляється в активний рівень: `INV(t) = 1`.
   - Загальна кількість перемикань на фізичній `(N + 1)`-розрядній шині становить `(N - H) + ΔINV`, де `ΔINV` — перемикання лінії інверсії (0 або 1). Оскільки `N - H < N / 2`, сумарна кількість перемикань строго не перевищує `N / 2`.
3. Якщо `H ≤ N / 2`:
   - Дані виставляються на шину без інверсії: `B(t) = D(t)`.
   - Лінія інверсії скидається: `INV(t) = 0`.
   - Кількість перемикань становить `H + ΔINV ≤ N / 2`.

На стороні приймача апаратна схема декодування складається з `N` паралельних вентилів XOR:
```
D_received[i] = B_physical[i] ⊕ INV
```
Якщо `INV == 1`, кожен біт інвертується назад; якщо `INV == 0`, дані проходять без змін із затримкою лише в один логічний вентиль XOR (~15–30 пс).

---

### Математичний аналіз зниження активності

Для випадкових незалежних двійкових даних розрядність шини `N` визначає біноміальний розподіл відстаней Геммінга між сусідніми словами. Ймовірність того, що між двома тактами рівно `k` бітів змінять свій стан, описується формулою:

```
P(H = k) = C(N, k) / 2^N = (N! / (k! · (N - k)!)) / 2^N
```

Математичне сподівання кількості перемикань на некодованій шині дорівнює `E_raw = N / 2`.

Після застосування алгоритму Bus Invert усі випадки, де `k > N / 2`, відображаються у значення `N - k` (плюс перемикання лінії інверсії). Математичне сподівання перемикань для `N`-розрядної шини (при парному `N`) набуває точного аналітичного значення:

```
E_encoded = (N / 2) - (1 / 2^N) · C(N, N / 2) + P(INV_t ≠ INV_{t-1})
```

Для 8-розрядної шини (`N = 8`):
- Некодована шина: у середньому `4.00` перемикань на байт (`α = 0.500`).
- Закодована шина Bus Invert (8 даних + 1 INV): у середньому `3.27` перемикань на слово (`α = 3.27 / 9 ≈ 0.363` відносно 9 ліній, або економія **18.2%** енергії на байт даних).

---

### Програмна реалізація та моделювання енергоспоживання

Нижче наведено модульну реалізацію кодера Bus Invert для 32-бітної шини, розбитої на чотири незалежні 8-розрядні байти. Побайтне розбиття є критично важливим: для монолітної 32-бітної шини ймовірність того, що випадкове слово матиме понад 16 інвертованих бітів, незначна через швидке спадання хвостів біноміального розподілу. Розбиття на чотири 8-розрядні підшини з чотирма лініями `INV` забезпечує значно вищу енергетичну віддачу.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define BUS_WIDTH_BITS 32
#define BYTE_WIDTH 8
#define NUM_LANES (BUS_WIDTH_BITS / BYTE_WIDTH)

typedef struct {
    uint8_t data[NUM_LANES];
    uint8_t inv_mask; // біти інверсії для кожного з 4 каналів
} EncodedBusWord;

typedef struct {
    uint8_t prev_bus[NUM_LANES];
    uint8_t prev_inv;
    uint64_t total_raw_transitions;
    uint64_t total_encoded_transitions;
} BusInvertState;

static inline uint32_t count_ones_8(uint8_t val) {
    return (uint32_t)__builtin_popcount((unsigned int)val);
}

void bus_invert_init(BusInvertState* state) {
    for (size_t i = 0; i < NUM_LANES; ++i) {
        state->prev_bus[i] = 0;
    }
    state->prev_inv = 0;
    state->total_raw_transitions = 0;
    state->total_encoded_transitions = 0;
}

EncodedBusWord bus_invert_encode_word(BusInvertState* state, uint32_t raw_data) {
    EncodedBusWord out;
    out.inv_mask = 0;

    for (size_t i = 0; i < NUM_LANES; ++i) {
        uint8_t current_byte = (uint8_t)((raw_data >> (i * 8)) & 0xFF);
        uint8_t prev_raw = state->prev_bus[i];
        if (state->prev_inv & (1 << i)) {
            prev_raw = ~prev_raw;
        }

        // Обчислюємо перемикання для сирого сигналу
        uint32_t raw_diff = count_ones_8(current_byte ^ prev_raw);
        state->total_raw_transitions += raw_diff;

        // Обчислюємо відстань Геммінга відносно фізичного стану шини
        uint32_t hamming = count_ones_8(current_byte ^ state->prev_bus[i]);

        if (hamming > (BYTE_WIDTH / 2)) {
            out.data[i] = ~current_byte;
            out.inv_mask |= (uint8_t)(1 << i);
        } else {
            out.data[i] = current_byte;
        }

        // Рахуємо реальні перемикання на закодованій шині
        uint32_t bus_diff = count_ones_8(out.data[i] ^ state->prev_bus[i]);
        state->total_encoded_transitions += bus_diff;
        state->prev_bus[i] = out.data[i];
    }

    // Додаємо перемикання ліній інверсії
    uint32_t inv_diff = count_ones_8(out.inv_mask ^ state->prev_inv);
    state->total_encoded_transitions += inv_diff;
    state->prev_inv = out.inv_mask;

    return out;
}

double bus_invert_get_savings_percent(const BusInvertState* state) {
    if (state->total_raw_transitions == 0) return 0.0;
    double raw = (double)state->total_raw_transitions;
    double enc = (double)state->total_encoded_transitions;
    return (1.0 - (enc / raw)) * 100.0;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <bit>
#include <span>
#include <array>
#include <vector>

class BusInvertChannel {
public:
    static constexpr size_t Width = 8;
    static constexpr size_t MaxTransitions = Width / 2;

    struct EncodedByte {
        uint8_t bus_data;
        bool inverted;
    };

    EncodedByte encode(uint8_t new_data) noexcept {
        const uint32_t hamming = std::popcount(static_cast<uint8_t>(new_data ^ prev_bus_data_));
        
        EncodedByte result{};
        if (hamming > MaxTransitions) {
            result.bus_data = static_cast<uint8_t>(~new_data);
            result.inverted = true;
        } else {
            result.bus_data = new_data;
            result.inverted = false;
        }

        prev_bus_data_ = result.bus_data;
        return result;
    }

    [[nodiscard]] static uint8_t decode(const EncodedByte& encoded) noexcept {
        return encoded.inverted ? static_cast<uint8_t>(~encoded.bus_data) : encoded.bus_data;
    }

private:
    uint8_t prev_bus_data_{0};
};

class BusInvert32 {
public:
    static constexpr size_t Lanes = 4;

    struct Frame {
        std::array<uint8_t, Lanes> lanes;
        uint8_t inv_flags; // 4 біти для 4 байтів
    };

    struct Stats {
        uint64_t raw_transitions{0};
        uint64_t encoded_transitions{0};

        [[nodiscard]] double power_reduction_pct() const noexcept {
            if (raw_transitions == 0) return 0.0;
            return (1.0 - static_cast<double>(encoded_transitions) / static_cast<double>(raw_transitions)) * 100.0;
        }
    };

    Frame encode_word(uint32_t word) noexcept {
        Frame frame{};
        frame.inv_flags = 0;
        uint8_t current_inv_state = 0;

        for (size_t i = 0; i < Lanes; ++i) {
            const auto byte_val = static_cast<uint8_t>((word >> (i * 8)) & 0xFF);
            
            // Враховуємо перемикання сирого сигналу для статистики
            stats_.raw_transitions += std::popcount(static_cast<uint8_t>(byte_val ^ prev_raw_bytes_[i]));
            prev_raw_bytes_[i] = byte_val;

            auto [bus_byte, is_inv] = channels_[i].encode(byte_val);
            frame.lanes[i] = bus_byte;
            
            stats_.encoded_transitions += std::popcount(static_cast<uint8_t>(bus_byte ^ prev_encoded_bytes_[i]));
            prev_encoded_bytes_[i] = bus_byte;

            if (is_inv) {
                frame.inv_flags |= static_cast<uint8_t>(1 << i);
                current_inv_state |= static_cast<uint8_t>(1 << i);
            }
        }

        // Враховуємо перемикання ліній прапорців інверсії
        stats_.encoded_transitions += std::popcount(static_cast<uint8_t>(current_inv_state ^ prev_inv_flags_));
        prev_inv_flags_ = current_inv_state;

        return frame;
    }

    [[nodiscard]] const Stats& statistics() const noexcept { return stats_; }

private:
    std::array<BusInvertChannel, Lanes> channels_{};
    std::array<uint8_t, Lanes> prev_raw_bytes_{};
    std::array<uint8_t, Lanes> prev_encoded_bytes_{};
    uint8_t prev_inv_flags_{0};
    Stats stats_{};
};
```
:::

---

### Аналіз ефективності та практичні компроміси

1. **Зниження пікового споживання струму:** У найгіршому сценарії на сирій 8-бітній шині одночасно перемикаються всі 8 ліній (`0x00 → 0xFF`), створюючи піковий струм `8 · C_bus · (V_DD / t_r)`. З алгоритмом Bus Invert цей перехід трансформується у `0x00 → ~0xFF = 0x00` з перемиканням лише однієї лінії `INV` (1 перехід замість 8). Пікова кількість переходів гарантовано не перевищує `N / 2 = 4` для 8-бітного блоку. Це вдвічі знижує рівень індуктивного шуму шин живлення (*ground bounce*).
2. **Зниження середньої потужності:** Для випадкових некорельованих даних середня активність біта на сирій шині становить `α = 0.5`. При 8-розрядному кодуванні Bus Invert середня активність шини зменшується до `α ≈ 0.422`, що дає скорочення середньої динамічної потужності шини на **15.6%**.
3. **Ефект розміру групи (Partitioning):** Для монолітної 32-бітної шини без розбиття економія становить лише ~3.2% через високу концентрацію біноміального розподілу біля значення 16. Розбиття на 4 групи по 8 бітів дає 15.6% економії, а розбиття на 8 груп по 4 біти — понад 21% економії ціною додавання 8 службових ліній.
4. **Порівняння з іншими кодами:** Для адресних шин, де переважає послідовний інкремент адрес (`addr, addr+1, addr+2...`), значно ефективнішим є код Грея (Gray code) або протокол T0, які зводять кількість перемикань при переході до сусіднього слова до рівно одного біта. Натомість для шин даних із випадковим розподілом інформації Bus Invert залишається стандартом де-факто, застосованим у специфікаціях низькоспоживаючої пам'яті LPDDR4 та LPDDR5 (під назвою Data Bus Inversion — DBI).
5. **Апаратні накладні витрати:** Реалізація кодера вимагає суматора одиниць (popcount на базі таблиці або комбінаційного дерева), компаратора з числом `N/2` та банку вентилів XOR для умовної інверсії. Затримка кодера становить близько 2–4 логічних вентилів, що в сучасних інтерфейсах легко компенсується конвеєризацією на етапі передачі.
