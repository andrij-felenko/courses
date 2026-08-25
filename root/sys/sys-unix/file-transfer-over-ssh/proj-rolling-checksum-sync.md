# ⚙️ Реалізація ковзного хешу та дельта-пошуку для синхронізації блоків

Цей практичний розбір містить алгоритмічну модель та робочу реалізацію дельта-алгоритму синхронізації блоків мовами C та C++, демонструючи обчислення 32-бітного ковзного хешу (rollsum) за час O(1) на кожен байт та пошук збігів зі зміщенням у потоці даних без повторного передавання незмінених блоків.

## Постановка задачі дельта-синхронізації

Уявімо два хости у мережі: джерело, яке має свіжу версію файлу A розміром N_A байтів, та одержувач, на диску якого зберігається старіша версія B розміром N_B байтів. Якщо на початку файлу A було додано всього один байт тексту чи заголовка, абсолютні зміщення всіх наступних блоків файлу зсуваються на одну позицію праворуч.

Якщо використати наївний підхід із розбиттям файлу на блоки за фіксованими межами (наприклад, кожні 2048 байтів від початку файлу), поблочне порівняння покаже, що 100% блоків файлу змінилися. У результаті програма буде змушена перекачати весь гігабайтний файл заново, хоча 99.9% його байтів є абсолютно ідентичними.

Щоб виявити зсунуті ідентичні блоки, відправник повинен просканувати весь файл A «ковзним вікном» розміру S, перевіряючи кожну можливу байтову позицію від 0 до N_A - S.

Пряме обчислення важкого криптографічного хешу (наприклад, SHA-256 або MD5) на кожному байтовому зсуві вимагатиме O(N · S) операцій. Для файлу розміром 1 ГБ і розміру блоку 2 КБ це складе понад два трильйони операцій читання й обчислення, що повністю заблокує процесор і зведе нанівець перевагу дельта-передачі.

Архітектурний розв'язок rsync базується на багаторівневому комбінованому хешуванні:
1. **Слабкий ковзний хеш (32 біти):** обчислюється на кожному байтовому зсуві за константний час O(1) шляхом віднімання значення байта, що вибув з вікна, і додавання нового байта, що зайшов у вікно.
2. **Сильний хеш (64 або 128 бітів):** обчислюється над поточним вікном лише тоді, коли значення слабкого хешу знайдено в хеш-таблиці сигнатур цільового файлу B.

## Математична модель алгоритму Rollsum

Ковзний хеш rsync (модифікація алгоритму Марка Адлера, відомого як Adler-32) використовує дві 16-бітні контрольні суми a та b над масивом байтів вікна довжиною S за модулем M = 65536 (2¹⁶).

Для запобігання виродженню хешу при великій кількості нульових байтів (наприклад, у розріджених файлах або неініціалізованих буферах) до кожного байта додається зміщення CHAR_OFFSET = 31.

Початкові значення для першого вікна байтів x₀, x₁, ..., x_{S-1}:

```text
a = sum(x_i + 31)  mod 65536,  де i від 0 до S-1
b = sum((S - i) * (x_i + 31))  mod 65536,  де i від 0 до S-1
rollsum = (b << 16) | a
```

Сума `a` є простою сумою всіх байтів вікна зі зміщенням. Сума `b` є зваженою сумою, де перший байт входить із коефіцієнтом S, другий із коефіцієнтом S - 1, а останній — із коефіцієнтом 1. Завдяки цьому сума `b` надзвичайно чутлива до порядку слідування байтів: перестановка двох сусідніх символів гарантовано змінює значення `b`.

При зсуві вікна на один байт праворуч (старий байт x_out вибуває, новий байт x_in заходить) нові суми перераховуються за формулами:

```text
a_new = (a_old - x_out + x_in)  mod 65536
b_new = (b_old - S * (x_out + 31) + a_new)  mod 65536
```

