# ⚙️ Реалізація потокового голосування Бойєра — Мура та алгоритму Місри — Гріса

Практична реалізація алгоритмів пошуку елементів більшості та частих запитів у високопродуктивних системах вимагає глибокого врахування апаратних особливостей сучасних процесорів: ефективного використання регістрового файлу, мінімізації розгалужень (branch mispredictions), векторної обробки SIMD та коректного злиття станів у багатопотокових середовищах.

## Архітектура потокового акумулятора та двопрохідний верифікатор

Базова інженерна структура алгоритму Бойєра — Мура розділяється на два незалежні модулі: потоковий акумулятор (`Accumulator`), який оновлює поточного кандидата на льоту для кожного елемента, та фазу верифікації (`Verifier`), яка підраховує точну частоту знайденого кандидата для масивів із довільним розподілом даних.

У потоковому акумуляторі критично важливо забезпечити мінімальний розмір структури стану. Оскільки стан складається лише зі значення кандидата та числового лічильника, вся структура займає лише 8–16 байтів. Це гарантує, що змінні стану повністю розміщуються в регістрах процесора (наприклад, `RAX` та `RCX` в архітектурі x86-64), не спричиняючи жодних звернень до кеш-пам'яті першого рівня L1 під час обробки нескінченного потоку.

Для порівняння: підхід на базі хеш-таблиці (`std::unordered_map` у C++ або масив колізійних ланцюжків у C) вимагає динамічного виділення пам'яті в купі під кожен новий унікальний ключ. Це спричиняє промахи кешу L1/L2, деградацію швидкості через фрагментацію пам'яті та непрогнозовані затримки при зміні розміру таблиці (rehashing). Алгоритм Бойєра — Мура гарантує строго детерміновану затримку виконання (зазвичай 1–3 такти процесора на елемент).

Нижче наведено повну реалізацію базового акумулятора та двопрохідного пошуку мовами C та C++.

:::tabs
```c
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
    int32_t candidate;
    size_t count;
} MajorityVoteState;

/* Ініціалізація стану потокового акумулятора */
void majority_state_init(MajorityVoteState *state) {
    state->candidate = 0;
    state->count = 0;
}

/* Однопрохідне потокове оновлення стану для нового елемента */
void majority_state_update(MajorityVoteState *state, int32_t x) {
    if (state->count == 0) {
        state->candidate = x;
        state->count = 1;
    } else if (state->candidate == x) {
        state->count++;
    } else {
        state->count--;
    }
}

/* Повний двопрохідний алгоритм із верифікацією */
bool find_majority_element(const int32_t *data, size_t size, int32_t *out_majority) {
    if (data == NULL || size == 0 || out_majority == NULL) {
        return false;
    }

    MajorityVoteState state;
    majority_state_init(&state);

    /* Прохід 1: Знаходження потенційного кандидата */
    for (size_t i = 0; i < size; ++i) {
        majority_state_update(&state, data[i]);
    }

    /* Якщо лічильник дорівнює нулю, більшості точно немає */
    if (state.count == 0) {
        return false;
    }

    /* Прохід 2: Точний підрахунок частоти кандидата */
    size_t actual_count = 0;
    for (size_t i = 0; i < size; ++i) {
        if (data[i] == state.candidate) {
            actual_count++;
        }
    }

    if (actual_count > size / 2) {
        *out_majority = state.candidate;
        return true;
    }

    return false;
}
```
```cpp
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

template <std::equality_comparable T>
class MajorityVoteAccumulator {
public:
    constexpr MajorityVoteAccumulator() noexcept = default;

    constexpr void update(const T& value) noexcept {
        if (count_ == 0) {
            candidate_ = value;
            count_ = 1;
        } else if (candidate_ == value) {
            ++count_;
        } else {
            --count_;
        }
    }

    [[nodiscard]] constexpr std::optional<T> candidate() const noexcept {
        if (count_ > 0) {
            return candidate_;
        }
        return std::nullopt;
    }

    [[nodiscard]] constexpr std::size_t surplus() const noexcept {
        return count_;
    }

    constexpr void reset() noexcept {
        candidate_ = T{};
        count_ = 0;
    }

private:
    T candidate_{};
    std::size_t count_{0};
};

template <std::equality_comparable T>
[[nodiscard]] std::optional<T> find_majority_element(std::span<const T> data) noexcept {
    if (data.empty()) {
        return std::nullopt;
    }

    MajorityVoteAccumulator<T> tracker;
    for (const auto& item : data) {
        tracker.update(item);
    }

    const auto cand = tracker.candidate();
    if (!cand.has_value()) {
        return std::nullopt;
    }

    std::size_t actual_count = 0;
    for (const auto& item : data) {
        if (item == *cand) {
            ++actual_count;
        }
    }

    if (actual_count > data.size() / 2) {
        return cand;
    }

    return std::nullopt;
}
```
:::

