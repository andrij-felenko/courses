# ⚙️ Динамічна бітова множина: векторний бітсет з апаратним скануванням

Стандартний контейнер `std::bitset<N>` у стандартній бібліотеці C++ має фіксований розмір `N`, який обов'язково повинен бути відомий ще на етапі компіляції програми. Проте в більшості реальних інженерних застосунків — таких як інвертовані пошукові індекси, алгоритми аналізу графів, бази даних та динамічні алокатори пам'яті — точний діапазон ідентифікаторів з'ясовується лише під час виконання. Спеціалізація `std::vector<bool>` хоч і упаковує кожен логічний елемент в один біт, має критичні недоліки для системного програмування: її оператор індексації `operator[]` повертає важкий проксі-об'єкт `std::vector<bool>::reference`, блокує прямий доступ до слів пам'яті через покажчики, унеможливлює векторизацію та не надає швидких методів підрахунку встановлених бітів чи апаратного пошуку наступного елемента.

Нижче наведено промислову реалізацію динамічного бітсета мовами C та C++20. Структура оперує безпосередньо суцільним масивом 64-бітних машинних слів `uint64_t`, забезпечує вирівнювання пам'яті, коректно обробляє хвостові біти та використовує апаратні інструкції процесора `POPCNT` і `CTZ` для миттєвої ітерації.

### Архітектура та математика побітової адресації

Динамічний бітсет виділяє в купі суцільний буфер пам'яті, що складається з масиву беззнакових 64-бітних слів `uint64_t`. Загальна кількість слів `num_words`, необхідна для збереження `num_bits` елементів, розраховується за формулою заокруглення вгору:

```
num_words = (num_bits + 63) / 64
```

Для довільного бітового індексу `i` адресація розкладається на три швидкі побітові операції:
1. **Індекс слова у масиві (`word_index`):** визначається цілочисельним діленням на 64. Оскільки 64 є степенем двійки (`2⁶ = 64`), ділення еквівалентне зсуву праворуч на 6 розрядів: `i >> 6`.
2. **Зміщення біта всередині слова (`bit_offset`):** залишок від ділення на 64. Обчислюється як побітове `AND` з маскою 63: `i & 63` (у двійковій системі це `0011 1111₂`).
3. **Бітова маска розряду (`mask`):** одиничний 64-бітний біт, зсунутий на відповідне зміщення: `1ULL << bit_offset`.

#### Обробка хвостових бітів (Tail Masking)

Якщо загальна кількість бітів `num_bits` не кратна 64, останнє слово масиву містить невикористані «зайві» бітові позиції. Якщо користувач викликає операцію інверсії `NOT` або заповнення одиницями `set_all()`, ці невикористані біти стануть одиницями. Це призведе до спотворення результатів: функція підрахунку елементів `popcount()` поверне завищене число, а ітератори почнуть видавати неіснуючі індекси за межами розміру бітсета.

Для усунення цієї проблеми реалізовано очищення хвостового слова за допомогою маски `last_word_mask`:

```
last_word_mask = (num_bits & 63) == 0 ? ~0ULL : ((1ULL << (num_bits & 63)) - 1ULL);
```

Будь-яка операція, що потенційно модифікує невикористані розряди, наприкінці накладає цю маску через побітове `AND` на останній елемент масиву.

### Повна реалізація мовами C та C++20

Нижче наведено повний вихідний код. Версія для C містить функції з ручним керуванням пам'яттю та перевірками меж, а версія для C++20 інкапсулює логіку в безпечний клас з семантикою переміщення, підтримкою `std::span` та стандартних функцій заголовка `<bit>`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define BITSET_NOT_FOUND ((size_t)-1)

typedef struct {
    uint64_t *words;
    size_t num_bits;
    size_t num_words;
} BitSet;

static inline size_t bitset_calc_words(size_t bits) {
    return (bits + 63) / 64;
}

static inline uint64_t bitset_get_tail_mask(size_t bits) {
    size_t rem = bits & 63;
    return rem == 0 ? ~0ULL : ((1ULL << rem) - 1ULL);
}

BitSet* bitset_create(size_t num_bits) {
    BitSet *bs = (BitSet*)malloc(sizeof(BitSet));
    if (!bs) return NULL;

    bs->num_bits = num_bits;
    bs->num_words = bitset_calc_words(num_bits);
    
    /* Виділяємо та обнуляємо пам'ять під слова */
    bs->words = (uint64_t*)calloc(bs->num_words > 0 ? bs->num_words : 1, sizeof(uint64_t));
    if (!bs->words) {
        free(bs);
        return NULL;
    }
    return bs;
}

