# ⚙️ Практична реалізація Xor-фільтра на C та C++

<preknowlist>
- [Біти й порядок байтів](root:sf-algorithms/bits-bytes-endianness) — побітові операції XOR, зсуви та маски.
- [Хеш-таблиця](root:sf-algorithms/hash-table) — швидкі хеш-функції MurmurHash3, xxHash та виключення ділення.
- [Стрічковий фільтр](root:sf-algorithms/ribbon-filter) — розв'язання лінійних систем над двійковими полями.
</preknowlist>

Xor-фільтр є однією з найбільш витончених ймовірнісних структур даних: його алгоритм перевірки належності не містить розгалужень (branchless) і вимагає лише трьох звернень до пам'яті з наступною операцією `XOR`.

Розглянемо повну промислову реалізацію 8-бітного Xor-фільтра (з імовірністю хибних спрацьовувань `ε = 1/256 ≈ 0.39%`) на мовах C та C++.

## Детальний аналіз алгоритмічних компонентів

Побудова Xor-фільтра вимагає вирішення кількох нетривіальних інженерних задач, від яких безпосередньо залежить як швидкість конструювання, так і стабільність роботи у продакшені.

### 1. Трюк з накопичувачем HXor для економії пам'яті

У наївній реалізації 3-гіперграфа для кожного слота потрібно було б зберігати динамічний список інцидентних йому ключів. Це вимагало б виділення великої кількості динамічної пам'яті під вказівники та спричиняло б фрагментацію купи.

Xor-фільтр застосовує елегантний математичний прийом: замість списку ключів для кожної комірки `c` зберігається лише 8-бітний лічильник степеня `HCount[c]` та 64-бітне число `HXor[c]`, що є побітовою сумою `XOR` усіх інцидентних ключів:

```
HXor[c] = k₁ ⊕ k₂ ⊕ ... ⊕ k_d
```

Коли під час лущення степінь вершини зменшується до `HCount[c] == 1`, у накопичувачі `HXor[c]` автоматично залишається єдиний незлущений ключ, оскільки всі інші ключі були видалені через повторне застосування операції `HXor[c] ^= removed_key` (властивість самоскасування `x ⊕ x = 0`). Це скорочує витрати допоміжної пам'яті під час побудови до фіксованих 9 байтів на слот.

### 2. Швидке масштабування без ділення (Lemire FastRange)

Класичне взяття залишку від ділення `hash % block_length` транслюється компілятором в апаратну інструкцію ділення `div` або `idiv`, яка на архітектурах x86-64 та ARM виконується від 12 до 25 тактів процесора.

Для відображення 32-бітного хешу на діапазон `[0, L)` застосовується швидке множення з 32-бітним зсувом:

```
reduce(h, L) = (uint32_t)(((uint64_t)h * (uint64_t)L) >> 32)
```

Ця операція виконується за 1 такт процесора і забезпечує строгу рівномірність розподілу без появи небезпечних систематичних зміщень.

### 3. Гарантія розв'язності через LIFO-стек

Порядок лущення фіксує послідовність елімінації ребер. Коли вершина `pure_slot` має степінь 1, вона належить рівно одному активному рівнянню. Записуючи пару `(key, pure_slot)` у стек, ми гарантуємо, що при зворотному проході від вершини стека до дна слот `pure_slot` ще не задіяний жодним іншим рівнянням. Це дає нам рівно один вільний ступінь свободи для детермінованого обчислення `B[pure_slot] = fp ^ B[c_a] ^ B[c_b]`.

### 4. Покрокове трасування лущення на конкретному прикладі

Нехай ми маємо множину з трьох ключів `{k₁, k₂, k₃}` та масив слотів із трьох блоків по 2 комірки в кожному (`L = 2`, усього `M = 6` слотів: `B₀ = {0, 1}`, `B₁ = {2, 3}`, `B₂ = {4, 5}`).