## Аналіз крайових випадків та перевірка коректності

Для забезпечення надійності вбудованого коду необхідно протестувати поведінку алгоритму на характерних граничних наборах даних:

1. **Порожній вхідний масив (`size == 0`)**: Обидві реалізації коректно перевіряють розмір і повертають `false` (або `std::nullopt` у C++), не здійснюючи небезпечного розіменування нульового вказівника.
2. **Масив з одного елемента (`[X]`)**: На першому кроці `candidate = X`, `count = 1`. Другий прохід підтверджує частоту `1 > 1/2 = 0.5`. Результат: знайдено `X`.
3. **Усі елементи однакові (`[A, A, A, A]`)**: Лічильник монотонно зростає до `count = N`. Верифікація миттєво підтверджує 100% частоту.
4. **Рівний баланс двох кандидатів (`[A, A, B, B]`)**: Лічильник після обробки пари `(A, B)` стає рівним нулю. Прохід 1 завершується з `count = 0` або випадковим кандидатом, але другий прохід виявляє точну частоту `2`, що не перевищує поріг `4 / 2 = 2` (потрібна строга нерівність `> 2`). Результат: більшість відсутня.
5. **Розрив чергування (`[A, B, A, B, A]`)**: Лічильник почергово падає до нуля та знову піднімається до 1. Фінальний стан: `candidate = A`, `count = 1`. Другий прохід підтверджує частоту `3 > 5/2 = 2.5`.

## Оптимізація без розгалужень (Branchless Execution)

У високошвидкісних мережевих конвеєрах традиційні умовні переходи `if-else` всередині гарячого циклу можуть спричиняти часті промахи блоку передбачення переходів процесора (Branch Misprediction), коли дані чергуються псевдовипадковим чином. Штраф за промах конвеєра на сучасних процесорах (Intel Golden Cove, AMD Zen 4) становить від 12 до 20 тактів.

Використання безрозгалуженої арифметичної логіки дозволяє компілятору згенерувати інструкції умовного копіювання (`cmov` в архітектурі x86-64 або `csel` в ARM64). Такі інструкції виконуються за фіксовану кількість тактів (зазвичай 1 такт) незалежно від патерну вхідних даних, що усуває простої конвеєра.

:::tabs
```c
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Безрозгалужена версія оновлення лічильника */
void majority_update_branchless(int32_t *candidate, int32_t *count, int32_t x) {
    /* Якщо count == 0, кандидат заміщується на x */
    int32_t is_zero = (*count == 0);
    *candidate = is_zero ? x : *candidate;
    
    /* delta = +1 якщо x == candidate, інакше -1 */
    int32_t is_match = (*candidate == x);
    int32_t delta = (is_match << 1) - 1; /* 1 -> +1, 0 -> -1 */
    
    /* Якщо count було 0, новий count стає 1 */
    *count = is_zero ? 1 : (*count + delta);
}

int32_t find_candidate_branchless(const int32_t *data, size_t size) {
    int32_t candidate = 0;
    int32_t count = 0;

    for (size_t i = 0; i < size; ++i) {
        int32_t x = data[i];
        int32_t is_zero = (count == 0);
        candidate = is_zero ? x : candidate;
        count = is_zero ? 1 : (count + ((candidate == x) ? 1 : -1));
    }

    return candidate;
}
```
```cpp
#include <cstddef>
#include <cstdint>
#include <span>

class BranchlessMajorityTracker {
public:
    [[nodiscard]] static int32_t find_candidate(std::span<const int32_t> stream) noexcept {
        int32_t candidate = 0;
        int32_t count = 0;

        for (const int32_t value : stream) {
            const bool is_zero = (count == 0);
            candidate = is_zero ? value : candidate;
            count = is_zero ? 1 : (count + ((candidate == value) ? 1 : -1));
        }

        return candidate;
    }
};
```
:::