void bitset_destroy(BitSet *bs) {
    if (bs) {
        free(bs->words);
        free(bs);
    }
}

void bitset_set(BitSet *bs, size_t i) {
    if (i < bs->num_bits) {
        bs->words[i >> 6] |= (1ULL << (i & 63));
    }
}

void bitset_clear(BitSet *bs, size_t i) {
    if (i < bs->num_bits) {
        bs->words[i >> 6] &= ~(1ULL << (i & 63));
    }
}

bool bitset_test(const BitSet *bs, size_t i) {
    if (i >= bs->num_bits) return false;
    return (bs->words[i >> 6] & (1ULL << (i & 63))) != 0;
}

void bitset_fill_zeros(BitSet *bs) {
    if (bs->num_words > 0) {
        memset(bs->words, 0, bs->num_words * sizeof(uint64_t));
    }
}

void bitset_fill_ones(BitSet *bs) {
    if (bs->num_words == 0) return;
    memset(bs->words, 0xFF, bs->num_words * sizeof(uint64_t));
    /* Очищуємо зайві біти в останньому слові */
    bs->words[bs->num_words - 1] &= bitset_get_tail_mask(bs->num_bits);
}

/* Підрахунок потужності множини через апаратний POPCNT */
size_t bitset_popcount(const BitSet *bs) {
    size_t total = 0;
    for (size_t w = 0; w < bs->num_words; ++w) {
        total += (size_t)__builtin_popcountll(bs->words[w]);
    }
    return total;
}

/* Пошук першого встановленого біта (найменшого елемента) через CTZ */
size_t bitset_find_first(const BitSet *bs) {
    for (size_t w = 0; w < bs->num_words; ++w) {
        uint64_t val = bs->words[w];
        if (val != 0) {
            size_t bit_pos = (w << 6) + (size_t)__builtin_ctzll(val);
            return (bit_pos < bs->num_bits) ? bit_pos : BITSET_NOT_FOUND;
        }
    }
    return BITSET_NOT_FOUND;
}

/* Пошук наступного встановленого біта після поточної позиції curr */
size_t bitset_find_next(const BitSet *bs, size_t curr) {
    size_t next_idx = curr + 1;
    if (next_idx >= bs->num_bits) return BITSET_NOT_FOUND;

    size_t w = next_idx >> 6;
    size_t offset = next_idx & 63;

    /* Маскуємо вже пройдені молодші біти в поточному слові */
    uint64_t val = bs->words[w] & (~0ULL << offset);
    if (val != 0) {
        size_t bit_pos = (w << 6) + (size_t)__builtin_ctzll(val);
        return (bit_pos < bs->num_bits) ? bit_pos : BITSET_NOT_FOUND;
    }

    /* Скануємо наступні слова */
    for (w = w + 1; w < bs->num_words; ++w) {
        val = bs->words[w];
        if (val != 0) {
            size_t bit_pos = (w << 6) + (size_t)__builtin_ctzll(val);
            return (bit_pos < bs->num_bits) ? bit_pos : BITSET_NOT_FOUND;
        }
    }
    return BITSET_NOT_FOUND;
}

/* Операції над множинами: dst = dst OP src */
bool bitset_intersect(BitSet *dst, const BitSet *src) {
    if (dst->num_bits != src->num_bits) return false;
    for (size_t w = 0; w < dst->num_words; ++w) {
        dst->words[w] &= src->words[w];
    }
    return true;
}

bool bitset_union(BitSet *dst, const BitSet *src) {
    if (dst->num_bits != src->num_bits) return false;
    for (size_t w = 0; w < dst->num_words; ++w) {
        dst->words[w] |= src->words[w];
    }
    dst->words[dst->num_words - 1] &= bitset_get_tail_mask(dst->num_bits);
    return true;
}