Припустимо, хеш-функції згенерували такі індекси та відбитки:
* Ключ `k₁`: позиції `(0, 2, 4)`, відбиток `fp₁ = 0xAA`
* Ключ `k₂`: позиції `(0, 3, 4)`, відбиток `fp₂ = 0x55`
* Ключ `k₃`: позиції `(1, 2, 5)`, відбиток `fp₃ = 0xFF`

**Фаза 1: Ініціалізація та лущення**:
1. **Підрахунок степенів**:
   * Слот 0: інцидентні `k₁, k₂` → `HCount[0] = 2`, `HXor[0] = k₁ ⊕ k₂`
   * Слот 1: інцидентний `k₃` → `HCount[1] = 1`, `HXor[1] = k₃` (степінь 1!)
   * Слот 2: інцидентні `k₁, k₃` → `HCount[2] = 2`, `HXor[2] = k₁ ⊕ k₃`
   * Слот 3: інцидентний `k₂` → `HCount[3] = 1`, `HXor[3] = k₂` (степінь 1!)
   * Слот 4: інцидентні `k₁, k₂` → `HCount[4] = 2`, `HXor[4] = k₁ ⊕ k₂`
   * Слот 5: інцидентний `k₃` → `HCount[5] = 1`, `HXor[5] = k₃` (степінь 1!)
2. **Черга вершин степеня 1**: містить слоти `{1, 3, 5}`.
3. **Крок 1 лущення**: витягуємо слот 1. Єдиний ключ `k₃`. Кладемо `(k₃, 1)` у стек. Зменшуємо лічильники для позицій `k₃` (слоти 1, 2, 5). Тепер `HCount[2]` зменшується з 2 до 1, тому слот 2 потрапляє в чергу!
4. **Крок 2 лущення**: витягуємо слот 2. Єдиний ключ `k₁`. Кладемо `(k₁, 2)` у стек. Зменшуємо лічильники для `(0, 2, 4)`. Тепер `HCount[0]` та `HCount[4]` стають 1 (обидва в чергу).
5. **Крок 3 лущення**: витягуємо слот 3. Єдиний ключ `k₂`. Кладемо `(k₂, 3)` у стек.
6. Усі 3 ключі розміщені в стеку: `Stack = [(k₃, 1), (k₁, 2), (k₂, 3)]`.

**Фаза 2: Зворотна підстановка**:
1. Ініціалізуємо `B[0..5] = {0, 0, 0, 0, 0, 0}`.
2. Знімаємо `(k₂, 3)`: позиції `k₂` це `(0, 3, 4)`. Слоти 0 і 4 наразі дорівнюють `0x00`. Обчислюємо:
   `B[3] = fp₂ ⊕ B[0] ⊕ B[4] = 0x55 ⊕ 0x00 ⊕ 0x00 = 0x55`.
3. Знімаємо `(k₁, 2)`: позиції `k₁` це `(0, 2, 4)`. Обчислюємо:
   `B[2] = fp₁ ⊕ B[0] ⊕ B[4] = 0xAA ⊕ 0x00 ⊕ 0x00 = 0xAA`.
4. Знімаємо `(k₃, 1)`: позиції `k₃` це `(1, 2, 5)`. Слот `B[2]` уже має `0xAA`, а слот `B[5]` має `0x00`. Обчислюємо:
   `B[1] = fp₃ ⊕ B[2] ⊕ B[5] = 0xFF ⊕ 0xAA ⊕ 0x00 = 0x55`.
5. Підсумковий масив слотів: `B = {0x00, 0x55, 0xAA, 0x55, 0x00, 0x00}`.
6. Перевірка:
   * Для `k₁`: `B[0] ⊕ B[2] ⊕ B[4] = 0x00 ⊕ 0xAA ⊕ 0x00 = 0xAA == fp₁` (правильно!).
   * Для `k₂`: `B[0] ⊕ B[3] ⊕ B[4] = 0x00 ⊕ 0x55 ⊕ 0x00 = 0x55 == fp₂` (правильно!).
   * Для `k₃`: `B[1] ⊕ B[2] ⊕ B[5] = 0x55 ⊕ 0xAA ⊕ 0x00 = 0xFF == fp₃` (правильно!).

