# ⚙️ Двигун тегованої інвалідації, версійних епох та відкладеного очищення

Реалізація надійного механізму інвалідації в розподілених сервісах вимагає вирішення трьох взаємопов'язаних завдань:
1. **Групове очищення за тегами (Surrogate Keys):** Автоматичний пошук і видалення всіх ключів, асоційованих зі зміненою сутністю, через двосторонній інвертований індекс без повного сканування сховища.
2. **Миттєве очищення просторів імен за `O(1)` (Generation Bumping):** Перемикання лічильника версії епохи для миттєвого знецінення мільйонів ключів без дискового та мережевого навантаження.
3. **Захист від лагу реплікації (Delayed Double-Delete):** Асинхронне планування повторного видалення ключа з урахуванням затримки передачі даних між майстром і репліками бази даних.

## Архітектура та структури даних

Кеш підтримує дві взаємодоповнюючі структури індексації:
* **Прямий зв'язок (`Key -> Set<Tag>`):** Зберігає перелік усіх тегів, які були прив'язані до конкретного кешованого об'єкта під час його запису. Цей індекс є критично необхідним для запобігання витокам пам'яті (memory leaks). Якщо ключ видаляється напряму або витісняється за алгоритмом `LRU`, кеш зобов'язаний зайти в списки кожного з його тегів і видалити посилання на цей ключ, інакше списки тегів будуть нескінченно розростатися «мертвими» ключами.
* **Інвертований індекс (`Tag -> Set<Key>`):** Зберігає зворотне відображення від семантичного тегу до множини всіх ключів кешу, які залежать від цієї сутності. Коли бізнес-логіка генерує подію оновлення (наприклад, зміну ціни товару `#42`), система знаходить вузол тегу `item:42` за `O(1)` і миттєво отримує точний перелік ключів, що підлягають анулюванню.

У такій дворівневій моделі операція групової інвалідації виконується за час `O(K_tag)`, де `K_tag` — кількість ключів, прив'язаних до конкретного тегу, замість катастрофічного для продуктивності лінійного сканування всієї пам'яті `O(N_total)`.

### Потокобезпека та синхронізація

У багатопотоковому середовищі операція інвалідації повинна бути строго ізольованою. Якщо один потік виконує `purge_tag`, а інший у цей самий момент записує новий ключ із цим самим тегом, виникає стан гонки (race condition), який може призвести до розриву вказівників або втрати щойно записаних даних. У наведеній C++ реалізації доступ до таблиці даних та інвертованого індексу координується спільним м'ютексом `std::mutex`, а модифікації виконуються під ексклюзивним блокуванням `std::unique_lock`. Для високонавантажених шардованих систем цей м'ютекс розділяють за хеш-кошиками (striping locks), щоб операції над різними ключами виконувалися паралельно.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_KEYS_PER_TAG 64
#define MAX_TAGS_PER_KEY 16
#define HASH_BUCKETS 1024

/* Запис у кеші */
typedef struct CacheEntry {
    char key[128];
    char value[512];
    time_t expires_at;
    uint64_t lease_token;
    char tags[MAX_TAGS_PER_KEY][64];
    int tag_count;
    struct CacheEntry* next;
} CacheEntry;

/* Вузол інвертованого індексу тегів */
typedef struct TagNode {
    char tag[64];
    char keys[MAX_KEYS_PER_TAG][128];
    int key_count;
    struct TagNode* next;
} TagNode;

/* Лічильник покоління простору імен */
typedef struct NamespaceGen {
    char ns[64];
    uint64_t generation;
    struct NamespaceGen* next;
} NamespaceGen;

/* Головний стан двигуна інвалідації */
typedef struct {
    CacheEntry* cache_table[HASH_BUCKETS];
    TagNode* tag_index[HASH_BUCKETS];
    NamespaceGen* ns_table[HASH_BUCKETS];
    uint64_t next_lease_id;
} InvalidationEngine;

static unsigned int hash_str(const char* str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_BUCKETS;
}

InvalidationEngine* engine_create(void) {
    InvalidationEngine* eng = (InvalidationEngine*)calloc(1, sizeof(InvalidationEngine));
    eng->next_lease_id = 1000;
    return eng;
}