Оскільки всі обчислення виконуються над 16-бітними регістрами за модулем 65536, операція взяття залишку в процесорі зводиться до звичайного бітового маскування `& 0xffff`. Для оновлення хешу потрібно лише одне множення, три додавання та два маскування, що займає кілька тактів CPU незалежно від того, чи розмір блоку S становить 512 байтів, чи 64 кілобайти.

## Реалізація алгоритму на C та C++

Наведений нижче код реалізує структури сигнатур блоків цільового файлу, обчислення ковзного хешу, побудову швидкої хеш-таблиці та генерацію дельта-потоку токенів збігу (`MATCH`) і сирих даних (`LITERAL`).

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define CHAR_OFFSET 31
#define BLOCK_SIZE 64
#define HASH_TABLE_SIZE 1024

/* 64-бітний сильний хеш FNV-1a для демонстрації */
static uint64_t fnv1a_64(const uint8_t *data, size_t len) {
    uint64_t hash = 0xcbf29ce484222325ULL;
    for (size_t i = 0; i < len; ++i) {
        hash ^= data[i];
        hash *= 0x100000001b3ULL;
    }
    return hash;
}

/* Структура 32-бітного ковзного хешу rollsum */
typedef struct {
    uint16_t a;
    uint16_t b;
} Rollsum;

static inline void rollsum_init(Rollsum *r, const uint8_t *buf, size_t len) {
    uint32_t a = 0;
    uint32_t b = 0;
    for (size_t i = 0; i < len; ++i) {
        uint32_t val = (uint32_t)buf[i] + CHAR_OFFSET;
        a += val;
        b += (uint32_t)(len - i) * val;
    }
    r->a = (uint16_t)(a & 0xffff);
    r->b = (uint16_t)(b & 0xffff);
}

static inline void rollsum_rotate(Rollsum *r, uint8_t out_byte, uint8_t in_byte, size_t len) {
    uint32_t out_val = (uint32_t)out_byte + CHAR_OFFSET;
    uint32_t in_val = (uint32_t)in_byte + CHAR_OFFSET;
    
    r->a = (uint16_t)((r->a - out_val + in_val) & 0xffff);
    r->b = (uint16_t)((r->b - (uint32_t)len * out_val + r->a) & 0xffff);
}

static inline uint32_t rollsum_digest(const Rollsum *r) {
    return ((uint32_t)r->b << 16) | (uint32_t)r->a;
}

/* Сигнатура блоку цільового файлу */
typedef struct BlockSig {
    uint32_t block_index;
    uint32_t rollsum;
    uint64_t strong_hash;
    struct BlockSig *next;
} BlockSig;

typedef struct {
    BlockSig *buckets[HASH_TABLE_SIZE];
} SigTable;

static void sig_table_init(SigTable *table) {
    memset(table->buckets, 0, sizeof(table->buckets));
}

static void sig_table_insert(SigTable *table, uint32_t index, uint32_t rsum, uint64_t strong) {
    uint32_t bucket = (rsum ^ (rsum >> 10)) % HASH_TABLE_SIZE;
    BlockSig *node = (BlockSig *)malloc(sizeof(BlockSig));
    if (!node) return;
    node->block_index = index;
    node->rollsum = rsum;
    node->strong_hash = strong;
    node->next = table->buckets[bucket];
    table->buckets[bucket] = node;
}

static int sig_table_find(const SigTable *table, uint32_t rsum, uint64_t strong) {
    uint32_t bucket = (rsum ^ (rsum >> 10)) % HASH_TABLE_SIZE;
    for (BlockSig *curr = table->buckets[bucket]; curr; curr = curr->next) {
        if (curr->rollsum == rsum && curr->strong_hash == strong) {
            return (int)curr->block_index;
        }
    }
    return -1;
}

static void sig_table_free(SigTable *table) {
    for (size_t i = 0; i < HASH_TABLE_SIZE; ++i) {
        BlockSig *curr = table->buckets[i];
        while (curr) {
            BlockSig *tmp = curr->next;
            free(curr);
            curr = tmp;
        }
        table->buckets[i] = NULL;
    }
}