## Вихідний код: C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

/* Коефіцієнт просторового надлишку c = 1.23 */
#define XOR_FILTER_OVERHEAD_FACTOR 1.23
#define XOR_FILTER_MAX_ATTEMPTS 64

/* Структура 8-бітного Xor-фільтра */
typedef struct {
    uint64_t seed;          /* Псевдовипадковий засів хешування */
    uint32_t block_length;  /* Довжина одного з 3 блоків (L) */
    uint8_t *fingerprints;  /* Масив відбитків розміром 3 * block_length */
} xor_filter_8_t;

/* Допоміжна структура для стека лущення */
typedef struct {
    uint64_t key;
    uint32_t index;
} xor_peel_entry_t;

/* Швидкий 64-бітний хеш Murmur3/SplitMix64 */
static inline uint64_t xor_hash64(uint64_t x, uint64_t seed) {
    x ^= seed;
    x ^= x >> 33;
    x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33;
    return x;
}

/* Швидке зведення 64-бітного значення до діапазону [0, n) без ділення (Lemire FastRange) */
static inline uint32_t xor_reduce(uint32_t hash, uint32_t n) {
    return (uint32_t)(((uint64_t)hash * (uint64_t)n) >> 32);
}

/* Обчислення трьох індексів у трьох незалежних блоках B0, B1, B2 */
static inline void xor_get_positions(uint64_t key, uint64_t seed, uint32_t block_len,
                                     uint32_t *h0, uint32_t *h1, uint32_t *h2) {
    uint64_t hash = xor_hash64(key, seed);
    uint32_t a = (uint32_t)(hash >> 32);
    uint32_t b = (uint32_t)hash;
    uint32_t c = (uint32_t)(hash ^ (hash >> 16));

    *h0 = xor_reduce(a, block_len);
    *h1 = block_len + xor_reduce(b, block_len);
    *h2 = 2 * block_len + xor_reduce(c, block_len);
}

/* Обчислення 8-бітного цільового відбитка */
static inline uint8_t xor_fingerprint(uint64_t key, uint64_t seed) {
    uint64_t hash = xor_hash64(key, ~seed);
    uint8_t fp = (uint8_t)(hash ^ (hash >> 32));
    return (fp == 0) ? 1 : fp; /* Уникаємо нульового відбитка для надійності */
}

