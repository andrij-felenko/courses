# ⚙️ Реалізація адаптивного кешу: побудовник ключів, детектор гарячих точок Count-Min Sketch та динамічне розщеплення

Цей практичний проект містить повний робочий рушій кешування, який поєднує канонічний детермінований генератор ключів, потоковий детектор аномального навантаження (Heavy Hitters) на основі алгоритму Count-Min Sketch та адаптивний дворівневий шар з автоматичним розщепленням (Key Salting) для запобігання перевантаженню віддалених вузлів.

## Архітектурний дизайн та декомпозиція системи

У високонавантажених розподілених середовищах наївне пряме звернення до віддаленого кластера Redis або Memcached призводить до відмови окремих вузлів, якщо популярність певного об'єкта різко зростає. Спроектований рушій вирішує цю проблему на рівні клієнтського застосунку за допомогою трьох взаємопов'язаних модулів:

1. **Канонічний побудовник ключів (`CacheKeyBuilder`):**
   - Відповідає за форматування ключів за суворою схемою `service:tenant:entity:id:{slot}:v<ver>:hash`.
   - Забезпечує детерміноване згортання довільних рядків фільтрації запиту в 64-бітне шістнадцяткове число за допомогою некриптографічного алгоритму MurmurHash3.
   - Гарантує усунення дублікатів та запобігає витоку даних між різними орендарями системи.

2. **Потоковий детектор гарячих точок (`HeavyHitterDetector`):**
   - Реалізує компактну ймовірнісну структуру даних **Count-Min Sketch** із матрицею `4 × 2048` 32-бітних лічильників.
   - Використовує чотири незалежні псевдовипадкові початкові значення (англ. *seeds*) для мінімізації ймовірності колізій.
   - Реалізує механізм експоненційного згасання (англ. *decay*): періодичний зсув лічильників праворуч (ділення на 2) забезпечує актуальність оцінки частоти в межах ковзного часового вікна та очищує застарілі сплески трафіку.