/* Генерація дельти між двома буферами в пам'яті */
static void generate_delta(const uint8_t *target, size_t target_len,
                           const uint8_t *source, size_t source_len) {
    SigTable table;
    sig_table_init(&table);

    /* 1. Фаза побудови сигнатур цільового файлу B */
    size_t num_blocks = (target_len + BLOCK_SIZE - 1) / BLOCK_SIZE;
    for (size_t i = 0; i < num_blocks; ++i) {
        size_t offset = i * BLOCK_SIZE;
        size_t b_len = (offset + BLOCK_SIZE <= target_len) ? BLOCK_SIZE : (target_len - offset);
        
        Rollsum r;
        rollsum_init(&r, target + offset, b_len);
        uint64_t strong = fnv1a_64(target + offset, b_len);
        
        sig_table_insert(&table, (uint32_t)i, rollsum_digest(&r), strong);
    }

    /* 2. Фаза сканування джерела A ковзним вікном */
    size_t src_pos = 0;
    size_t literal_start = 0;
    size_t literal_len = 0;

    Rollsum window_sum;
    bool window_valid = false;

    while (src_pos + BLOCK_SIZE <= source_len) {
        if (!window_valid) {
            rollsum_init(&window_sum, source + src_pos, BLOCK_SIZE);
            window_valid = true;
        } else {
            rollsum_rotate(&window_sum, source[src_pos - 1], source[src_pos + BLOCK_SIZE - 1], BLOCK_SIZE);
        }

        uint32_t rsum = rollsum_digest(&window_sum);
        int matched_block = -1;

        /* Швидка перевірка: чи є такий rollsum у таблиці */
        uint32_t bucket = (rsum ^ (rsum >> 10)) % HASH_TABLE_SIZE;
        if (table.buckets[bucket]) {
            uint64_t strong = fnv1a_64(source + src_pos, BLOCK_SIZE);
            matched_block = sig_table_find(&table, rsum, strong);
        }

        if (matched_block >= 0) {
            /* Якщо були накопичені літеральні байти, видаємо їх */
            if (literal_len > 0) {
                printf("[LITERAL %zu байтів на зміщенні %zu]\n", literal_len, literal_start);
                literal_len = 0;
            }
            printf("[MATCH блок %d на зміщенні %zu]\n", matched_block, src_pos);
            src_pos += BLOCK_SIZE;
            window_valid = false;
            literal_start = src_pos;
        } else {
            if (literal_len == 0) literal_start = src_pos;
            literal_len++;
            src_pos++;
        }
    }

    /* Залишкові байти в кінці файлу */
    literal_len += (source_len - src_pos);
    if (literal_len > 0) {
        printf("[LITERAL %zu байтів на зміщенні %zu]\n", literal_len, literal_start);
    }

    sig_table_free(&table);
}