/* Ініціалізація та побудова Xor-фільтра */
bool xor_filter_8_build(xor_filter_8_t *filter, const uint64_t *keys, size_t count) {
    if (!filter || !keys || count == 0) return false;

    /* Обчислення довжини сегмента L = ceil(1.23 * count / 3) */
    uint32_t block_len = (uint32_t)((XOR_FILTER_OVERHEAD_FACTOR * (double)count) / 3.0) + 1;
    if (block_len < 32) block_len = 32;
    uint32_t total_slots = 3 * block_len;

    filter->block_length = block_len;
    filter->fingerprints = (uint8_t *)calloc(total_slots, sizeof(uint8_t));
    if (!filter->fingerprints) return false;

    /* Виділення службових структур для лущення */
    uint8_t *hcount = (uint8_t *)malloc(total_slots * sizeof(uint8_t));
    uint64_t *hxor = (uint64_t *)malloc(total_slots * sizeof(uint64_t));
    uint32_t *queue = (uint32_t *)malloc(total_slots * sizeof(uint32_t));
    xor_peel_entry_t *stack = (xor_peel_entry_t *)malloc(count * sizeof(xor_peel_entry_t));

    if (!hcount || !hxor || !queue || !stack) {
        free(filter->fingerprints);
        free(hcount); free(hxor); free(queue); free(stack);
        return false;
    }

    uint64_t seed = 0x8543290134ULL;
    bool success = false;

    for (int attempt = 0; attempt < XOR_FILTER_MAX_ATTEMPTS; ++attempt) {
        seed = xor_hash64(seed + attempt, 0x9e3779b97f4a7c15ULL);
        memset(hcount, 0, total_slots * sizeof(uint8_t));
        memset(hxor, 0, total_slots * sizeof(uint64_t));

        /* Крок 1: Заповнення графів інцидентності */
        for (size_t i = 0; i < count; ++i) {
            uint32_t h0, h1, h2;
            xor_get_positions(keys[i], seed, block_len, &h0, &h1, &h2);

            hcount[h0]++; hxor[h0] ^= keys[i];
            hcount[h1]++; hxor[h1] ^= keys[i];
            hcount[h2]++; hxor[h2] ^= keys[i];
        }

        /* Крок 2: Знаходження початкових вершин степеня 1 */
        uint32_t q_head = 0, q_tail = 0;
        for (uint32_t i = 0; i < total_slots; ++i) {
            if (hcount[i] == 1) {
                queue[q_tail++] = i;
            }
        }

        /* Крок 3: Лущення гіперграфа */
        uint32_t stack_size = 0;
        while (q_head < q_tail) {
            uint32_t slot = queue[q_head++];
            if (hcount[slot] != 1) continue;

            uint64_t key = hxor[slot];
            stack[stack_size].key = key;
            stack[stack_size].index = slot;
            stack_size++;

            uint32_t h[3];
            xor_get_positions(key, seed, block_len, &h[0], &h[1], &h[2]);

            for (int j = 0; j < 3; ++j) {
                uint32_t neighbor = h[j];
                hcount[neighbor]--;
                hxor[neighbor] ^= key;
                if (hcount[neighbor] == 1) {
                    queue[q_tail++] = neighbor;
                }
            }
        }

        /* Якщо всі ключі злущено без виникнення 2-ядра — успіх */
        if (stack_size == count) {
            filter->seed = seed;
            success = true;
            break;
        }
    }

    if (!success) {
        free(filter->fingerprints);
        filter->fingerprints = NULL;
        free(hcount); free(hxor); free(queue); free(stack);
        return false;
    }

    /* Фаза 2: Зворотна підстановка (Back-substitution) */
    memset(filter->fingerprints, 0, total_slots * sizeof(uint8_t));
    while (count > 0) {
        count--;
        uint64_t key = stack[count].key;
        uint32_t slot = stack[count].index;
        uint8_t fp = xor_fingerprint(key, filter->seed);

        uint32_t h[3];
        xor_get_positions(key, filter->seed, block_len, &h[0], &h[1], &h[2]);

        uint8_t other_xor = 0;
        for (int j = 0; j < 3; ++j) {
            if (h[j] != slot) {
                other_xor ^= filter->fingerprints[h[j]];
            }
        }
        filter->fingerprints[slot] = fp ^ other_xor;
    }

    free(hcount); free(hxor); free(queue); free(stack);
    return true;
}

/* Перевірка належності ключа (Lookup) — константний час O(1), branchless */
bool xor_filter_8_contains(const xor_filter_8_t *filter, uint64_t key) {
    if (!filter || !filter->fingerprints) return false;

    uint32_t h0, h1, h2;
    xor_get_positions(key, filter->seed, filter->block_length, &h0, &h1, &h2);
    uint8_t fp = xor_fingerprint(key, filter->seed);

    uint8_t combined = filter->fingerprints[h0] ^
                       filter->fingerprints[h1] ^
                       filter->fingerprints[h2];

    return (combined == fp);
}

/* Звільнення ресурсів */
void xor_filter_8_destroy(xor_filter_8_t *filter) {
    if (filter && filter->fingerprints) {
        free(filter->fingerprints);
        filter->fingerprints = NULL;
        filter->block_length = 0;
    }
}
```
```cpp
#include <cstdint>
#include <vector>
#include <span>
#include <array>
#include <memory>
#include <expected>
#include <string_view>
#include <algorithm>