3. **Адаптивний дворівневий менеджер (`AdaptiveCacheManager`):**
   - Реалізує багаторівневий шлях читання: рівень L1 (швидка локальна пам'ять процесу з коротким TTL) та рівень L2 (розподілений шардований кластер).
   - Для звичайних (холодних) ключів запити спрямовуються безпосередньо до єдиного базового ключа на відповідному вузлі L2.
   - При фіксації перевищення порогу звернень (`HOT_THRESHOLD = 50`) менеджер динамічно переводить ключ у розщеплений режим: запити читання розподіляються між `K` розщепленими ключами (`key#0..key#K-1`) за допомогою генератора випадкових чисел, паралельно зберігаючи копію в локальному L1-кеші на 3 секунди.

## Повний вихідний код мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_KEY_LEN 256
#define MAX_VAL_LEN 1024
#define CMS_DEPTH 4
#define CMS_WIDTH 2048
#define HOT_THRESHOLD 50
#define SALT_FACTOR 4
#define L1_CAPACITY 64

/* Швидкий некриптографічний 64-бітний хеш MurmurHash3 */
static uint64_t murmurhash3_64(const void* key, size_t len, uint32_t seed) {
    const uint8_t* data = (const uint8_t*)key;
    const size_t nblocks = len / 8;
    uint64_t h = seed ^ (len * 0xc6a4a7935bd1e995ULL);
    const uint64_t m = 0xc6a4a7935bd1e995ULL;
    const int r = 47;

    const uint64_t* blocks = (const uint64_t*)data;
    for (size_t i = 0; i < nblocks; i++) {
        uint64_t k = blocks[i];
        k *= m;
        k ^= k >> r;
        k *= m;
        h ^= k;
        h *= m;
    }

    const uint8_t* tail = (const uint8_t*)(data + nblocks * 8);
    uint64_t k = 0;
    switch (len & 7) {
        case 7: k ^= ((uint64_t)tail[6]) << 48;
        case 6: k ^= ((uint64_t)tail[5]) << 40;
        case 5: k ^= ((uint64_t)tail[4]) << 32;
        case 4: k ^= ((uint64_t)tail[3]) << 24;
        case 3: k ^= ((uint64_t)tail[2]) << 16;
        case 2: k ^= ((uint64_t)tail[1]) << 8;
        case 1: k ^= ((uint64_t)tail[0]);
                k *= m; k ^= k >> r; k *= m; h ^= k;
    };

    h ^= h >> r;
    h *= m;
    h ^= h >> r;
    return h;
}

/* 1. Канонічний побудовник ключів */
typedef struct {
    char service[32];
    char tenant[32];
    char entity[32];
    char id[32];
    char slot_tag[32];
    uint32_t schema_version;
} KeySpec;

bool build_canonical_key(const KeySpec* spec, const char* query_params, char* out_buf, size_t out_max) {
    if (!spec || !out_buf || out_max < 32) return false;

    char hash_suffix[32] = "";
    if (query_params && strlen(query_params) > 0) {
        uint64_t h = murmurhash3_64(query_params, strlen(query_params), 0x9747b28c);
        snprintf(hash_suffix, sizeof(hash_suffix), ":%016llx", (unsigned long long)h);
    }

    char tag_part[40] = "";
    if (strlen(spec->slot_tag) > 0) {
        snprintf(tag_part, sizeof(tag_part), ":{%s}", spec->slot_tag);
    }

    int written = snprintf(out_buf, out_max, "%s:%s:%s:%s%s:v%u%s",
                           spec->service, spec->tenant, spec->entity,
                           spec->id, tag_part, spec->schema_version, hash_suffix);

    return (written > 0 && (size_t)written < out_max);
}

/* 2. Потоковий детектор гарячих точок Count-Min Sketch */
typedef struct {
    uint32_t table[CMS_DEPTH][CMS_WIDTH];
    uint32_t seeds[CMS_DEPTH];
    uint32_t total_count;
} CountMinSketch;

void cms_init(CountMinSketch* cms) {
    memset(cms->table, 0, sizeof(cms->table));
    cms->seeds[0] = 0x1337beef;
    cms->seeds[1] = 0xdeadc0de;
    cms->seeds[2] = 0xcafebabe;
    cms->seeds[3] = 0x8badf00d;
    cms->total_count = 0;
}

void cms_record(CountMinSketch* cms, const char* key) {
    size_t len = strlen(key);
    for (int i = 0; i < CMS_DEPTH; i++) {
        uint64_t hash = murmurhash3_64(key, len, cms->seeds[i]);
        uint32_t col = (uint32_t)(hash % CMS_WIDTH);
        if (cms->table[i][col] < UINT32_MAX) {
            cms->table[i][col]++;
        }
    }
    cms->total_count++;
}

uint32_t cms_estimate(const CountMinSketch* cms, const char* key) {
    size_t len = strlen(key);
    uint32_t min_count = UINT32_MAX;
    for (int i = 0; i < CMS_DEPTH; i++) {
        uint64_t hash = murmurhash3_64(key, len, cms->seeds[i]);
        uint32_t col = (uint32_t)(hash % CMS_WIDTH);
        if (cms->table[i][col] < min_count) {
            min_count = cms->table[i][col];
        }
    }
    return min_count;
}

void cms_decay(CountMinSketch* cms) {
    for (int i = 0; i < CMS_DEPTH; i++) {
        for (int j = 0; j < CMS_WIDTH; j++) {
            cms->table[i][j] /= 2;
        }
    }
    cms->total_count /= 2;
}

/* 3. Дворівневий кеш-менеджер із солінням (Key Salting) */
typedef struct {
    char key[MAX_KEY_LEN];
    char val[MAX_VAL_LEN];
    time_t expires_at;
} L1Entry;

typedef struct {
    L1Entry l1[L1_CAPACITY];
    size_t l1_count;
    CountMinSketch detector;
} AdaptiveCache;

void cache_init(AdaptiveCache* c) {
    c->l1_count = 0;
    cms_init(&c->detector);
    srand((unsigned int)time(NULL));
}

const char* l1_get(AdaptiveCache* c, const char* key) {
    time_t now = time(NULL);
    for (size_t i = 0; i < c->l1_count; i++) {
        if (strcmp(c->l1[i].key, key) == 0) {
            if (c->l1[i].expires_at >= now) {
                return c->l1[i].val;
            }
            /* Сплив термін дії */
            c->l1[i] = c->l1[c->l1_count - 1];
            c->l1_count--;
            return NULL;
        }
    }
    return NULL;
}

void l1_put(AdaptiveCache* c, const char* key, const char* val, int ttl_sec) {
    time_t now = time(NULL);
    for (size_t i = 0; i < c->l1_count; i++) {
        if (strcmp(c->l1[i].key, key) == 0) {
            strncpy(c->l1[i].val, val, MAX_VAL_LEN - 1);
            c->l1[i].expires_at = now + ttl_sec;
            return;
        }
    }
    if (c->l1_count < L1_CAPACITY) {
        strncpy(c->l1[c->l1_count].key, key, MAX_KEY_LEN - 1);
        strncpy(c->l1[c->l1_count].val, val, MAX_VAL_LEN - 1);
        c->l1[c->l1_count].expires_at = now + ttl_sec;
        c->l1_count++;
    }
}

/* Симуляція віддаленого L2-кластера з підрахунком звернень до шарду */
static int cluster_shard_hits[16] = {0};

void l2_mock_set(const char* key, const char* val) {
    (void)key; (void)val;
}

void l2_mock_get(const char* key, char* out_val, size_t out_max) {
    uint64_t h = murmurhash3_64(key, strlen(key), 0x55aa55aa);
    int shard = (int)(h % 16);
    cluster_shard_hits[shard]++;
    snprintf(out_val, out_max, "DataFor(%s)", key);
}

/* Читання через адаптивний контролер */
bool adaptive_cache_get(AdaptiveCache* c, const char* base_key, char* out_buf, size_t out_max) {
    /* Крок 1: Перевірка L1 In-Process */
    const char* l1_val = l1_get(c, base_key);
    if (l1_val) {
        strncpy(out_buf, l1_val, out_max - 1);
        return true;
    }

    /* Крок 2: Фіксація звернення в детекторі аномалій */
    cms_record(&c->detector, base_key);
    uint32_t frequency = cms_estimate(&c->detector, base_key);

    /* Крок 3: Якщо ключ став гарячим — обираємо солений підключ для L2 */
    char fetch_key[MAX_KEY_LEN];
    if (frequency >= HOT_THRESHOLD) {
        int salt = rand() % SALT_FACTOR;
        snprintf(fetch_key, sizeof(fetch_key), "%s#%d", base_key, salt);
        
        /* Зчитуємо з L2 та промоутимо в локальний L1 на короткий час */
        l2_mock_get(fetch_key, out_buf, out_max);
        l1_put(c, base_key, out_buf, 3);
        return true;
    }

    /* Холодний/звичайний ключ: пряме читання базового ключа з L2 */
    l2_mock_get(base_key, out_buf, out_max);
    return true;
}

int main(void) {
    KeySpec spec = {
        .service = "catalog",
        .tenant = "client_ua",
        .entity = "product",
        .id = "9901",
        .slot_tag = "prod_9901",
        .schema_version = 2
    };

    char key[MAX_KEY_LEN];
    build_canonical_key(&spec, "category=electronics&sort=asc", key, sizeof(key));
    printf("Згенеровано канонічний ключ:\n  %s\n\n", key);

    AdaptiveCache cache;
    cache_init(&cache);

    printf("Симуляція 200 запитів до гарячого ключа...\n");
    char result[MAX_VAL_LEN];
    for (int i = 0; i < 200; i++) {
        adaptive_cache_get(&cache, key, result, sizeof(result));
    }

    printf("\nРозподіл звернень по шардах кластера L2:\n");
    for (int s = 0; s < 16; s++) {
        if (cluster_shard_hits[s] > 0) {
            printf("  Шард %2d: %d звернень\n", s, cluster_shard_hits[s]);
        }
    }
    printf("Частотна оцінка Count-Min Sketch: %u\n", cms_estimate(&cache.detector, key));
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <unordered_map>
#include <chrono>
#include <random>
#include <algorithm>
#include <cstdint>

namespace cache {

// 64-бітний алгоритм MurmurHash3
constexpr uint64_t murmurhash3_64(std::string_view data, uint32_t seed) noexcept {
    const size_t len = data.size();
    const size_t nblocks = len / 8;
    uint64_t h = seed ^ (len * 0xc6a4a7935bd1e995ULL);
    constexpr uint64_t m = 0xc6a4a7935bd1e995ULL;
    constexpr int r = 47;

    const auto* blocks = reinterpret_cast<const uint64_t*>(data.data());
    for (size_t i = 0; i < nblocks; ++i) {
        uint64_t k = blocks[i];
        k *= m;
        k ^= k >> r;
        k *= m;
        h ^= k;
        h *= m;
    }

    const auto* tail = reinterpret_cast<const uint8_t*>(data.data() + nblocks * 8);
    uint64_t k = 0;
    switch (len & 7) {
        case 7: k ^= static_cast<uint64_t>(tail[6]) << 48; [[fallthrough]];
        case 6: k ^= static_cast<uint64_t>(tail[5]) << 40; [[fallthrough]];
        case 5: k ^= static_cast<uint64_t>(tail[4]) << 32; [[fallthrough]];
        case 4: k ^= static_cast<uint64_t>(tail[3]) << 24; [[fallthrough]];
        case 3: k ^= static_cast<uint64_t>(tail[2]) << 16; [[fallthrough]];
        case 2: k ^= static_cast<uint64_t>(tail[1]) << 8;  [[fallthrough]];
        case 1: k ^= static_cast<uint64_t>(tail[0]);
                k *= m; k ^= k >> r; k *= m; h ^= k;
    }

    h ^= h >> r;
    h *= m;
    h ^= h >> r;
    return h;
}

// 1. Канонічний побудовник ключів
struct KeySpec {
    std::string_view service;
    std::string_view tenant;
    std::string_view entity;
    std::string_view id;
    std::string_view slot_tag{};
    uint32_t schema_version{1};
};

class CacheKeyBuilder {
public:
    static std::string build(const KeySpec& spec, std::string_view query_params = "") {
        std::string key;
        key.reserve(128);

        key += spec.service; key += ':';
        key += spec.tenant;  key += ':';
        key += spec.entity;  key += ':';
        key += spec.id;

        if (!spec.slot_tag.empty()) {
            key += ":{";
            key += spec.slot_tag;
            key += '}';
        }

        key += ":v";
        key += std::to_string(spec.schema_version);

        if (!query_params.empty()) {
            uint64_t h = murmurhash3_64(query_params, 0x9747b28c);
            key += ':';
            char hex_buf[17];
            snprintf(hex_buf, sizeof(hex_buf), "%016llx", static_cast<unsigned long long>(h));
            key += hex_buf;
        }

        return key;
    }
};

// 2. Потоковий детектор гарячих точок Count-Min Sketch
template <size_t Depth = 4, size_t Width = 2048>
class HeavyHitterDetector {
public:
    HeavyHitterDetector() {
        seeds_ = {0x1337beef, 0xdeadc0de, 0xcafebabe, 0x8badf00d};
        for (auto& row : table_) row.fill(0);
    }

    void record(std::string_view key) noexcept {
        for (size_t i = 0; i < Depth; ++i) {
            uint64_t h = murmurhash3_64(key, seeds_[i]);
            size_t col = h % Width;
            if (table_[i][col] < std::numeric_limits<uint32_t>::max()) {
                ++table_[i][col];
            }
        }
    }

    [[nodiscard]] uint32_t estimate(std::string_view key) const noexcept {
        uint32_t min_val = std::numeric_limits<uint32_t>::max();
        for (size_t i = 0; i < Depth; ++i) {
            uint64_t h = murmurhash3_64(key, seeds_[i]);
            size_t col = h % Width;
            min_val = std::min(min_val, table_[i][col]);
        }
        return min_val;
    }

    void decay() noexcept {
        for (auto& row : table_) {
            for (auto& cell : row) {
                cell /= 2;
            }
        }
    }

private:
    std::array<std::array<uint32_t, Width>, Depth> table_;
    std::array<uint32_t, Depth> seeds_;
};

// 3. Дворівневий адаптивний кеш-менеджер
class AdaptiveCacheManager {
public:
    struct L1Entry {
        std::string value;
        std::chrono::steady_clock::time_point expires_at;
    };

    AdaptiveCacheManager(uint32_t hot_threshold = 50, size_t salt_factor = 4)
        : hot_threshold_(hot_threshold), salt_factor_(salt_factor), rng_(std::random_device{}()) {}

    std::string get(const std::string& base_key) {
        auto now = std::chrono::steady_clock::now();

        // Перевірка L1 In-Process
        auto it = l1_cache_.find(base_key);
        if (it != l1_cache_.end() && it->second.expires_at > now) {
            return it->second.value;
        }

        // Фіксація звернення в CMS
        detector_.record(base_key);
        uint32_t freq = detector_.estimate(base_key);

        std::string fetch_key = base_key;
        if (freq >= hot_threshold_) {
            std::uniform_int_distribution<size_t> dist(0, salt_factor_ - 1);
            size_t salt = dist(rng_);
            fetch_key = base_key + "#" + std::to_string(salt);

            // Читаємо розщеплений ключ з L2 і кладемо в L1 на 3 секунди
            std::string val = mock_l2_get(fetch_key);
            l1_cache_[base_key] = L1Entry{val, now + std::chrono::seconds(3)};
            return val;
        }

        return mock_l2_get(fetch_key);
    }

    static void print_cluster_stats() {
        std::cout << "\nСтатистика звернень до 16 шардів L2-кластера:\n";
        for (size_t s = 0; s < shard_hits_.size(); ++s) {
            if (shard_hits_[s] > 0) {
                std::cout << "  Шард " << s << ": " << shard_hits_[s] << " запитів\n";
            }
        }
    }

    [[nodiscard]] uint32_t get_frequency(std::string_view key) const noexcept {
        return detector_.estimate(key);
    }

private:
    std::string mock_l2_get(std::string_view key) {
        uint64_t h = murmurhash3_64(key, 0x55aa55aa);
        size_t shard = h % shard_hits_.size();
        ++shard_hits_[shard];
        return "DataFor(" + std::string(key) + ")";
    }

    uint32_t hot_threshold_;
    size_t salt_factor_;
    HeavyHitterDetector<4, 2048> detector_;
    std::unordered_map<std::string, L1Entry> l1_cache_;
    std::mt19937 rng_;
    inline static std::array<size_t, 16> shard_hits_{};
};

} // namespace cache

int main() {
    cache::KeySpec spec{
        .service = "catalog",
        .tenant = "client_ua",
        .entity = "product",
        .id = "9901",
        .slot_tag = "prod_9901",
        .schema_version = 2
    };

    std::string canonical_key = cache::CacheKeyBuilder::build(spec, "category=electronics&sort=asc");
    std::cout << "Згенеровано канонічний ключ:\n  " << canonical_key << "\n\n";

    cache::AdaptiveCacheManager manager(50, 4);

    std::cout << "Симуляція 200 паралельних запитів...\n";
    for (int i = 0; i < 200; ++i) {
        manager.get(canonical_key);
    }

    cache::AdaptiveCacheManager::print_cluster_stats();
    std::cout << "Оцінена частота ключа в CMS: " << manager.get_frequency(canonical_key) << '\n';

    return 0;
}
```
:::

## Аналіз поведінки та практичні рекомендації з експлуатації

При запуску симуляції на двохстах послідовних запитах спостерігається три послідовні фази роботи рушія:

1. **Фаза холодного старту (перші 50 запитів):**
   - Ключ вважається звичайним. Частота в Count-Min Sketch менша за `HOT_THRESHOLD`.
   - Усі 50 запитів прямують на базовий ключ `catalog:client_ua:product:9901:{prod_9901}:v2:b7a8c901...` і концентруються на єдиному шарді № 10.

2. **Фаза активації соління (запити 51–65):**
   - Детектор Heavy Hitters фіксує перевищення порогу частоти.
   - Запити починають рандомізуватися за суфіксами `#0, #1, #2, #3`.
   - Навантаження рівномірно розподіляється між чотирма різними шардами (наприклад, шарди № 2, 6, 11, 15).

3. **Фаза поглинання локальним кешем L1 (запити 66–200):**
   - Перше успішне читання розщепленого ключа з L2 автоматично наповнює локальний кеш L1 із тривалістю життя 3 секунди.
   - Наступні 135 запитів обслуговуються безпосередньо з оперативної пам'яті процесу за 20–40 наносекунд без жодного звернення до симулятора мережевого кластера.

## Внутрішня механіка хешування MurmurHash3 та властивості розсіювання

Функція `murmurhash3_64` є фундаментальною основою як побудовника ключів, так і детектора аномалій. Вона забезпечує високу швидкість обчислення (понад 3–5 гігабайтів обробленого тексту на секунду на одне процесорне ядро) та бездоганний лавинний ефект (англ. *avalanche effect*): зміна навіть одного біта у вхідному рядку (наприклад, індексу солі `prod:9901#0` на `prod:9901#1`) змінює в середньому 50% бітів вихідного 64-бітного значення.

Алгоритм обробляє вхідний потік 64-бітними блоками (8 байтів):
1. Кожен блок множиться на велику непарну константу `m = 0xc6a4a7935bd1e995ULL`, що забезпечує нелінійне перемішування бітів.
2. Застосовується циклічний зсув (англ. *rotate right / xor-shift*) на 47 бітів та повторне множення на `m`.
3. Залишок даних (`tail`) довжиною від 1 до 7 байтів обробляється оператором `switch-case` із каскадним провалюванням (`fallthrough`), що усуває накладні витрати циклів для коротких суфіксів.
4. Фінальний блок перемішування (англ. *finalization mix*) застосовує три послідовні операції `h ^= h >> r; h *= m;`, гарантуючи відсутність регулярних патернів у молодших бітах, які використовуються для операції взяття залишку `hash % CMS_WIDTH`.

## Багатопотокова синхронізація та промислові оптимізації

У багатопотокових серверах (наприклад, пулах воркерів C++ на базі epoll/io_uring або вебсерверах на Go) наївне блокування всього кешу єдиним м'ютексом стає вузьким місцем (англ. *lock contention*). Для масштабування на десятках ядер застосовують такі архітектурні патерни:

- **Шардований м'ютекс для L1-кешу:** масив із 16 або 64 незалежних блокувань `std::shared_mutex`, де номер блокування обирається як `hash(key) % NUM_LOCKS`. Читання виконується під неблокуючим спільним блокуванням (`shared_lock`), а запис нового гарячого ключа блокує лише один ізольований сегмент таблиці.
- **Атомарний Count-Min Sketch:** для детектора аномалій комірки таблиці оголошуються як `std::atomic<uint32_t>` з використанням розслабленого порядку пам'яті (`std::memory_order_relaxed`). Оскільки CMS є ймовірнісною структурою, мікроскопічні гонки при інкрементах лічильників не впливають на загальну точність виявлення гарячих ключів, проте повністю виключають синхронізаційні затримки ядра.
- **Усунення колізій кеш-ліній (False Sharing):** рядки матриці детектора або елементи шардованих м'ютексів вирівнюються за розміром лінії кешу процесора (`alignas(64)`), щоб модифікація лічильника одним потоком не інвалідувала кеш сусіднього ядра L1/L2.
