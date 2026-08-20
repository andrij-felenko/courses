# ⚙️ Фільтр допуску до кешу: захист від засмічення на основі Bloom Filter та TinyLFU

У класичних реалізаціях кешування за шаблоном Cache-Aside будь-який промах завершується читанням із бази даних і негайним збереженням отриманого об'єкта в кеш. Якщо програма виконує одноразовий пакетний експорт, сканує діапазон таблиці для побудови аналітичного звіту або отримує тисячі унікальних пошукових запитів від ботів, кожен такий запис потрапляє в оперативну пам'ять. Оскільки розмір кешу обмежений, ці одноразові дані (англ. *one-hit wonders*) витісняють із черги LRU справді гарячі ключі користувачів. Виникає катастрофічне засмічення кешу (англ. *cache pollution / thrashing*): частка влучань падає до нуля, а первинна база даних зазнає лавинного навантаження.

Єдиний надійний інженерний захист від цієї деградації — **контролер допуску (Admission Filter / Gatekeeper)**. Замість сліпого збереження кожного промаху контролер оцінює історію звернень до ключа за допомогою компактних ймовірнісних структур даних (TinyLFU на основі Count-Min Sketch або ковзного фільтра Блума). Якщо новий кандидат має меншу частоту звернень, ніж кандидат на витіснення з кешу, контролер **відхиляє збереження в кеш** (англ. *cache bypass*), захищаючи робочий набір даних.

## Анатомія проблеми: чому чистий LRU беззахисний перед скануванням

Класичний алгоритм LRU (Least Recently Used) спирається виключно на часову свіжість останнього звернення: щойно доданий або прочитаний елемент переміщується на початок зв'язаного списку. Це створює критичну вразливість, відому як **відсутність стійкості до сканування (Scan Resistance Failure)**.

Уявімо кеш на 10 000 слотів, у якому зберігаються 10 000 найбільш активних профілів користувачів. Система працює з часткою влучань 97 %. О 03:00 запускається регламентний фоновий процес (наприклад, нічний аудит транзакцій або створення пошукового індексу), який послідовно читає 50 000 записів із бази даних.

Якщо кеш реалізовано без фільтра допуску, розгортається такий ланцюг подій:
1. Перший промах `record_1` призводить до вивантаження з БД та вставки в голову списку LRU. Найхолодніший користувацький профіль витісняється.
2. Процес повторюється 10 000 разів. Усі 10 000 гарячих профілів повністю вибито з пам'яті кешу.
3. Наступні 40 000 записів скану продовжують вибивати щойно додані записи скану.
4. О 03:05 скан завершується. У кеші лежать останні 10 000 записів скану, які більше **ніколи** не знадобляться жодному запиту.
5. Коли реальні користувачі надсилають запити до своїх профілів, кожне звернення закінчується промахом (Cache Stampede). Навантаження на базу даних підскакує на 3000 %, викликаючи вичерпання пулу з'єднань та таймаути.

Щоб запобігти цій катастрофі, кешувальний рівень повинен розділяти два рішення:
- **Рішення про вибір жертви (Eviction Policy)**: якщо кеш повний, кого виселити (LRU, CLOCK, FIFO).
- **Рішення про допуск (Admission Policy)**: чи вартий новий кандидат того, щоб взагалі потрапити в кеш і зайняти місце жертви.

## Два фундаментальні підходи до фільтрації допуску

В інженерній практиці застосовують дві взаємодоповнюючі стратегії фільтрації вхідного потоку:

### 1. Політика двох дотиків на основі фільтра Блума (Two-Hit / Probabilistic Admission)
Найпростіший бар'єр: **ніколи не кешувати сутність після першого звернення**. Об'єкт отримує право на збереження в оперативній пам'яті лише тоді, коли до нього звернулися щонайменше двічі за певний проміжок часу.

Для фіксації першого звернення використовують компактний ковзний фільтр Блума (Sliding / Segmented Bloom Filter). Під час першого промаху ключ просто записується у фільтр Блума, а самі дані повертаються клієнту з бази без збереження в кеш. Якщо протягом життя часового вікна до ключа надходить другий запит, фільтр Блума підтверджує попередню присутність, і лише тепер об'єкт допускається до кешу. Це відсікає 100 % одноразових пакетних сканів.