namespace algorithms {

enum class FilterError {
    EmptyInput,
    AllocationFailure,
    PeelingFailedExceededAttempts
};

template <typename FingerprintType = uint8_t>
class XorFilter {
public:
    static constexpr double OverheadFactor = 1.23;
    static constexpr int MaxBuildAttempts = 64;

    XorFilter() noexcept = default;

    /* Фабричний метод побудови фільтра з послідовності ключів */
    [[nodiscard]] static std::expected<XorFilter, FilterError>
    build(std::span<const uint64_t> keys) {
        if (keys.empty()) {
            return std::unexpected(FilterError::EmptyInput);
        }

        const size_t count = keys.size();
        uint32_t block_len = static_cast<uint32_t>((OverheadFactor * static_cast<double>(count)) / 3.0) + 1;
        if (block_len < 32) block_len = 32;
        const uint32_t total_slots = 3 * block_len;

        std::vector<uint8_t> hcount(total_slots, 0);
        std::vector<uint64_t> hxor(total_slots, 0);
        std::vector<uint32_t> queue(total_slots, 0);

        struct PeelEntry {
            uint64_t key;
            uint32_t index;
        };
        std::vector<PeelEntry> stack;
        stack.reserve(count);

        uint64_t seed = 0x8543290134ULL;
        bool success = false;

        for (int attempt = 0; attempt < MaxBuildAttempts; ++attempt) {
            seed = hash64(seed + attempt, 0x9e3779b97f4a7c15ULL);
            std::fill(hcount.begin(), hcount.end(), 0);
            std::fill(hxor.begin(), hxor.end(), 0);
            stack.clear();

            for (uint64_t key : keys) {
                auto [h0, h1, h2] = get_positions(key, seed, block_len);
                hcount[h0]++; hxor[h0] ^= key;
                hcount[h1]++; hxor[h1] ^= key;
                hcount[h2]++; hxor[h2] ^= key;
            }

            uint32_t q_head = 0, q_tail = 0;
            for (uint32_t i = 0; i < total_slots; ++i) {
                if (hcount[i] == 1) {
                    queue[q_tail++] = i;
                }
            }

            while (q_head < q_tail) {
                uint32_t slot = queue[q_head++];
                if (hcount[slot] != 1) continue;

                uint64_t key = hxor[slot];
                stack.push_back({key, slot});

                auto [h0, h1, h2] = get_positions(key, seed, block_len);
                const std::array<uint32_t, 3> neighbors = {h0, h1, h2};

                for (uint32_t neighbor : neighbors) {
                    hcount[neighbor]--;
                    hxor[neighbor] ^= key;
                    if (hcount[neighbor] == 1) {
                        queue[q_tail++] = neighbor;
                    }
                }
            }

            if (stack.size() == count) {
                success = true;
                break;
            }
        }

        if (!success) {
            return std::unexpected(FilterError::PeelingFailedExceededAttempts);
        }

        /* Фаза зворотної підстановки */
        XorFilter filter;
        filter.seed_ = seed;
        filter.block_length_ = block_len;
        filter.fingerprints_.resize(total_slots, 0);

        for (auto it = stack.rbegin(); it != stack.rend(); ++it) {
            const uint64_t key = it->key;
            const uint32_t slot = it->index;
            const FingerprintType fp = compute_fingerprint(key, filter.seed_);

            auto [h0, h1, h2] = get_positions(key, filter.seed_, block_len);
            const std::array<uint32_t, 3> pos = {h0, h1, h2};

            FingerprintType other_xor = 0;
            for (uint32_t p : pos) {
                if (p != slot) {
                    other_xor ^= filter.fingerprints_[p];
                }
            }
            filter.fingerprints_[slot] = fp ^ other_xor;
        }

        return filter;
    }

    /* Швидка перевірка належності O(1) */
    [[nodiscard]] bool contains(uint64_t key) const noexcept {
        if (fingerprints_.empty()) return false;

        auto [h0, h1, h2] = get_positions(key, seed_, block_length_);
        const FingerprintType fp = compute_fingerprint(key, seed_);

        const FingerprintType combined = fingerprints_[h0] ^
                                         fingerprints_[h1] ^
                                         fingerprints_[h2];

        return (combined == fp);
    }