## Паралельне злиття станів (Map-Reduce Merge)

Коли вхідний потік даних шардований між кількома процесорними ядрами або вузлами розподіленого кластера, кожен потік може незалежно обробити свою частину масиву та повернути локальну пару `(candidate, count)`.

Оператор злиття двох станів спирається на той самий принцип взаємного знищення:
* Якщо локальні кандидати збігаються, їхні лічильники переваги додаються.
* Якщо кандидати відрізняються, їхні лічильники віднімаються, а виживає кандидат із більшим лічильником.

Ця операція є строго комутативною та асоціативною, що дозволяє виконувати паралельну деревоподібну редукцію (Tree-based Reduction) масиву довільного розміру на GPU або багатоядерних процесорах за логарифмічний час `O(log P)`, де `P` — кількість потоків обробки.

:::tabs
```c
#include <stddef.h>
#include <stdint.h>

typedef struct {
    int32_t candidate;
    size_t count;
} PartialMajority;

/* Асоціативний оператор злиття двох локальних результатів */
PartialMajority merge_majority_states(PartialMajority a, PartialMajority b) {
    if (a.count == 0) return b;
    if (b.count == 0) return a;

    if (a.candidate == b.candidate) {
        PartialMajority res = { a.candidate, a.count + b.count };
        return res;
    }

    if (a.count >= b.count) {
        PartialMajority res = { a.candidate, a.count - b.count };
        return res;
    } else {
        PartialMajority res = { b.candidate, b.count - a.count };
        return res;
    }
}
```
```cpp
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

template <std::equality_comparable T>
struct SummaryVote {
    T candidate{};
    std::size_t count{0};

    [[nodiscard]] constexpr friend SummaryVote operator+(const SummaryVote& lhs, const SummaryVote& rhs) noexcept {
        if (lhs.count == 0) return rhs;
        if (rhs.count == 0) return lhs;

        if (lhs.candidate == rhs.candidate) {
            return SummaryVote{ lhs.candidate, lhs.count + rhs.count };
        }

        if (lhs.count >= rhs.count) {
            return SummaryVote{ lhs.candidate, lhs.count - rhs.count };
        } else {
            return SummaryVote{ rhs.candidate, rhs.count - lhs.count };
        }
    }
};
```
:::

## Узагальнений алгоритм Місри — Гріса для k частих елементів

Для виявлення всіх елементів, чия частота перевищує `N / k`, підтримується фіксований асоціативний масив із `k - 1` слотів. Нижче наведено оптимізовану реалізацію для `k = 3` (пошук елементів із частотою строго більше ніж 33.33% від загального обсягу потоку).

Узагальнення використовує масив фіксованого розміру `std::array` у C++, що гарантує відсутність будь-яких динамічних виділень пам'яті в купі під час потокової обробки. Це дозволяє вбудовувати структуру безпосередньо у статичні дескриптори мережевих сокетів або пам'ять ядер реального часу (RTOS).

:::tabs
```c
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define MG_K 3
#define MG_SLOTS (MG_K - 1)

typedef struct {
    int32_t candidate[MG_SLOTS];
    size_t count[MG_SLOTS];
} MisraGries3State;

void mg3_init(MisraGries3State *state) {
    for (size_t i = 0; i < MG_SLOTS; ++i) {
        state->candidate[i] = 0;
        state->count[i] = 0;
    }
}

void mg3_update(MisraGries3State *state, int32_t x) {
    /* 1. Перевірка чи елемент вже є серед кандидатів */
    for (size_t i = 0; i < MG_SLOTS; ++i) {
        if (state->count[i] > 0 && state->candidate[i] == x) {
            state->count[i]++;
            return;
        }
    }

    /* 2. Пошук порожнього слота */
    for (size_t i = 0; i < MG_SLOTS; ++i) {
        if (state->count[i] == 0) {
            state->candidate[i] = x;
            state->count[i] = 1;
            return;
        }
    }

    /* 3. Всі слоти зайняті та елемент новий: групове скорочення */
    for (size_t i = 0; i < MG_SLOTS; ++i) {
        state->count[i]--;
    }
}
```
```cpp
#include <array>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

template <std::equality_comparable T, std::size_t K>
    requires (K >= 2)
class MisraGriesHeavyHitters {
public:
    static constexpr std::size_t SlotCount = K - 1;

    constexpr MisraGriesHeavyHitters() noexcept {
        for (auto& slot : slots_) {
            slot.count = 0;
        }
    }

    constexpr void update(const T& item) noexcept {
        // 1. Пошук чи елемент вже відслідковується
        for (auto& slot : slots_) {
            if (slot.count > 0 && slot.candidate == item) {
                ++slot.count;
                return;
            }
        }

        // 2. Пошук вільного слота
        for (auto& slot : slots_) {
            if (slot.count == 0) {
                slot.candidate = item;
                slot.count = 1;
                return;
            }
        }

        // 3. Групове скорочення лічильників усіх кандидатів
        for (auto& slot : slots_) {
            --slot.count;
        }
    }

    [[nodiscard]] std::vector<T> candidates() const {
        std::vector<T> result;
        result.reserve(SlotCount);
        for (const auto& slot : slots_) {
            if (slot.count > 0) {
                result.push_back(slot.candidate);
            }
        }
        return result;
    }

private:
    struct Slot {
        T candidate{};
        std::size_t count{0};
    };

    std::array<Slot, SlotCount> slots_{};
};
```
:::

