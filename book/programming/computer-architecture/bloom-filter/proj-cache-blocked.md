# ⚙️ Проєкт: Кеш-блочний фільтр Блума (Blocked Bloom Filter)

У системному програмуванні та високонавантажених сховищах даних класичний фільтр Блума часто демонструє парадоксальну поведінку: теоретично він має алгоритмічну складність `O(k)`, проте на реальному обладнанні працює у кілька разів повільніше за звичайну геш-таблицю з відкритою адресацією. Причина цього парадоксу полягає не в складності обчислень, а в апаратному устрої ієрархії пам'яті сучасних процесорів x86-64 та ARM64.

Коли розмір бітового масиву становить десятки чи сотні мегабайтів (наприклад, 100 мільйонів ключів вимагають близько 120 МБ пам'яті), цей масив виходить далеко за межі швидких кешів першого (L1), другого (L2) і навіть спільного третього (L3) рівнів. Якщо для кожного вхідного запиту обчислюється `k = 8` незалежних геш-функцій, кожна з них генерує випадковий бітовий індекс у абсолютно різних кінцях 120-мегабайтного адресного простору.

Як наслідок, одна-єдина перевірка ключа спричиняє до **восьми незалежних промахів кешу L3**, зупиняючи конвеєр процесора на 200–400 наносекунд в очікуванні транзакцій контролера DRAM. Процесорні ядра витрачають понад 90% часу на очікування шини пам'яті, а не на корисні обчислення.

**Кеш-блочний фільтр Блума** (*Cache-, Blocked- or Sector-Aligned Bloom Filter*) розв'язує цю фундаментальну проблему на рівні мікроархітектури, узгоджуючи роботу алгоритму з фізичною структурою кеш-ліній процесора.

---

### Архітектурна ідея: локалізація в межах однієї кеш-лінії

Замість одного монолітного бітового масиву пам'ять ділиться на масив незалежних **блоків по 64 байти** (512 бітів), що точно відповідає фізичному розміру кеш-лінії сучасних архітектур x86-64 та ARM.

1. **Вибір блоку (1 промах кешу):** перший 64-розрядний геш `h₀(key)` визначає номер 64-байтового блоку в пам'яті:
   `block_index = h₀(key) % num_blocks`.
2. **Завантаження в кеш:** процесор виконує рівно **одне** звернення до пам'яті, підтягуючи цілу 64-байтову лінію в найшвидший кеш L1.
3. **Локальне тестування:** наступні `k` бітових індексів генеруються та перевіряються **виключно всередині цих 512 бітів**, використовуючи швидкі побітові операції або векторні SIMD-інструкції AVX2/AVX-512.

Кількість промахів кешу на один запит падає з `k` до **рівно одного** (або нуля, якщо блок уже перебував у кеші), що збільшує пропускну здатність фільтра в 5–8 разів.

---

### Реалізація: C та ідіоматичний C++20

Нижче наведено повну, компільовану та працездатну реалізацію кеш-блочного фільтра Блума. Пам'ять гарантовано вирівнюється за межею 64 байтів за допомогою системних викликів `posix_memalign` (у C) та специфікатора `alignas(64)` (у C++) для уникнення апаратного розщеплення кеш-ліній (*cache line split*).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#define CACHE_LINE_BYTES 64
#define BITS_PER_BLOCK   (CACHE_LINE_BYTES * 8) // 512 бітів
#define WORDS_PER_BLOCK  (CACHE_LINE_BYTES / sizeof(uint64_t)) // 8 слів по 64 біти

// Блок розміром рівно в одну кеш-лінію (64 байти)
typedef struct {
    uint64_t words[WORDS_PER_BLOCK];
} cache_block_t;

typedef struct {
    cache_block_t *blocks;
    size_t num_blocks;
    uint32_t k_hashes;
} blocked_bloom_t;

// 64-бітний швидкий некриптографічний геш MurmurHash3 / SplitMix64
static inline uint64_t hash_step(uint64_t x) {
    x ^= x >> 30;
    x *= 0xbf58476d1ce4e5b9ULL;
    x ^= x >> 27;
    x *= 0x94d049bb133111ebULL;
    x ^= x >> 31;
    return x;
}

// Ініціалізація блочного фільтра Блума
blocked_bloom_t* blocked_bloom_create(size_t num_elements, double fp_rate) {
    if (num_elements == 0 || fp_rate <= 0.0 || fp_rate >= 1.0) return NULL;

    // Розрахунок необхідної кількості бітів: m = -n * ln(p) / (ln(2))^2
    // Для блочного фільтра додаємо невеликий запас (+15%) на дисперсію завантаження блоків
    size_t total_bits = (size_t)(-1.65 * (double)num_elements * (fp_rate > 0.01 ? -4.6 : -6.9));
    size_t num_blocks = (total_bits + BITS_PER_BLOCK - 1) / BITS_PER_BLOCK;
    if (num_blocks == 0) num_blocks = 1;

    blocked_bloom_t *filter = (blocked_bloom_t*)malloc(sizeof(blocked_bloom_t));
    if (!filter) return NULL;

    // Виділення пам'яті з апаратним вирівнюванням по 64 байти
    void *raw_ptr = NULL;
    if (posix_memalign(&raw_ptr, CACHE_LINE_BYTES, num_blocks * sizeof(cache_block_t)) != 0) {
        free(filter);
        return NULL;
    }

    filter->blocks = (cache_block_t*)raw_ptr;
    filter->num_blocks = num_blocks;
    filter->k_hashes = 8; // Оптимально: 8 бітів на кеш-лінію 512 бітів
    memset(filter->blocks, 0, num_blocks * sizeof(cache_block_t));

    return filter;
}

// Додавання 64-бітного ключа
void blocked_bloom_add(blocked_bloom_t *filter, uint64_t key) {
    uint64_t h1 = hash_step(key);
    uint64_t h2 = hash_step(h1 ^ 0x517cc1b727220a95ULL);

    // 1. Вибір одного 64-байтового блоку (кеш-лінії)
    size_t block_idx = h1 % filter->num_blocks;
    cache_block_t *block = &filter->blocks[block_idx];

    // 2. Встановлення k бітів ВИКЛЮЧНО всередині цієї кеш-лінії
    for (uint32_t i = 0; i < filter->k_hashes; ++i) {
        uint32_t bit_idx = (uint32_t)((h1 + i * h2) & (BITS_PER_BLOCK - 1));
        uint32_t word_idx = bit_idx >> 6;          // bit_idx / 64
        uint64_t bit_mask = 1ULL << (bit_idx & 63); // bit_idx % 64
        block->words[word_idx] |= bit_mask;
    }
}

// Перевірка наявності 64-бітного ключа
bool blocked_bloom_contains(const blocked_bloom_t *filter, uint64_t key) {
    uint64_t h1 = hash_step(key);
    uint64_t h2 = hash_step(h1 ^ 0x517cc1b727220a95ULL);

    // 1. Вибір блоку: єдине звернення до пам'яті
    size_t block_idx = h1 % filter->num_blocks;
    const cache_block_t *block = &filter->blocks[block_idx];

    // 2. Локальна перевірка всіх k бітів у L1 кеші
    for (uint32_t i = 0; i < filter->k_hashes; ++i) {
        uint32_t bit_idx = (uint32_t)((h1 + i * h2) & (BITS_PER_BLOCK - 1));
        uint32_t word_idx = bit_idx >> 6;
        uint64_t bit_mask = 1ULL << (bit_idx & 63);

        if ((block->words[word_idx] & bit_mask) == 0) {
            return false; // Гарантований True Negative (100% відсутній)
        }
    }
    return true; // Possible Positive (можливе хибнопозитивне)
}

void blocked_bloom_destroy(blocked_bloom_t *filter) {
    if (filter) {
        free(filter->blocks);
        free(filter);
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <memory>
#include <bit>
#include <new>

// Блок, вирівняний по 64 байти (кеш-лінія)
struct alignas(64) CacheBlock {
    static constexpr size_t kWords = 8;
    static constexpr size_t kBits = kWords * 64; // 512 бітів
    uint64_t words[kWords]{0};
};

class BlockedBloomFilter {
public:
    explicit BlockedBloomFilter(size_t expected_elements, double fp_rate = 0.01)
        : k_hashes_(8) {
        // Розрахунок кількості блоків з урахуванням дисперсії
        const size_t total_bits = static_cast<size_t>(
            -1.65 * static_cast<double>(expected_elements) * (fp_rate > 0.01 ? -4.6 : -6.9)
        );
        num_blocks_ = (total_bits + CacheBlock::kBits - 1) / CacheBlock::kBits;
        if (num_blocks_ == 0) num_blocks_ = 1;

        // Виділення пам'яті з апаратним вирівнюванням
        blocks_ = std::make_unique_for_overwrite<CacheBlock[]>(num_blocks_);
        std::fill_n(blocks_.get(), num_blocks_, CacheBlock{});
    }

    void add(uint64_t key) noexcept {
        const auto [h1, h2] = compute_hashes(key);
        CacheBlock& block = blocks_[h1 % num_blocks_];

        for (uint32_t i = 0; i < k_hashes_; ++i) {
            const uint32_t bit_idx = (h1 + i * h2) & (CacheBlock::kBits - 1);
            const uint32_t word_idx = bit_idx >> 6;
            const uint64_t bit_mask = 1ULL << (bit_idx & 63);
            block.words[word_idx] |= bit_mask;
        }
    }

    [[nodiscard]] bool contains(uint64_t key) const noexcept {
        const auto [h1, h2] = compute_hashes(key);
        const CacheBlock& block = blocks_[h1 % num_blocks_];

        for (uint32_t i = 0; i < k_hashes_; ++i) {
            const uint32_t bit_idx = (h1 + i * h2) & (CacheBlock::kBits - 1);
            const uint32_t word_idx = bit_idx >> 6;
            const uint64_t bit_mask = 1ULL << (bit_idx & 63);

            if ((block.words[word_idx] & bit_mask) == 0) {
                return false; // 100% відсутній
            }
        }
        return true; // Ймовірно присутній
    }

    [[nodiscard]] size_t memory_bytes() const noexcept {
        return num_blocks_ * sizeof(CacheBlock);
    }

private:
    struct HashPair { uint64_t h1; uint64_t h2; };

    static constexpr HashPair compute_hashes(uint64_t key) noexcept {
        // Швидкий геш SplitMix64
        auto splitmix = [](uint64_t x) constexpr -> uint64_t {
            x ^= x >> 30;
            x *= 0xbf58476d1ce4e5b9ULL;
            x ^= x >> 27;
            x *= 0x94d049bb133111ebULL;
            x ^= x >> 31;
            return x;
        };
        uint64_t h1 = splitmix(key);
        uint64_t h2 = splitmix(h1 ^ 0x517cc1b727220a95ULL);
        return {h1, h2};
    }

    size_t num_blocks_{0};
    uint32_t k_hashes_{8};
    std::unique_ptr<CacheBlock[]> blocks_;
};
```
:::

---

### Покроковий розбір коду та бітових операцій

1. **Інкапсуляція кеш-лінії у структуру `CacheBlock`:** структура складається з масиву восьми 64-розрядних слів `uint64_t words[8]`. Загальний обсяг становить `8 · 8 = 64` байти, що дорівнює 512 бітам. Специфікатор `alignas(64)` змушує компілятор розміщувати кожен блок за адресою, кратною 64, що виключає перетинання межі кеш-ліній при зчитуванні.
2. **Адресація бітів усередині 512-бітового блоку:** обчислений бітовий індекс `bit_idx` затискається в межах `0..511` за допомогою швидкої побітової маски `& (512 - 1)` (еквівалент операції за модулем 512).
   - Номер 64-розрядного слова `word_idx` обчислюється зсувом управо: `bit_idx >> 6` (ділення на 64).
   - Позиція біта всередині слова визначається маскою `1ULL << (bit_idx & 63)` (залишок від ділення на 64).
3. **Раннє відхилення (Early Termination):** у циклі перевірки `contains()` перевірка кожного біта виконується по черзі. Щойно виявлено слово, в якому `block->words[word_idx] & bit_mask == 0`, функція миттєво повертає `false` без обчислення решти гешів.

---

### Тонкощі, пастки та оптимізація швидкодії

1. **Компенсація дисперсії завантаження блоків:** у класичному фільтрі кожен біт заповнюється з абсолютно однаковою ймовірністю. У блочному фільтрі ключі потрапляють у блоки за біноміальним розподілом (аналог задачі про розміщення куль у кошиках). Через випадкову дисперсію деякі блоки отримають трохи більше ключів, ніж у середньому, а інші — трохи менше. Переповнені блоки матимуть вищу ймовірність хибного спрацьовування. Щоб результуючий рівень помилок відповідав цільовому значенню `p`, розмір блочного фільтра збільшують на 10–15% у порівнянні з класичною формулою Блума.
2. **Швидке відображення діапазону замість повільного ділення:** операція залишку від ділення `h1 % num_blocks` компілюється в апаратну команду `DIV` / `IDIV`, яка на процесорах x86-64 виконується від 15 до 30 тактів. Якщо `num_blocks` є степенем двійки, її замінюють на `& (num_blocks - 1)`. Якщо ж фільтр має довільну кількість блоків, застосовують метод *fastrange* (множення без ділення):

:::tabs
```c
// Бездільне відображення за 1 такт CPU у C
size_t block_idx = (size_t)(((unsigned __int128)h1 * num_blocks) >> 64);
```
```cpp
// Бездільне відображення у C++ з використанням 128-бітного типу
auto block_idx = static_cast<size_t>((static_cast<unsigned __int128>(h1) * num_blocks) >> 64);
```
:::

3. **SIMD-векторизація через AVX2:** у системних базах даних (наприклад, у рушії виконання SQL-запитів Apache Impala та колоночних сховищах ClickHouse) 512-бітовий блок перевіряється двома 256-бітними регістрами `__m256i`. Сформована бітова маска перевіряється векторною командою `_mm256_testc_si256`, що виконує повну перевірку всіх `k` бітів за 2 процесорні такти без жодного розгалуження в машинному коді.
4. **Вирівнювання пам'яті в багатопотокових системах:** якщо масив блоків не вирівняно за межею 64 байтів, один блок може перетинати межу двох фізичних кеш-ліній (наприклад, 24 байти в першій лінії та 40 байтів у другій). У такому разі одне звернення до блоку призведе до завантаження двох ліній кешу замість однієї, що вдвічі знижує пропускну здатність шини пам'яті та створює ризик помилкового розділення пам'яті (*false sharing*) між сусідніми ядрами.