    [[nodiscard]] size_t size_in_bytes() const noexcept {
        return sizeof(*this) + fingerprints_.size() * sizeof(FingerprintType);
    }

    [[nodiscard]] uint32_t block_length() const noexcept { return block_length_; }
    [[nodiscard]] uint64_t seed() const noexcept { return seed_; }

private:
    uint64_t seed_{0};
    uint32_t block_length_{0};
    std::vector<FingerprintType> fingerprints_;

    static constexpr uint64_t hash64(uint64_t x, uint64_t seed) noexcept {
        x ^= seed;
        x ^= x >> 33;
        x *= 0xff51afd7ed558ccdULL;
        x ^= x >> 33;
        x *= 0xc4ceb9fe1a85ec53ULL;
        x ^= x >> 33;
        return x;
    }

    static constexpr uint32_t reduce(uint32_t hash, uint32_t n) noexcept {
        return static_cast<uint32_t>((static_cast<uint64_t>(hash) * static_cast<uint64_t>(n)) >> 32);
    }

    static std::array<uint32_t, 3> get_positions(uint64_t key, uint64_t seed, uint32_t block_len) noexcept {
        const uint64_t hash = hash64(key, seed);
        const uint32_t a = static_cast<uint32_t>(hash >> 32);
        const uint32_t b = static_cast<uint32_t>(hash);
        const uint32_t c = static_cast<uint32_t>(hash ^ (hash >> 16));

        return {
            reduce(a, block_len),
            block_len + reduce(b, block_len),
            2 * block_len + reduce(c, block_len)
        };
    }

    static FingerprintType compute_fingerprint(uint64_t key, uint64_t seed) noexcept {
        const uint64_t hash = hash64(key, ~seed);
        auto fp = static_cast<FingerprintType>(hash ^ (hash >> 32));
        return (fp == 0) ? 1 : fp;
    }
};

} // namespace algorithms
```
:::

## Крайові випадки та правила експлуатації

Під час інтеграції Xor-фільтра у високонавантажені сховища необхідно враховувати специфічні особливості алгоритму:

1. **Дублікати ключів у вхідному масиві**:
   Якщо вхідний масив містить однакові ключі `k₁ == k₂`, вони додадуть однакові гіперребра `(h₀, h₁, h₂)`. У накопичувачі `HXor` ці ключі взаємно знищаться (`k ⊕ k = 0`), а лічильник `HCount` отримає значення 2. В результаті вершина ніколи не стане степенем 1, і лущення завершиться невдачею. Тому перед викликом методу побудови вхідні ключі **повинні бути дедупліковані** (наприклад, через `std::sort` та `std::unique`).

2. **Мінімальний розмір набору ключів**:
   Для дуже малих множин (`N < 32`) випадкові флуктуації розподілу можуть підвищувати ймовірність утворення циклічних ядер. Для запобігання збоям мінімальна довжина блоку `block_length` штучно обмежується значенням не менше 32 слотів.

3. **Незмінність після побудови**:
   Xor-фільтр є строго статичною структурою. Додавання нового ключа до вже розрахованого масиву неможливе без повної перебудови, оскільки зміна навіть одного слота порушить рівняння для раніше розміщених ключів. У системах зі змішуванням даних (наприклад, у LSM-деревах) фільтр генерується один раз у момент злиття (compaction) та скидання SSTable на диск.

4. **Пакетна обробка та векторні інструкції SIMD**:
   Оскільки операція перевірки не має умовних переходів, запити можна легко обробляти пакетами по 4, 8 або 16 ключів, завантажуючи значення слотів за допомогою інструкцій векторного збору `_mm256_i32gather_epi32` (AVX2). Це дозволяє досягти пропускної здатності понад 80–120 мільйонів перевірок на секунду на одному ядрі процесора.