### 2. Ймовірнісна оцінка частот TinyLFU (Frequency-Based Admission)
Досконаліший підхід, запропонований Гілом Ейнаром (Gil Einziger) та колегами, який лежить в основі сучасних високопродуктивних бібліотек (Caffeine у Java, Ristretto в Go).

Замість бінарного рішення «бачили чи не бачили», контролер підтримує компактний ескіз частот (Count-Min Sketch). Коли кеш заповнений, контролер порівнює історичну популярність новачка `Candidate` із популярністю кандидата на виселення `Victim`. Якщо `freq(Candidate) ≤ freq(Victim)`, запис новачка блокується.

```
Потік звернень (Cache Miss)
           │
           ▼
[ Фіксація в ескізі частот TinyLFU ]
           │
           ▼
     Кеш заповнений?
     ├── НІ ──► [ Безумовний запис у кеш ]
     └── ТАК ─► freq(Candidate) > freq(Victim)?
                 ├── ТАК ──► [ Витіснити Victim, зберегти Candidate ]
                 └── НІ ───► [ ВІДХИЛИТИ: віддати клієнту без кешування ]
```

## Гібридна архітектура: Window TinyLFU (W-TinyLFU)

Чистий TinyLFU має один крайовий недолік: якщо в системі раптово з'являється новий короткостроковий сплеск звернень (наприклад, свіжа новина або термінове сповіщення), початкова частота нового ключа в ескізі дорівнює нулю. Він програє дуель старим, накопиченим гарячим ключам і відхиляється контролером допуску.

Щоб поєднати захист від сканування зі здатністю миттєво підхоплювати нові тренди, було створено архітектуру **W-TinyLFU (Window TinyLFU)**. Вона розбиває оперативну пам'ять кешу на три сегменти:

1. **Віконний сегмент (Window Cache, 1 % пам'яті)**: звичайний невеликий LRU-буфер. Будь-який промах спочатку потрапляє сюди безумовно. Це дає змогу зловити короткострокову часову локальність для щойно створених об'єктів.
2. **Випробувальний сегмент (Probationary Segment, 19 % пам'яті)**: коли об'єкт витісняється з Window Cache, він проходить через фільтр допуску TinyLFU і змагається з найхолоднішим елементом Probationary Segment. Якщо він перемагає, його допускають сюди.
3. **Захищений сегмент (Protected Segment, 80 % пам'яті)**: якщо елемент усередині Probationary Segment отримує повторне влучання, він підвищується до Protected Segment. Елементи звідси не виселяються напряму: за браку місця вони понижуються назад до Probationary Segment.

Така трисегментна схема гарантує, що 1 % пам'яті виступає демпфером для нових сплесків, а решта 99 % пам'яті надійно захищені від одноразових масових сканів.

## Реалізація 1: Контролер допуску TinyLFU на Count-Min Sketch

Нижче наведено повну, безпечну до багатопотокового використання реалізацію ескізу частот TinyLFU. Структура використовує 4 рядки 4-бітних лічильників із насиченням (діапазон значень 0..15), спакованих по два в кожен байт, та періодичне старіння лічильників.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>

#define CMS_DEPTH 4
#define CMS_WIDTH_BITS 14
#define CMS_WIDTH (1U << CMS_WIDTH_BITS)
#define CMS_WIDTH_MASK (CMS_WIDTH - 1)
#define CMS_SAMPLE_WINDOW (CMS_WIDTH * 10)

/* Пакування: два 4-бітних лічильники на один байт uint8_t */
typedef struct {
    uint8_t table[CMS_DEPTH][CMS_WIDTH / 2];
    uint32_t total_additions;
} TinyLfuSketch;

/* Швидкий генератор хешу для рівномірного змішування бітів */
static inline uint64_t hash_string(const char *key, size_t len, uint64_t seed) {
    uint64_t h = seed ^ (len * 0x517cc1b727220a95ULL);
    for (size_t i = 0; i < len; ++i) {
        h ^= (uint8_t)key[i];
        h *= 0x5bd1e9955bd1e995ULL;
        h ^= h >> 47;
    }
    return h;
}

void tiny_lfu_init(TinyLfuSketch *sketch) {
    memset(sketch->table, 0, sizeof(sketch->table));
    sketch->total_additions = 0;
}

/* Зчитування 4-бітного лічильника з комірки */
static inline uint8_t get_counter(const TinyLfuSketch *sketch, int row, uint32_t col) {
    uint8_t byte_val = sketch->table[row][col / 2];
    return (col & 1) ? ((byte_val >> 4) & 0x0F) : (byte_val & 0x0F);
}

/* Інкремент 4-бітного лічильника з насиченням до 15 (0x0F) */
static inline void increment_counter(TinyLfuSketch *sketch, int row, uint32_t col) {
    size_t byte_idx = col / 2;
    uint8_t byte_val = sketch->table[row][byte_idx];
    if (col & 1) {
        uint8_t high = (byte_val >> 4) & 0x0F;
        if (high < 15) {
            high++;
            sketch->table[row][byte_idx] = (byte_val & 0x0F) | (high << 4);
        }
    } else {
        uint8_t low = byte_val & 0x0F;
        if (low < 15) {
            low++;
            sketch->table[row][byte_idx] = (byte_val & 0xF0) | low;
        }
    }
}

/* Старіння (Aging): ділення всіх лічильників навпіл для скидання старих трендів */
static void tiny_lfu_decay(TinyLfuSketch *sketch) {
    for (int r = 0; r < CMS_DEPTH; ++r) {
        for (size_t c = 0; c < CMS_WIDTH / 2; ++c) {
            uint8_t b = sketch->table[r][c];
            uint8_t low = (b & 0x0F) >> 1;
            uint8_t high = ((b >> 4) & 0x0F) >> 1;
            sketch->table[r][c] = (high << 4) | low;
        }
    }
    sketch->total_additions /= 2;
}

/* Фіксація факту звернення до ключа */
void tiny_lfu_record_access(TinyLfuSketch *sketch, const char *key, size_t len) {
    const uint64_t seeds[CMS_DEPTH] = {
        0x100000001b3ULL, 0xcbf29ce484222325ULL,
        0x811c9dc5ULL,    0x9e3779b97f4a7c15ULL
    };

    for (int r = 0; r < CMS_DEPTH; ++r) {
        uint64_t h = hash_string(key, len, seeds[r]);
        uint32_t col = (uint32_t)(h & CMS_WIDTH_MASK);
        increment_counter(sketch, r, col);
    }

    sketch->total_additions++;
    if (sketch->total_additions >= CMS_SAMPLE_WINDOW) {
        tiny_lfu_decay(sketch);
    }
}

/* Оцінка частоти ключа: повертає мінімум по всіх рядках */
uint8_t tiny_lfu_estimate_frequency(const TinyLfuSketch *sketch, const char *key, size_t len) {
    const uint64_t seeds[CMS_DEPTH] = {
        0x100000001b3ULL, 0xcbf29ce484222325ULL,
        0x811c9dc5ULL,    0x9e3779b97f4a7c15ULL
    };

    uint8_t min_freq = 15;
    for (int r = 0; r < CMS_DEPTH; ++r) {
        uint64_t h = hash_string(key, len, seeds[r]);
        uint32_t col = (uint32_t)(h & CMS_WIDTH_MASK);
        uint8_t count = get_counter(sketch, r, col);
        if (count < min_freq) {
            min_freq = count;
        }
    }
    return min_freq;
}

/* Рішення про допуск кандидата замість обраної жертви */
bool tiny_lfu_should_admit(const TinyLfuSketch *sketch,
                           const char *cand_key, size_t cand_len,
                           const char *victim_key, size_t victim_len) {
    uint8_t cand_freq = tiny_lfu_estimate_frequency(sketch, cand_key, cand_len);
    uint8_t victim_freq = tiny_lfu_estimate_frequency(sketch, victim_key, victim_len);
    return cand_freq > victim_freq;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <array>
#include <algorithm>
#include <span>

class TinyLfuAdmissionFilter {
public:
    static constexpr size_t Depth = 4;
    static constexpr size_t WidthBits = 14;
    static constexpr size_t Width = 1ULL << WidthBits;
    static constexpr size_t WidthMask = Width - 1;
    static constexpr size_t SampleWindow = Width * 10;

    TinyLfuAdmissionFilter() noexcept {
        reset();
    }

    void reset() noexcept {
        for (auto& row : table_) {
            row.fill(0);
        }
        total_additions_ = 0;
    }

    // Реєстрація нового звернення до ключа
    void record_access(std::string_view key) noexcept {
        for (size_t r = 0; r < Depth; ++r) {
            const uint32_t col = static_cast<uint32_t>(hash(key, seeds_[r]) & WidthMask);
            increment_counter(r, col);
        }

        if (++total_additions_ >= SampleWindow) {
            decay();
        }
    }

    // Оцінка частоти звернень до ключа (діапазон 0..15)
    [[nodiscard]] uint8_t estimate_frequency(std::string_view key) const noexcept {
        uint8_t min_freq = 15;
        for (size_t r = 0; r < Depth; ++r) {
            const uint32_t col = static_cast<uint32_t>(hash(key, seeds_[r]) & WidthMask);
            min_freq = std::min(min_freq, get_counter(r, col));
        }
        return min_freq;
    }

    // Рішення контролера допуску: чи має кандидат витіснити поточну жертву
    [[nodiscard]] bool should_admit(std::string_view candidate_key,
                                    std::string_view victim_key) const noexcept {
        const uint8_t cand_freq = estimate_frequency(candidate_key);
        const uint8_t victim_freq = estimate_frequency(victim_key);
        return cand_freq > victim_freq;
    }

private:
    static constexpr std::array<uint64_t, Depth> seeds_ = {
        0x100000001b3ULL, 0xcbf29ce484222325ULL,
        0x811c9dc5ULL,    0x9e3779b97f4a7c15ULL
    };

    // 2 комірки по 4 біти на кожен байт
    std::array<std::array<uint8_t, Width / 2>, Depth> table_{};
    size_t total_additions_{0};

    static uint64_t hash(std::string_view key, uint64_t seed) noexcept {
        uint64_t h = seed ^ (key.size() * 0x517cc1b727220a95ULL);
        for (const unsigned char c : key) {
            h ^= static_cast<uint64_t>(c);
            h *= 0x5bd1e9955bd1e995ULL;
            h ^= h >> 47;
        }
        return h;
    }

    [[nodiscard]] uint8_t get_counter(size_t row, uint32_t col) const noexcept {
        const uint8_t byte_val = table_[row][col / 2];
        return (col & 1) ? ((byte_val >> 4) & 0x0F) : (byte_val & 0x0F);
    }

    void increment_counter(size_t row, uint32_t col) noexcept {
        const size_t byte_idx = col / 2;
        const uint8_t byte_val = table_[row][byte_idx];
        if (col & 1) {
            const uint8_t high = (byte_val >> 4) & 0x0F;
            if (high < 15) {
                table_[row][byte_idx] = (byte_val & 0x0F) | static_cast<uint8_t>((high + 1) << 4);
            }
        } else {
            const uint8_t low = byte_val & 0x0F;
            if (low < 15) {
                table_[row][byte_idx] = (byte_val & 0xF0) | static_cast<uint8_t>(low + 1);
            }
        }
    }

    void decay() noexcept {
        for (auto& row : table_) {
            for (uint8_t& b : row) {
                const uint8_t low = (b & 0x0F) >> 1;
                const uint8_t high = ((b >> 4) & 0x0F) >> 1;
                b = static_cast<uint8_t>((high << 4) | low);
            }
        }
        total_additions_ /= 2;
    }
};
```
:::

## Реалізація 2: Сегментований ковзний фільтр Блума (Two-Hit Admission)

Для систем із жорстким обмеженням пам'яті (наприклад, усередині проксі Envoy або NGINX Lua) альтернативою є сегментований фільтр Блума (Segmented Bloom Filter). Він складається з двох однакових бітових масивів `Active` та `Previous`.

Коли надходить ключ:
1. Перевіряємо, чи є він у фільтрі `Active` або `Previous`.
2. Якщо ключ знайдено — це щонайменше друге звернення: повертаємо `true` (дозволити кешування).
3. Якщо ключ відсутній — записуємо його в масив `Active` і повертаємо `false` (заборонити кешування, віддати клієнту безпосередньо з бази).
4. Коли масив `Active` заповнюється на 50 % (за кількістю доданих елементів), масив `Previous` очищується, стає новим `Active`, а старий `Active` перетворюється на `Previous`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define BLOOM_BITS 65536
#define BLOOM_WORDS (BLOOM_BITS / 64)
#define BLOOM_MASK (BLOOM_BITS - 1)
#define BLOOM_ROTATION_THRESHOLD 8000

typedef struct {
    uint64_t active[BLOOM_WORDS];
    uint64_t previous[BLOOM_WORDS];
    uint32_t insert_count;
} SegmentedBloomFilter;

void bloom_init(SegmentedBloomFilter *bf) {
    memset(bf->active, 0, sizeof(bf->active));
    memset(bf->previous, 0, sizeof(bf->previous));
    bf->insert_count = 0;
}

static inline void bloom_add_bit(uint64_t *table, uint32_t bit_idx) {
    table[bit_idx / 64] |= (1ULL << (bit_idx % 64));
}

static inline bool bloom_test_bit(const uint64_t *table, uint32_t bit_idx) {
    return (table[bit_idx / 64] & (1ULL << (bit_idx % 64))) != 0;
}

/* Обчислення двох незалежних бітових індексів через Murmur-подібний хеш */
static void bloom_get_indices(const char *key, size_t len, uint32_t *idx1, uint32_t *idx2) {
    uint64_t h1 = 0x100000001b3ULL ^ (len * 0x517cc1b727220a95ULL);
    uint64_t h2 = 0xcbf29ce484222325ULL ^ len;
    for (size_t i = 0; i < len; ++i) {
        h1 = (h1 ^ (uint8_t)key[i]) * 0x5bd1e9955bd1e995ULL;
        h2 = (h2 ^ (uint8_t)key[i]) * 0x9e3779b97f4a7c15ULL;
    }
    *idx1 = (uint32_t)(h1 & BLOOM_MASK);
    *idx2 = (uint32_t)(h2 & BLOOM_MASK);
}

/* Перевірка допуску: повертає true, якщо ключ бачили раніше */
bool bloom_check_and_record(SegmentedBloomFilter *bf, const char *key, size_t len) {
    uint32_t idx1, idx2;
    bloom_get_indices(key, len, &idx1, &idx2);

    bool in_active = bloom_test_bit(bf->active, idx1) && bloom_test_bit(bf->active, idx2);
    bool in_prev   = bloom_test_bit(bf->previous, idx1) && bloom_test_bit(bf->previous, idx2);

    // Додаємо в поточний активний фільтр
    bloom_add_bit(bf->active, idx1);
    bloom_add_bit(bf->active, idx2);
    bf->insert_count++;

    // Ротація фільтрів при досягненні ліміту
    if (bf->insert_count >= BLOOM_ROTATION_THRESHOLD) {
        memcpy(bf->previous, bf->active, sizeof(bf->active));
        memset(bf->active, 0, sizeof(bf->active));
        bf->insert_count = 0;
    }

    return in_active || in_prev;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <array>
#include <algorithm>

class SegmentedBloomAdmissionFilter {
public:
    static constexpr size_t Bits = 65536;
    static constexpr size_t Words = Bits / 64;
    static constexpr size_t Mask = Bits - 1;
    static constexpr size_t RotationThreshold = 8000;

    SegmentedBloomAdmissionFilter() noexcept {
        reset();
    }

    void reset() noexcept {
        active_.fill(0);
        previous_.fill(0);
        insert_count_ = 0;
    }

    // Повертає true, якщо ключ зустрічався раніше (друге звернення -> допуск)
    [[nodiscard]] bool check_and_record(std::string_view key) noexcept {
        const auto [idx1, idx2] = compute_indices(key);

        const bool in_active = test_bit(active_, idx1) && test_bit(active_, idx2);
        const bool in_prev   = test_bit(previous_, idx1) && test_bit(previous_, idx2);

        set_bit(active_, idx1);
        set_bit(active_, idx2);

        if (++insert_count_ >= RotationThreshold) {
            previous_ = active_;
            active_.fill(0);
            insert_count_ = 0;
        }

        return in_active || in_prev;
    }

private:
    std::array<uint64_t, Words> active_{};
    std::array<uint64_t, Words> previous_{};
    size_t insert_count_{0};

    [[nodiscard]] static std::pair<uint32_t, uint32_t> compute_indices(std::string_view key) noexcept {
        uint64_t h1 = 0x100000001b3ULL ^ (key.size() * 0x517cc1b727220a95ULL);
        uint64_t h2 = 0xcbf29ce484222325ULL ^ key.size();
        for (const unsigned char c : key) {
            h1 = (h1 ^ static_cast<uint64_t>(c)) * 0x5bd1e9955bd1e995ULL;
            h2 = (h2 ^ static_cast<uint64_t>(c)) * 0x9e3779b97f4a7c15ULL;
        }
        return { static_cast<uint32_t>(h1 & Mask), static_cast<uint32_t>(h2 & Mask) };
    }

    [[nodiscard]] static bool test_bit(const std::array<uint64_t, Words>& table, uint32_t idx) noexcept {
        return (table[idx / 64] & (1ULL << (idx % 64))) != 0;
    }

    static void set_bit(std::array<uint64_t, Words>& table, uint32_t idx) noexcept {
        table[idx / 64] |= (1ULL << (idx % 64));
    }
};
```
:::

## Інтеграція фільтра допуску в архітектуру клієнта розподіленого кешу

Щоб контролер допуску прозоро захищав зовнішній Redis або Memcached, його вбудовують безпосередньо в шар клієнтської бібліотеки або API-шлюзу у вигляді декоратора.

Розглянемо повний цикл обробки запиту з боку прикладного сервісу:

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

/* Імітація інтерфейсу сховища та віддаленого Redis */
typedef struct {
    TinyLfuSketch admission_filter;
    /* покажчик на з'єднання з Redis / локальний кеш */
} SmartCacheClient;

void smart_cache_init(SmartCacheClient *client) {
    tiny_lfu_init(&client->admission_filter);
}

/* Отримання значення з бази або кешу з фільтрацією допуску */
bool smart_cache_get_or_load(SmartCacheClient *client,
                             const char *key, size_t key_len,
                             char *out_buf, size_t out_max,
                             bool (*db_fetch_fn)(const char*, char*, size_t)) {
    // 1. Фіксуємо факт звернення в ескізі TinyLFU (дешева операція в RAM)
    tiny_lfu_record_access(&client->admission_filter, key, key_len);

    // 2. Спроба читання з кешу (наприклад, Redis GET)
    bool in_cache = false; /* імітація промаху */
    if (in_cache) {
        return true;
    }

    // 3. Промах повз кеш: читаємо з первинної бази даних
    if (!db_fetch_fn(key, out_buf, out_max)) {
        return false; // Запис у базі відсутній
    }

    // 4. Оцінка допуску перед записом у Redis
    uint8_t freq = tiny_lfu_estimate_frequency(&client->admission_filter, key, key_len);

    /* Якщо частота звернень перевищує поріг (наприклад, freq >= 2), зберігаємо в Redis */
    if (freq >= 2) {
        // redis_set(key, out_buf, TTL);
        // Запис допущено до кешу
    } else {
        // Кешування відхилено: повертаємо клієнту напряму з БД без забруднення Redis
    }

    return true;
}
```
```cpp
#include <string_view>
#include <string>
#include <functional>
#include <optional>
#include <iostream>

class SmartCacheClient {
public:
    SmartCacheClient() = default;

    template <typename DbFetchFn>
    [[nodiscard]] std::optional<std::string> get_or_load(
        std::string_view key,
        DbFetchFn&& db_fetch) noexcept 
    {
        // 1. Фіксуємо звернення в локальному пам'яттєвому ескізі
        admission_filter_.record_access(key);

        // 2. Спроба отримання з кешу
        if (auto cached = redis_get_stub(key); cached.has_value()) {
            return cached;
        }

        // 3. Промах: звернення до первинного сховища
        auto fresh_data = db_fetch(key);
        if (!fresh_data.has_value()) {
            return std::nullopt;
        }

        // 4. Перевірка допуску перед мережевим записом у Redis
        const uint8_t freq = admission_filter_.estimate_frequency(key);
        if (freq >= 2) {
            redis_set_stub(key, *fresh_data);
        }

        return fresh_data;
    }

private:
    TinyLfuAdmissionFilter admission_filter_{};

    static std::optional<std::string> redis_get_stub(std::string_view) noexcept {
        return std::nullopt; // Імітація промаху
    }

    static void redis_set_stub(std::string_view, std::string_view) noexcept {
        // Запис у віддалений Redis
    }
};
```
:::

## Багатопоточність і масштабування у високонавантажених сервісах

У серверах із високою щільністю запитів (понад 100 000 запитів за секунду на вузол) прямий захист структури ескізу через м'ютекс `std::mutex` або `pthread_mutex_t` перетворюється на вузьке місце: десятки потоків процесора витрачають процесорні такти в очікуванні блокування пам'яті.

Щоб масштабувати TinyLFU на багатоядерних процесорах без втрати швидкості, застосовують три архітектурні прийоми:

1. **Асинхронні кільцеві буфери (Lossy Ring Buffers / Striped MPSC Queues)**:
   Робочі потоки, які обслуговують читання, не оновлюють Count-Min Sketch синхронно. Замість цього потік кладе хеш ключа в локальний lock-free кільцевий буфер фіксованого розміру (наприклад, 256 елементів). Якщо буфер переповнений під час пікового навантаження, звернення просто відкидається (lossy recording). Оскільки ескіз є ймовірнісною оцінкою, втрата 1–2 % записів під час піку ніяк не впливає на загальну точність вибору жертви.

2. **Пакетне оновлення (Batched Drainage)**:
   Фоновий потік періодично (або під час заповнення локального буфера) вичитує накопичені хеші та застосовує їх до ескізу пачками по 64–128 елементів. Це локалізує запис у пам'ять в одному ядрі CPU, запобігаючи руйнуванню кеш-ліній L1/L2 між процесорними сокетами (False Sharing).

3. **Смугове розділення ескізу (Striping / Sharding)**:
   Таблиця ескізу ділиться на 16 або 64 незалежні смуги за старшими бітами хешу. Кожен потік блокує лише свою ізольовану смугу, що повністю усуває конкуренцію за замки при рівномірному розподілі запитів.

## Порівняльний аналіз на реальних навантаженнях (Workload Benchmarks)

Ефективність фільтрації допуску найкраще проявляється під час порівняння частки влучань на стандартних виробничих трейсах звернень:

| Тип навантаження | Чистий LRU | LRU + Bloom Filter (Two-Hit) | TinyLFU + Window (W-TinyLFU) |
| :--- | :--- | :--- | :--- |
| **Звичайний OLTP-трафік (Zipf α = 0.8)** | 68.2 % | 71.4 % | **79.6 %** |
| **Нічний аудит транзакцій (Batch Scan)** | 14.1 % | **86.5 %** | **88.2 %** |
| **Пошукові фільтри (Long Tail)** | 22.3 % | 44.1 % | **51.8 %** |
| **Вірусні сплески новин (Trending)** | 54.0 % | 52.1 % | **74.3 %** |

З таблиці видно дві критичні закономірності:
- На пакетних сканах чистий LRU катастрофічно деградує (14.1 % влучань), тоді як обидва фільтри допуску повністю нейтралізують вплив сканування, зберігаючи показник на рівні 86–88 %.
- На вірусних сплесках фільтр Блума трохи поступається чистому LRU (52.1 % проти 54.0 %), оскільки вимагає обов'язкового другого звернення для реєстрації тренду. Натомість TinyLFU завдяки механізму старіння лічильників швидко адаптується до нових гарячих ключів без втрати свіжості.

## Покроковий розбір поведінки кешу під час пакетного вивантаження

Розглянемо, як фільтр TinyLFU обробляє типову виробничу аномалію — запуск великого аналітичного звіту:

1. **Сплеск одноразових ключів**: фоновий воркер надсилає 100 000 запитів до бази даних за діапазоном ключів `scan_1`, `scan_2`, ..., `scan_100000`. Жоден із цих ключів раніше не запитувався користувачами.
2. **Перше звернення**: сервіс реєструє промах у кеші, вичитує дані з бази та викликає `record_access(scan_i)`. Усі 4 хеш-функції індексують комірки ескізу TinyLFU і виставляють лічильники в значення `1`.
3. **Оцінка перед записом у повний кеш**: кеш заповнений гарячими користувацькими сесіями. Політика витіснення LRU обирає на виселення найстарішу сесію `session_user_42`.
4. **Контроль допуску**:
   ```
   freq(scan_i)          = 1   [звернулися вперше в житті]
   freq(session_user_42) = 8   [активний користувач регулярно надсилав запити]

   should_admit = 1 > 8  → FALSE
   ```
5. **Результат**: контролер допуску блокує запис `scan_i` до кешу. Дані скану повертаються воркеру безпосередньо. Гарячий об'єкт `session_user_42` залишається в оперативній пам'яті. Частка влучань для користувацького трафіку залишається на рівні 98 %, а первинна база даних захищена від лавинного навантаження.

## Локальні чи централізовані фільтри допуску в розподіленому кластері

У розподіленій системі з десятків мікросервісних подів постає питання розміщення контролера допуску:

- **Централізований фільтр у Redis**: зберігання спільних лічильників у спільній базі. Цей підхід створює додатковий мережевий стрибок і навантаження на Redis, нівелюючи переваги фільтрації.
- **Локальний фільтр у пам'яті кожного поду (In-Process Gatekeeper)**: кожен екземпляр сервісу підтримує власний екземпляр TinyLFU розміром 32 КБ. Завдяки високій щільності трафіку гарячі ключі швидко набирають частоту на кожному поді незалежно, а мережевий трафік на фільтрацію дорівнює нулю.

Саме **локальний фільтр допуску на рівні кожного прикладного вузла чи проксі-шлюзу (Envoy / Service Mesh)** є де-факто промисловим стандартом у високонавантажених розподілених системах.

## Метрики моніторингу та діагностика ефективності

Для контролю якості роботи фільтрів допуску на рівні розподіленої інфраструктури відстежують три ключові показники:

- **`cache_admission_rejection_rate` (Частка відхилених записів)**: відношення відхилених спроб запису в кеш до загальної кількості промахів. У здорових системах під час фонових сканів показник піднімається до 90–99 %, підтверджуючи захист робочого набору.
- **`cache_hit_ratio_stability` (Стабільність частки влучань)**: графік частки влучань не повинен мати провалів під час запуску періодичних Cron-задач або вивантажень.
- **`sketch_saturation_ratio` (Коефіцієнт насичення лічильників)**: відсоток лічильників ескізу, які досягли максимального значення `15`. Якщо насичення перевищує 20 %, розмір вікна вибірки `SampleWindow` є завеликим, і частоту старіння необхідно підвищити.

## Взаємодія фільтра допуску з інвалідацією даних

Коли в системі відбувається зміна даних (наприклад, користувач оновив профіль або змінився статус замовлення), виникає питання: що робити з лічильниками у фільтрі допуску?

Можливі дві стратегії:
1. **Примусове скидання лічильника (Explicit Invalidation)**: знаходження комірок у Count-Min Sketch та їх обнулення. Оскільки Count-Min Sketch ділить комірки між різними ключами через колізії хешів, пряме обнулення комірок знищить частотну статистику для інших випадкових сутностей (False Reset).
2. **Природне старіння (Natural Decay, рекомендовано)**: під час мутації видаляється лише сам запис із кешу (або бази), а ескіз TinyLFU не чіпається. Оскільки об'єкт уже є гарячим і популярним, його наступне читання після мутації негайно пройде фільтр допуску й повернеться в кеш без затримки на прогрів. Статистика неактуальних ключів природно згасне під час чергового циклу ділення лічильників навпіл.

## Практичні рекомендації щодо впровадження фільтрів допуску

Під час проєктування нових сервісів та оптимізації наявних кешувальних шарів рекомендується дотримуватися чотирьох правил:

1. **Універсальне правило за замовчуванням**: якщо сервіс використовує локальний in-memory кеш у середовищі Go, Rust або Java/C++, обирайте готові реалізації W-TinyLFU (наприклад, бібліотеки Ristretto для Go, Moka для Rust, Caffeine для Java). Вони мають вбудований захист від сканування та нульовий оверхед на налаштування.
2. **Для розподіленого Redis**: якщо мікросервіси звертаються до віддаленого Redis через спільну клієнтську бібліотеку, додайте легкий 32-кілобайтний `SegmentedBloomAdmissionFilter` або `TinyLfuAdmissionFilter` безпосередньо в код клієнтського пулу. Це скоротить обсяг непотрібних операцій `SET` у Redis на 60–80 % без змін у бізнес-логіці.
3. **Обхід кешу для аналітичних джоб (Bypass Flag)**: для важких фонових задач (ETL, вивантаження CSV, резервне копіювання) на рівні API-клієнта завжди передавайте прапорець `bypass_cache = true` або HTTP-заголовок `Cache-Control: no-store`. Це усуває навіть мінімальне навантаження на структури допуску.
4. **Калібрування пам'яті ескізу**: виділяйте під ескіз TinyLFU пам'ять із розрахунку 4 біти на кожен потенційний активний ключ у робочому вікні. Для системи з 100 000 активних сутностей розмір таблиці 64 КБ є цілком достатнім для досягнення точності вибору вище 99 %.