/* Прив'язка ключа до тегу в інвертованому індексі */
static void add_key_to_tag(InvalidationEngine* eng, const char* tag, const char* key) {
    unsigned int b = hash_str(tag);
    TagNode* cur = eng->tag_index[b];
    while (cur) {
        if (strcmp(cur->tag, tag) == 0) {
            for (int i = 0; i < cur->key_count; ++i) {
                if (strcmp(cur->keys[i], key) == 0) return;
            }
            if (cur->key_count < MAX_KEYS_PER_TAG) {
                strncpy(cur->keys[cur->key_count++], key, 127);
            }
            return;
        }
        cur = cur->next;
    }
    TagNode* node = (TagNode*)malloc(sizeof(TagNode));
    strncpy(node->tag, tag, 63);
    node->tag[63] = '\0';
    strncpy(node->keys[0], key, 127);
    node->keys[0][127] = '\0';
    node->key_count = 1;
    node->next = eng->tag_index[b];
    eng->tag_index[b] = node;
}

/* Запис значення з набором тегів */
void engine_set(InvalidationEngine* eng, const char* key, const char* val,
                int ttl_seconds, const char* tags[], int num_tags) {
    unsigned int b = hash_str(key);
    CacheEntry* cur = eng->cache_table[b];
    while (cur) {
        if (strcmp(cur->key, key) == 0) break;
        cur = cur->next;
    }
    if (!cur) {
        cur = (CacheEntry*)malloc(sizeof(CacheEntry));
        strncpy(cur->key, key, 127);
        cur->key[127] = '\0';
        cur->next = eng->cache_table[b];
        eng->cache_table[b] = cur;
    }
    strncpy(cur->value, val, 511);
    cur->value[511] = '\0';
    cur->expires_at = time(NULL) + ttl_seconds;
    cur->lease_token = ++eng->next_lease_id;
    cur->tag_count = 0;

    for (int i = 0; i < num_tags && i < MAX_TAGS_PER_KEY; ++i) {
        strncpy(cur->tags[cur->tag_count++], tags[i], 63);
        add_key_to_tag(eng, tags[i], key);
    }
}

/* Пряме видалення одного ключа */
bool engine_del(InvalidationEngine* eng, const char* key) {
    unsigned int b = hash_str(key);
    CacheEntry** pp = &eng->cache_table[b];
    while (*pp) {
        if (strcmp((*pp)->key, key) == 0) {
            CacheEntry* victim = *pp;
            *pp = victim->next;
            free(victim);
            return true;
        }
        pp = &(*pp)->next;
    }
    return false;
}

/* Очищення всіх ключів за заданим тегом */
int engine_purge_tag(InvalidationEngine* eng, const char* tag) {
    unsigned int b = hash_str(tag);
    TagNode** pp = &eng->tag_index[b];
    while (*pp) {
        if (strcmp((*pp)->tag, tag) == 0) {
            TagNode* node = *pp;
            int purged = 0;
            for (int i = 0; i < node->key_count; ++i) {
                if (engine_del(eng, node->keys[i])) {
                    purged++;
                }
            }
            *pp = node->next;
            free(node);
            return purged;
        }
        pp = &(*pp)->next;
    }
    return 0;
}

/* Отримання актуальної епохи простору імен */
uint64_t engine_get_generation(InvalidationEngine* eng, const char* ns) {
    unsigned int b = hash_str(ns);
    NamespaceGen* cur = eng->ns_table[b];
    while (cur) {
        if (strcmp(cur->ns, ns) == 0) return cur->generation;
        cur = cur->next;
    }
    NamespaceGen* node = (NamespaceGen*)malloc(sizeof(NamespaceGen));
    strncpy(node->ns, ns, 63);
    node->ns[63] = '\0';
    node->generation = 1;
    node->next = eng->ns_table[b];
    eng->ns_table[b] = node;
    return 1;
}