bool bitset_difference(BitSet *dst, const BitSet *src) {
    if (dst->num_bits != src->num_bits) return false;
    for (size_t w = 0; w < dst->num_words; ++w) {
        dst->words[w] &= ~src->words[w];
    }
    return true;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <bit>
#include <algorithm>
#include <limits>
#include <iostream>

class DynamicBitset {
public:
    static constexpr std::size_t npos = std::numeric_limits<std::size_t>::max();

    explicit DynamicBitset(std::size_t num_bits = 0)
        : num_bits_(num_bits),
          words_((num_bits + 63) / 64, 0ULL) {}

    [[nodiscard]] std::size_t size() const noexcept { return num_bits_; }
    [[nodiscard]] std::size_t word_count() const noexcept { return words_.size(); }
    [[nodiscard]] bool empty() const noexcept { return num_bits_ == 0; }

    void set(std::size_t i) {
        if (i < num_bits_) {
            words_[i >> 6] |= (1ULL << (i & 63));
        }
    }

    void reset(std::size_t i) {
        if (i < num_bits_) {
            words_[i >> 6] &= ~(1ULL << (i & 63));
        }
    }

    [[nodiscard]] bool test(std::size_t i) const noexcept {
        if (i >= num_bits_) return false;
        return (words_[i >> 6] & (1ULL << (i & 63))) != 0;
    }

    void reset_all() noexcept {
        std::fill(words_.begin(), words_.end(), 0ULL);
    }

    void set_all() noexcept {
        if (words_.empty()) return;
        std::fill(words_.begin(), words_.end(), ~0ULL);
        trim_tail();
    }

    /* Підрахунок потужності множини через std::popcount (C++20) */
    [[nodiscard]] std::size_t count() const noexcept {
        std::size_t total = 0;
        for (std::uint64_t w : words_) {
            total += static_cast<std::size_t>(std::popcount(w));
        }
        return total;
    }

    /* Пошук першого елемента через std::countr_zero (C++20) */
    [[nodiscard]] std::size_t find_first() const noexcept {
        for (std::size_t w = 0; w < words_.size(); ++w) {
            if (words_[w] != 0) {
                std::size_t pos = (w << 6) + static_cast<std::size_t>(std::countr_zero(words_[w]));
                return (pos < num_bits_) ? pos : npos;
            }
        }
        return npos;
    }

    /* Пошук наступного встановленого біта */
    [[nodiscard]] std::size_t find_next(std::size_t curr) const noexcept {
        size_t next_idx = curr + 1;
        if (next_idx >= num_bits_) return npos;

        std::size_t w = next_idx >> 6;
        std::size_t offset = next_idx & 63;

        std::uint64_t val = words_[w] & (~0ULL << offset);
        if (val != 0) {
            std::size_t pos = (w << 6) + static_cast<std::size_t>(std::countr_zero(val));
            return (pos < num_bits_) ? pos : npos;
        }

        for (++w; w < words_.size(); ++w) {
            if (words_[w] != 0) {
                std::size_t pos = (w << 6) + static_cast<std::size_t>(std::countr_zero(words_[w]));
                return (pos < num_bits_) ? pos : npos;
            }
        }
        return npos;
    }

    /* Побітові оператори над множинами */
    DynamicBitset& operator&=(const DynamicBitset& other) noexcept {
        std::size_t n = std::min(words_.size(), other.words_.size());
        for (std::size_t i = 0; i < n; ++i) {
            words_[i] &= other.words_[i];
        }
        return *this;
    }

    DynamicBitset& operator|=(const DynamicBitset& other) noexcept {
        std::size_t n = std::min(words_.size(), other.words_.size());
        for (std::size_t i = 0; i < n; ++i) {
            words_[i] |= other.words_[i];
        }
        trim_tail();
        return *this;
    }

    DynamicBitset& operator^=(const DynamicBitset& other) noexcept {
        std::size_t n = std::min(words_.size(), other.words_.size());
        for (std::size_t i = 0; i < n; ++i) {
            words_[i] ^= other.words_[i];
        }
        trim_tail();
        return *this;
    }

    DynamicBitset operator~() const {
        DynamicBitset res = *this;
        for (auto& w : res.words_) {
            w = ~w;
        }
        res.trim_tail();
        return res;
    }

    [[nodiscard]] std::span<const std::uint64_t> words() const noexcept {
        return words_;
    }

private:
    void trim_tail() noexcept {
        if (!words_.empty()) {
            std::size_t rem = num_bits_ & 63;
            if (rem != 0) {
                words_.back() &= ((1ULL << rem) - 1ULL);
            }
        }
    }

    std::size_t num_bits_{0};
    std::vector<std::uint64_t> words_{};
};
```
:::

### Покроковий розбір алгоритму find_next()

Ключовою функцією для ефективного використання бітової множини є `find_next(curr)`. Вона дозволяє знайти наступний встановлений розряд після позиції `curr` без повного перебору бітів. Її виконання складається з двох послідовних фаз:

1. **Фаза поточного слова:** Обчислюється наступний індекс `next_idx = curr + 1`, його номер слова `w = next_idx >> 6` та зміщення `offset = next_idx & 63`. Щоб проігнорувати біти, які розташовані ліворуч від `offset` (тобто вже пройдені молодші позиції), до поточного слова застосовується маска `~0ULL << offset`. Якщо після маскування слово `val` не дорівнює нулю, найменший встановлений біт визначається за один машинний такт інструкцією `std::countr_zero(val)` (або `__builtin_ctzll`).
2. **Фаза наступних слів:** Якщо в поточному слові після позиції `offset` одиниць не лишилося, цикл переходить до наступних слів `words[w+1]...`. Усі цілі нульові слова пропускаються за одну перевірку регістра `if (val != 0)`. Щойно знайдено перше ненульове слово, інструкція `CTZ` повертає точну позицію першої одиниці в ньому.

### Алгоритмічний аналіз та обчислювальна складність

Представлена структура даних забезпечує оптимальні характеристики продуктивності для всіх фундаментальних операцій:

| Операція | Функція | Часова складність | Просторовий оверхед | Примітка |
|---|---|---|---|---|
| Перевірка належності | `test(i)` | `O(1)` | 0 байтів | 1 операція зсуву та маскування |
| Встановлення біта | `set(i)` | `O(1)` | 0 байтів | 1 операція побітового `OR` |
| Скидання біта | `reset(i)` | `O(1)` | 0 байтів | 1 операція побітового `AND-NOT` |
| Потужність множини | `count()` | `O(N / 64)` | 0 байтів | Використовує апаратну команду `POPCNT` |
| Перетин множин | `operator&=` | `O(N / 64)` | 0 байтів | 64 пари бітів за 1 машинну дію |
| Пошук наступного біта | `find_next()` | `O(S)` слів | 0 байтів | Пропускає нульові слова за 1 такт ЦП |

### Швидка ітерація без перевірки нульових слів

Найбільша практична вигода представлення `DynamicBitset` полягає в швидкості ітерації. Замість перевірки кожного біта з перебором `N` кроків, код сканує масив цілими 64-бітними словами:

```cpp
void process_set_elements(const DynamicBitset& bs) {
    for (std::size_t idx = bs.find_first(); idx != DynamicBitset::npos; idx = bs.find_next(idx)) {
        // Опрацьовуємо лише дійсно присутні елементи множини
        std::cout << "Елемент у множині: " << idx << "\n";
    }
}
```

Якщо множина містить 10 елементів у діапазоні `0 … 1 000 000`, наївний цикл виконає 1 000 000 ітерацій. Алгоритм на базі `std::countr_zero` та пропуску нульових слів виконає рівно 15 625 перевірок слів і лише 10 викликів тіла обробки, прискорюючи фільтрацію у сотні разів.

### Вирівнювання пам'яті під векторні інструкції SIMD

Для досягнення максимальної швидкості побітових операцій над великими бітовими множинами буфер слів повинен бути вирівняний в оперативній пам'яті по межі кеш-лінії або векторного регістра (32 байти для AVX2 або 64 байти для AVX-512). Невирівняний доступ до пам'яті призводить до того, що одне завантаження регістра перетинає межу двох фізичних кеш-ліній, подвоюючи кількість звернень до кешу L1 і сповільнюючи виконання.

Для виділення вирівняного буфера використовують системні виклики:
* У C: `posix_memalign((void**)&words, 64, num_words * sizeof(uint64_t))` або `aligned_alloc(64, num_words * sizeof(uint64_t))`
* У C++: `std::pmr::polymorphic_allocator` або перевантаження власного вирівняного алокатора для `std::vector`

Вирівняний масив дозволяє компілятору автоматично генерувати векторні команди `vpand`, `vpor`, `vpxor` над 256- та 512-бітними регістрами `ymm` / `zmm` без ризику падіння швидкодії на межах сторінок.

### Багатопотоковість та атомарні операції

У багатопотокових середовищах виникає явище **False Sharing** (помилкове спільне використання), якщо два незалежні потоки модифікують сусідні біти, що належать одному 64-бітному слову або одній 64-байтовій кеш-лінії процесора. Оскільки операція `words[w] |= mask` є неатомарною послідовністю «читання — модифікація — запис» (RMW, *Read-Modify-Write*), одночасний запис без синхронізації призведе до стану гонитви (*race condition*) та втрати даних.

Для безпечної конкурентної модифікації окремих бітів у спільному бітсеті необхідно використовувати атомарні інструкції:
* У C11: `atomic_fetch_or((_Atomic uint64_t*)&words[w], mask)`
* У C++20: `std::atomic_ref<std::uint64_t>(words[w]).fetch_or(mask, std::memory_order_relaxed)`

Ці команди генерують асемблерну інструкцію `LOCK BTS` (Bit Test and Set) або `LOCK OR` на архітектурі x86, гарантуючи коректність запису на рівні апаратного протоколу когерентності кешів процесора без використання важких м'ютексів.