## Векторизація SIMD та профілювання продуктивності

Для досягнення максимальної пропускної здатності на сучасних процесорах фаза верифікації (підрахунок частоти знайденого кандидата) може бути прискорена за допомогою векторних розширень SIMD (AVX2 / AVX-512 для x86-64 або ARM NEON).

Під час верифікації масив чисел порівнюється з вектором, заповненим значенням кандидата (наприклад, 8 елементів `int32_t` одночасно у 256-бітному регістрі `__m256i`). Інструкція `_mm256_cmpeq_epi32` формує бітову маску рівності, яка після операції `_mm256_movemask_epi8` та апаратного підрахунку встановлених бітів через інструкцію `popcnt` дає точну кількість збігів за мінімальну кількість тактів.

Такий підхід дозволяє обробляти понад 40 гігабайт пам'яті на секунду на одному ядрі, досягаючи пропускної здатності, обмеженої лише швидкістю системної шини оперативної пам'яті DRAM.

Розглянемо практичну векторну реалізацію підрахунку частоти для архітектури x86-64 з використанням інтринсиків AVX2:

:::tabs
```c
#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>

/* Векторний підрахунок частоти кандидата через AVX2 */
size_t count_frequency_avx2(const int32_t *data, size_t size, int32_t target) {
    size_t count = 0;
    size_t i = 0;

    __m256i target_vec = _mm256_set1_epi32(target);

    /* Обробка блоками по 8 елементів (256 біт) */
    for (; i + 8 <= size; i += 8) {
        __m256i chunk = _mm256_loadu_si256((const __m256i*)(data + i));
        __m256i match = _mm256_cmpeq_epi32(chunk, target_vec);
        int mask = _mm256_movemask_epi8(match);
        if (mask != 0) {
            /* Кожен збіг 32-бітного числа дає 4 біти в масці movemask */
            count += (size_t)__builtin_popcount(mask) / 4;
        }
    }

    /* Дообробка залишку масиву */
    for (; i < size; ++i) {
        if (data[i] == target) {
            count++;
        }
    }

    return count;
}
```
```cpp
#include <immintrin.h>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <span>

class SimdVerifier {
public:
    [[nodiscard]] static std::size_t count_frequency(std::span<const int32_t> data, int32_t target) noexcept {
        std::size_t count = 0;
        std::size_t i = 0;
        const std::size_t size = data.size();
        const int32_t* ptr = data.data();

        const __m256i target_vec = _mm256_set1_epi32(target);

        for (; i + 8 <= size; i += 8) {
            const __m256i chunk = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(ptr + i));
            const __m256i match = _mm256_cmpeq_epi32(chunk, target_vec);
            const int mask = _mm256_movemask_epi8(match);
            if (mask != 0) {
                count += static_cast<std::size_t>(std::popcount(static_cast<unsigned int>(mask))) / 4;
            }
        }

        for (; i < size; ++i) {
            if (ptr[i] == target) {
                ++count;
            }
        }

        return count;
    }
};
```
:::

Застосування векторного підрахунку у поєднанні з безрозгалуженим першим проходом забезпечує найвищу можливу продуктивність на сучасних серверних процесорах.