/* Інкремент епохи (миттєва інвалідація простору імен за O(1)) */
uint64_t engine_bump_generation(InvalidationEngine* eng, const char* ns) {
    unsigned int b = hash_str(ns);
    NamespaceGen* cur = eng->ns_table[b];
    while (cur) {
        if (strcmp(cur->ns, ns) == 0) {
            return ++cur->generation;
        }
        cur = cur->next;
    }
    NamespaceGen* node = (NamespaceGen*)malloc(sizeof(NamespaceGen));
    strncpy(node->ns, ns, 63);
    node->ns[63] = '\0';
    node->generation = 2;
    node->next = eng->ns_table[b];
    eng->ns_table[b] = node;
    return 2;
}

void engine_free(InvalidationEngine* eng) {
    for (int i = 0; i < HASH_BUCKETS; ++i) {
        CacheEntry* ce = eng->cache_table[i];
        while (ce) { CacheEntry* n = ce->next; free(ce); ce = n; }
        TagNode* tn = eng->tag_index[i];
        while (tn) { TagNode* n = tn->next; free(tn); tn = n; }
        NamespaceGen* ng = eng->ns_table[i];
        while (ng) { NamespaceGen* n = ng->next; free(ng); ng = n; }
    }
    free(eng);
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <memory>
#include <chrono>
#include <mutex>
#include <optional>
#include <thread>
#include <functional>

struct CacheEntry {
    std::string value;
    std::chrono::steady_clock::time_point expires_at;
    uint64_t lease_token{0};
    std::vector<std::string> tags;
};

class InvalidationEngine {
public:
    // Запис значення з прив'язкою до списку тегів
    void set(std::string_view key, std::string_view value,
             std::chrono::seconds ttl, const std::vector<std::string>& tags = {}) {
        std::unique_lock<std::mutex> lock(mutex_);
        std::string k(key);
        
        CacheEntry entry;
        entry.value = std::string(value);
        entry.expires_at = std::chrono::steady_clock::now() + ttl;
        entry.lease_token = ++next_lease_id_;
        entry.tags = tags;

        // Оновлюємо інвертований індекс тегів
        for (const auto& tag : tags) {
            tag_to_keys_[tag].insert(k);
        }

        cache_[k] = std::move(entry);
    }

    // Читання значення з перевіркою TTL
    std::optional<std::string> get(std::string_view key) {
        std::unique_lock<std::mutex> lock(mutex_);
        auto it = cache_.find(std::string(key));
        if (it == cache_.end()) {
            return std::nullopt;
        }

        if (std::chrono::steady_clock::now() > it->second.expires_at) {
            erase_internal(it->first);
            return std::nullopt;
        }

        return it->second.value;
    }

    // Пряме видалення одного ключа
    bool del(std::string_view key) {
        std::unique_lock<std::mutex> lock(mutex_);
        return erase_internal(std::string(key));
    }

    // Інвалідація всіх ключів за заданим тегом
    size_t purge_tag(std::string_view tag) {
        std::unique_lock<std::mutex> lock(mutex_);
        auto it = tag_to_keys_.find(std::string(tag));
        if (it == tag_to_keys_.end()) {
            return 0;
        }

        std::unordered_set<std::string> keys_to_remove = std::move(it->second);
        tag_to_keys_.erase(it);

        size_t purged_count = 0;
        for (const auto& key : keys_to_remove) {
            if (cache_.erase(key) > 0) {
                purged_count++;
            }
        }
        return purged_count;
    }

    // Отримання поточної епохи простору імен
    uint64_t get_generation(std::string_view ns) {
        std::unique_lock<std::mutex> lock(mutex_);
        auto it = namespace_epochs_.find(std::string(ns));
        if (it == namespace_epochs_.end()) {
            namespace_epochs_[std::string(ns)] = 1;
            return 1;
        }
        return it->second;
    }

    // Інкремент епохи (O(1) інвалідація простору імен)
    uint64_t bump_generation(std::string_view ns) {
        std::unique_lock<std::mutex> lock(mutex_);
        return ++namespace_epochs_[std::string(ns)];
    }

    // Формування версійного ключа з поточною епохою
    std::string make_versioned_key(std::string_view ns, std::string_view raw_key) {
        uint64_t gen = get_generation(ns);
        return std::string(ns) + ":v" + std::to_string(gen) + ":" + std::string(raw_key);
    }

    // Відкладене подвійне видалення (Delayed Double-Delete)
    void delayed_double_delete(std::string key, std::chrono::milliseconds delay) {
        // Перше негайне видалення
        del(key);

        // Друге відкладене видалення у фоновому потоці після затримки реплікації
        std::thread([this, key = std::move(key), delay]() {
            std::this_thread::sleep_for(delay);
            this->del(key);
        }).detach();
    }

private:
    bool erase_internal(const std::string& key) {
        auto it = cache_.find(key);
        if (it == cache_.end()) {
            return false;
        }

        // Очищаємо зворотні посилання в індексі тегів
        for (const auto& tag : it->second.tags) {
            auto tag_it = tag_to_keys_.find(tag);
            if (tag_it != tag_to_keys_.end()) {
                tag_it->second.erase(key);
                if (tag_it->second.empty()) {
                    tag_to_keys_.erase(tag_it);
                }
            }
        }

        cache_.erase(it);
        return true;
    }

    std::mutex mutex_;
    std::unordered_map<std::string, CacheEntry> cache_;
    std::unordered_map<std::string, std::unordered_set<std::string>> tag_to_keys_;
    std::unordered_map<std::string, uint64_t> namespace_epochs_;
    uint64_t next_lease_id_{1000};
};
```
:::

## Тестовий сценарій: перевірка поведінки системи

Продемонструємо роботу інвертованого індексу та версійних епох у повноцінній програмі.

:::tabs
```c
int main(void) {
    InvalidationEngine* eng = engine_create();

    const char* tags_laptop[] = {"item:42", "brand:apple", "cat:laptops"};
    const char* tags_phone[]  = {"item:99", "brand:apple", "cat:phones"};
    const char* tags_catalog[] = {"cat:laptops", "page:1"};

    // Заповнюємо кеш записами з перехресними тегами
    engine_set(eng, "/product/42", "MacBook Pro M3", 300, tags_laptop, 3);
    engine_set(eng, "/product/99", "iPhone 15", 300, tags_phone, 3);
    engine_set(eng, "/catalog/laptops", "List of 20 Laptops", 300, tags_catalog, 2);

    printf("1. Інвалідація товару #42 за тегом 'item:42'...\n");
    int purged = engine_purge_tag(eng, "item:42");
    printf("   Очищено ключів: %d (очікується 1: /product/42)\n", purged);

    printf("2. Інвалідація всієї категорії за тегом 'cat:laptops'...\n");
    purged = engine_purge_tag(eng, "cat:laptops");
    printf("   Очищено ключів: %d (очікується 1: /catalog/laptops)\n", purged);

    printf("3. Тестування Generation Bumping для тенанта 'tenant_10'...\n");
    uint64_t gen1 = engine_get_generation(eng, "tenant_10");
    printf("   Початкова епоха: v%" PRIu64 "\n", gen1);
    uint64_t gen2 = engine_bump_generation(eng, "tenant_10");
    printf("   Нова епоха після O(1) скидання: v%" PRIu64 "\n", gen2);

    engine_free(eng);
    return 0;
}
```
```cpp
#include <cinttypes>

int main() {
    InvalidationEngine engine;

    // Реєструємо кешовані сторінки
    engine.set("/product/42", "MacBook Pro M3", std::chrono::seconds(300),
               {"item:42", "brand:apple", "cat:laptops"});
    engine.set("/product/99", "iPhone 15", std::chrono::seconds(300),
               {"item:99", "brand:apple", "cat:phones"});
    engine.set("/catalog/laptops", "List of 20 Laptops", std::chrono::seconds(300),
               {"cat:laptops", "page:1"});

    std::cout << "1. Інвалідація товару #42 за тегом 'item:42'...\n";
    size_t purged = engine.purge_tag("item:42");
    std::cout << "   Очищено ключів: " << purged << " (очікується 1: /product/42)\n";

    std::cout << "2. Інвалідація бренду 'brand:apple'...\n";
    purged = engine.purge_tag("brand:apple");
    std::cout << "   Очищено ключів: " << purged << " (очікується 1: /product/99)\n";

    std::cout << "3. Тестування Generation Bumping...\n";
    std::string k1 = engine.make_versioned_key("tenant_10", "settings");
    std::cout << "   Ключ до скидання: " << k1 << "\n";
    engine.bump_generation("tenant_10");
    std::string k2 = engine.make_versioned_key("tenant_10", "settings");
    std::cout << "   Ключ після O(1) скидання: " << k2 << "\n";

    return 0;
}
```
:::

## Покроковий розбір життєвого циклу запису та інвалідації

Щоб зрозуміти динаміку взаємодії між структурами даних, простежимо поведінку рушія на трьох типових фазах:

1. **Реєстрація запису з тегами:**
   Коли застосунок виконує `engine.set("/product/42", data, ttl, {"item:42", "brand:apple", "cat:laptops"})`, рушій створює запис у головній таблиці кешу. Одночасно ключ `/product/42` вставляється в три окремі множини інвертованого індексу: для тегу `item:42`, тегу `brand:apple` та тегу `cat:laptops`. Якщо запис із таким ключем уже існував, старі зв'язки розриваються до оновлення, запобігаючи накопиченню застарілих посилань.

2. **Точкове та каскадне очищення за тегом:**
   Виклик `engine.purge_tag("item:42")` знаходить відповідний вузол тегу в інвертованому індексі, вилучає множину пов'язаних ключів і виконує їх послідовне видалення з кешу. Важливо, що при видаленні кожного ключа рушій викликає внутрішній метод `erase_internal`, який автоматично очищає цей ключ з усіх інших тегів (наприклад, з `brand:apple`), після чого звільняє порожні вузли тегів. Це гарантує нульовий витік дескрипторів і пам'яті.

3. **Скидання версійної епохи за `O(1)`:**
   Для видалення всіх даних конкретного орендаря (мультиарендність / multitenancy) або всієї конфігурації замість перебору мільйонів ключів застосунок викликає `engine.bump_generation("tenant_10")`. Лічильник епохи змінюється з `1` на `2`. Усі наступні операції читання генерують запити до ключів із префіксом `tenant_10:v2:...`, що призводить до негайного промаху кешу (`CACHE_MISS`) та завантаження свіжого стану з бази даних. Старі ключі `tenant_10:v1:...` більше ніколи не будуть прочитані й спокійно вивільняться фоновим алгоритмом витіснення `LRU` або таймером `TTL`.

## Підводні камені та виробничі пастки

1. **Пам'ять інвертованого індексу та коефіцієнт розмноження зв'язків:**
   Якщо один об'єкт прив'язується до 30–50 дрібних тегів (категорія, підкатегорія, автор, місто, знижки, наявність), розмір службового індексу може перевищити розмір самого корисного навантаження (JSON/HTML). Обов'язково обмежуйте максимальну кількість тегів на один ключ і своєчасно видаляйте порожні списки тегів (`tag_to_keys_.erase()`).
2. **Асинхронний подвійний запис і надійність відкладеного видалення:**
   У навчальному прикладі друге видалення запускається через `std::thread` зі `sleep_for`. У промисловому розподіленому середовищі такий підхід неприпустимий через ризик падіння вузла застосунку під час паузи очікування. Відкладене друге видалення повинно публікуватися в надійну чергу повідомлень із підтримкою затриманої доставки (наприклад, RabbitMQ Delayed Message Exchange, Amazon SQS Delayed Queue або Redis Sorted Set зі zset-таймерами).
3. **Витіснення лічильників епох за браком пам'яті:**
   Ключ лічильника епохи простору імен (`gen:tenant_42`) повинен зберігатися в персистентному сховищі або мати конфігурацію `noeviction`. Якщо під час сплеску навантаження Redis витіснить лічильник епохи за правилом `LRU`, наступний запит ініціалізує лічильник знову значенням `1`, що призведе до катастрофічного воскресіння старих застарілих даних (zombie data).
4. **Конкуренція за блокування індексу тегів:**
   Під час глобального очищення популярного тегу (наприклад, `brand:apple`, до якого прив'язано 100 000 товарів) тривале утримання ексклюзивного м'ютекса заблокує всі операції читання й запису інших користувачів. Для великих колекцій застосовують асинхронне фонове видалення батчами (Chunked Invalidation) або перемикання версії самого тегу (Soft Tag Invalidation).