int main(void) {
    const uint8_t target[] = "The quick brown fox jumps over the lazy dog. "
                             "Systems programming with rsync and ssh provides "
                             "reliable data transfer for all production systems.";
    const uint8_t source[] = "PREFIX_INSERTED_DATA: "
                             "The quick brown fox jumps over the lazy dog. "
                             "Systems programming with rsync and ssh provides "
                             "MODIFIED data transfer for all production systems.";

    generate_delta(target, strlen((const char *)target),
                   source, strlen((const char *)source));
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <unordered_map>
#include <variant>
#include <cstdint>
#include <cstring>

namespace rsync_delta {

inline constexpr uint16_t CHAR_OFFSET = 31;
inline constexpr size_t BLOCK_SIZE = 64;

// 64-бітний сильний хеш FNV-1a над масивом байтів
[[nodiscard]] constexpr uint64_t fnv1a_64(std::span<const uint8_t> data) noexcept {
    uint64_t hash = 0xcbf29ce484222325ULL;
    for (uint8_t byte : data) {
        hash ^= byte;
        hash *= 0x100000001b3ULL;
    }
    return hash;
}

// 32-бітний ковзний хеш rollsum
class RollingChecksum {
public:
    constexpr RollingChecksum() noexcept = default;

    void init(std::span<const uint8_t> data) noexcept {
        uint32_t sum_a = 0;
        uint32_t sum_b = 0;
        const size_t len = data.size();
        for (size_t i = 0; i < len; ++i) {
            const auto val = static_cast<uint32_t>(data[i]) + CHAR_OFFSET;
            sum_a += val;
            sum_b += static_cast<uint32_t>(len - i) * val;
        }
        a_ = static_cast<uint16_t>(sum_a & 0xffff);
        b_ = static_cast<uint16_t>(sum_b & 0xffff);
    }

    void rotate(uint8_t out_byte, uint8_t in_byte, size_t block_len) noexcept {
        const auto out_val = static_cast<uint32_t>(out_byte) + CHAR_OFFSET;
        const auto in_val = static_cast<uint32_t>(in_byte) + CHAR_OFFSET;

        a_ = static_cast<uint16_t>((a_ - out_val + in_val) & 0xffff);
        b_ = static_cast<uint16_t>((b_ - static_cast<uint32_t>(block_len) * out_val + a_) & 0xffff);
    }

    [[nodiscard]] uint32_t digest() const noexcept {
        return (static_cast<uint32_t>(b_) << 16) | static_cast<uint32_t>(a_);
    }

private:
    uint16_t a_{0};
    uint16_t b_{0};
};

// Токени дельта-потоку
struct MatchToken {
    uint32_t block_index;
    size_t source_offset;
};

struct LiteralToken {
    std::vector<uint8_t> bytes;
    size_t source_offset;
};

using DeltaToken = std::variant<MatchToken, LiteralToken>;

// Генератор дельти
class DeltaEngine {
public:
    struct BlockSignature {
        uint32_t block_index;
        uint64_t strong_hash;
    };

    static std::vector<DeltaToken> generate(std::span<const uint8_t> target,
                                            std::span<const uint8_t> source) {
        std::vector<DeltaToken> delta;
        std::unordered_multimap<uint32_t, BlockSignature> sig_map;

        // 1. Індексація блоків цільового файлу
        const size_t num_blocks = (target.size() + BLOCK_SIZE - 1) / BLOCK_SIZE;
        for (size_t i = 0; i < num_blocks; ++i) {
            const size_t offset = i * BLOCK_SIZE;
            const size_t b_len = std::min(BLOCK_SIZE, target.size() - offset);
            const auto block_data = target.subspan(offset, b_len);

            RollingChecksum rsum;
            rsum.init(block_data);
            const uint64_t strong = fnv1a_64(block_data);

            sig_map.emplace(rsum.digest(), BlockSignature{static_cast<uint32_t>(i), strong});
        }

        // 2. Сканування джерела ковзним вікном
        size_t src_pos = 0;
        std::vector<uint8_t> current_literals;
        size_t literal_start = 0;

        RollingChecksum window;
        bool window_valid = false;

        while (src_pos + BLOCK_SIZE <= source_len(source)) {
            if (!window_valid) {
                window.init(source.subspan(src_pos, BLOCK_SIZE));
                window_valid = true;
            } else {
                window.rotate(source[src_pos - 1], source[src_pos + BLOCK_SIZE - 1], BLOCK_SIZE);
            }

            const uint32_t rsum = window.digest();
            int matched_block = -1;

            if (auto range = sig_map.equal_range(rsum); range.first != range.second) {
                const uint64_t strong = fnv1a_64(source.subspan(src_pos, BLOCK_SIZE));
                for (auto it = range.first; it != range.second; ++it) {
                    if (it->second.strong_hash == strong) {
                        matched_block = static_cast<int>(it->second.block_index);
                        break;
                    }
                }
            }

            if (matched_block >= 0) {
                if (!current_literals.empty()) {
                    delta.emplace_back(LiteralToken{std::move(current_literals), literal_start});
                    current_literals.clear();
                }
                delta.emplace_back(MatchToken{static_cast<uint32_t>(matched_block), src_pos});
                src_pos += BLOCK_SIZE;
                window_valid = false;
                literal_start = src_pos;
            } else {
                if (current_literals.empty()) {
                    literal_start = src_pos;
                }
                current_literals.push_back(source[src_pos]);
                src_pos++;
            }
        }

        // Залишкові байти
        while (src_pos < source.size()) {
            if (current_literals.empty()) literal_start = src_pos;
            current_literals.push_back(source[src_pos++]);
        }

        if (!current_literals.empty()) {
            delta.emplace_back(LiteralToken{std::move(current_literals), literal_start});
        }

        return delta;
    }

private:
    static size_t source_len(std::span<const uint8_t> s) noexcept {
        return s.size();
    }
};

} // namespace rsync_delta

int main() {
    using namespace std::string_view_literals;

    const auto target_str = "The quick brown fox jumps over the lazy dog. "
                            "Systems programming with rsync and ssh provides "
                            "reliable data transfer for all production systems."sv;
    const auto source_str = "PREFIX_INSERTED_DATA: "
                            "The quick brown fox jumps over the lazy dog. "
                            "Systems programming with rsync and ssh provides "
                            "MODIFIED data transfer for all production systems."sv;

    const std::span<const uint8_t> target{reinterpret_cast<const uint8_t*>(target_str.data()), target_str.size()};
    const std::span<const uint8_t> source{reinterpret_cast<const uint8_t*>(source_str.data()), source_str.size()};

    const auto delta = rsync_delta::DeltaEngine::generate(target, source);

    for (const auto& token : delta) {
        std::visit([](const auto& t) {
            using T = std::decay_t<decltype(t)>;
            if constexpr (std::is_same_v<T, rsync_delta::MatchToken>) {
                std::cout << "[MATCH блок " << t.block_index << " на зміщенні " << t.source_offset << "]\n";
            } else if constexpr (std::is_same_v<T, rsync_delta::LiteralToken>) {
                std::cout << "[LITERAL " << t.bytes.size() << " байтів на зміщенні " << t.source_offset << "]\n";
            }
        }, token);
    }

    return 0;
}
```
:::

## Інженерні компроміси та практичні пастки

1. **Колізії слабкого хешу:** 32-бітний простір контрольної суми становить 2³² ≈ 4.29 мільярда можливих значень. Якщо розмір файлу перевищує 100 МБ, кількість перевірок ковзного вікна наближається до 10⁸. За парадоксом днів народження ймовірність появи однакового слабкого хешу для абсолютно різних блоків стає практично неминучою. Якщо програміст знехтує звіркою сильного хешу, цільовий файл буде зібраний зі змішаними даними, що призведе до тихого спотворення інформації.
2. **Вибір розміру блоку S:**
   - Занадто малий розмір блоку (наприклад, 128 або 256 байтів) забезпечує високу точність знаходження найменших змін, але обсяг таблиці сигнатур стрімко розростається (кількість блоків пропорційна N / S). Передавання самої таблиці сигнатур через мережу може зайняти більше трафіку, ніж передавання зміненого файлу.
   - Занадто великий розмір блоку (наприклад, 64 або 128 кілобайтів) мінімізує обсяг таблиці хешів, але будь-яка зміна одного байта змушує передавати весь великий блок як потік сирих літералів.
   - Утиліта `rsync` вибирає розмір блоку евристично, орієнтуючись на квадратний корінь від розміру файлу: S ≈ max(700, floor(sqrt(N))). Це забезпечує оптимальний баланс між обсягом метаданих сигнатур і гранулярністю передачі дельти.
3. **Пам'ять під хеш-таблицю сигнатур:** Для великих файлів розміром 100 ГБ і блоку 1 КБ генерується близько 100 мільйонів сигнатур. Якщо кожна сигнатура займає в структурі пам'яті 24 байти, таблиця вимагатиме понад 2.4 ГБ оперативної пам'яті лише для одного файлу. Щоб уникнути вичерпання RAM, сучасний rsync обробляє файли порціями та використовує інкрементне завантаження списків файлів.
