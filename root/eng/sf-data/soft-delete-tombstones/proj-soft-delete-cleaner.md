# ⚙️ Неблокувальний батчевий очищувач та ущільнювач надгробків

Безпосереднє виконання наївного запиту `DELETE FROM table WHERE deleted_at < cutoff` над таблицею з мільйонами записів призводить до миттєвого колапсу реляційної бази даних. 

Операція спричиняє ескалацію замків на рівні сторінок, блокує конкурентні транзакції запису, вичерпує дисковий простір журналу транзакцій (WAL / Undo Log) і провокує багатогодинні затримки потокової реплікації.

Щоб виконати фізичне очищення непомітно для основної системи, застосовують алгоритм **ітеративного курсорного видалення з обмеженням розміру порції (Keyset Chunked Purge Engine)**. 

Паралельно в розподілених сховищах на базі незмінних LSM-дерев (Log-Structured Merge-tree) надгробки вимагають окремого алгоритмічного контуру злиття (Compaction), який відсікає замасковані версії даних та вчасно утилізує самі маркери видалення.

---

### Архітектура та математична модель неблокувального очищення

Головна мета алгоритму — розбити гігантську деструктивну операцію на серію мікротранзакцій фіксованого розміру, забезпечуючи постійну складність `O(log N)` для кожного кроку вибірки.

#### 1. Курсорне секвенування проти пастки зсуву (Keyset vs Offset Pagination)

Класична пагінація через `OFFSET` є непридатною для видалення великих масивів даних:

```sql
-- АНТИПАТЕРН: катастрофічна деградація O(N)
DELETE FROM accounts 
WHERE id IN (
    SELECT id FROM accounts 
    WHERE deleted_at < :cutoff 
    ORDER BY id 
    LIMIT 5000 OFFSET :offset
);
```

Коли параметр `OFFSET` досягає значення 500 000, рушій СУБД змушений зчитати з диска та просканувати в оперативній пам'яті всі 500 000 попередніх рядків лише для того, щоб відкинути їх і взяти наступні 5000. Час виконання кожної наступної ітерації зростає лінійно, перетворюючи загальну складність очищення на квадратичну `O(N²)`.

Курсорне секвенування (Keyset Pagination) запам'ятовує максимальний ідентифікатор `id`, оброблений на попередньому кроці:

```sql
-- ПАТЕРН: стабільна складність O(log N) за B-Tree індексом
DELETE FROM accounts 
WHERE id IN (
    SELECT id FROM accounts 
    WHERE id > :last_seen_id 
      AND deleted_at < :cutoff 
    ORDER BY id ASC 
    LIMIT 5000
);
```

Завдяки умові `id > :last_seen_id` оптимізатор виконує прямий спуск деревом B-Tree до потрібного листового вузла за час `O(log N)`, повністю ігноруючи вже оброблений масив даних.

#### 2. Ізоляція транзакцій та збереження горизонту MVCC

Кожен батч (наприклад, 5000 рядків) виконується у власній короткій транзакції під рівнем ізоляції `Read Committed`. 

Використання тривалих транзакцій під рівнем `Repeatable Read` або `Serializable` для фонового очищувача є грубою помилкою: стара транзакція заморожує транзакційний знімок і утримує мінімальний ідентифікатор `xmin` (горизонт MVCC), забороняючи системному процесу `VACUUM` очищати мертві кортежі по всій базі даних.

#### 3. Адаптивне дроселювання введення-виведення (I/O Throttling)

Між виконанням окремих батчів вводиться пауза (наприклад, 50–100 мс). Це дає можливість дисковому контролеру скинути накопичені сторінки на SSD, запобігає голодуванню черг введення-виведення для клієнтських операцій `INSERT/UPDATE` та дозволяє реплікам читання застосувати згенерований WAL без відставання.

---

### Алгоритм злиття надгробків LSM (LSM Tombstone Compaction)

У сховищах типу LSM (RocksDB, LevelDB, Cassandra) операція видалення створює надгробок. Під час фонового злиття двох відсортованих списків ключів (новішого рівня `L_new` та старішого рівня `L_old`) алгоритм виконує модифіковане злиття:

1. Якщо ключ присутній в обох рівнях, а на рівні `L_new` він позначений як `TOMBSTONE`, старий запис даних із `L_old` фізично знищується.
2. Сам надгробок записується у результуючий файл лише за умови, що його вік не перевищує параметр `GC_GRACE_SECONDS` (`current_timestamp - tombstone_timestamp < GC_GRACE_SECONDS`).
3. Якщо надгробок старіший за `GC_GRACE_SECONDS` і процес злиття досяг найглибшого рівня дерева (де гарантовано немає старіших дублікатів), сам надгробок також безповоротно відкидається.

---

### Повна реалізація на мовах C та C++

Нижче наведено самодостатні реалізації ітеративного курсорного очищувача та рушія злиття надгробків.

У версії на C застосовано прямий одноетапний алгоритм ущільнення масиву двома покажчиками (`read_idx` та `write_idx`), що дозволяє виконувати фізичне вивільнення слотів пам'яті на місці (In-Place Compaction) без додаткових динамічних виділень пам'яті. 

У версії на C++ використано сучасну ідіому Erase-Remove на базі `std::remove_if` та лямбда-предиката з фіксацією стану курсора, що забезпечує строгу безпеку винятків та автоматичне керування ресурсами через RAII.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BATCH_SIZE 3
#define GC_GRACE_SECONDS 864000 // 10 днів у секундах

typedef enum {
    ENTRY_DATA,
    ENTRY_TOMBSTONE
} EntryType;

typedef struct {
    int64_t id;
    int64_t timestamp;
    EntryType type;
    char key[32];
    char value[64];
} StorageRecord;

typedef struct {
    StorageRecord *records;
    size_t count;
    size_t capacity;
} StorageTable;

// Ініціалізація пам'яті для сховища
StorageTable* create_table(size_t capacity) {
    StorageTable *table = (StorageTable*)malloc(sizeof(StorageTable));
    table->records = (StorageRecord*)malloc(sizeof(StorageRecord) * capacity);
    table->count = 0;
    table->capacity = capacity;
    return table;
}

void free_table(StorageTable *table) {
    if (table) {
        free(table->records);
        free(table);
    }
}

void append_record(StorageTable *t, int64_t id, const char *key, const char *val, int64_t ts, EntryType type) {
    if (t->count >= t->capacity) return;
    StorageRecord *r = &t->records[t->count++];
    r->id = id;
    r->timestamp = ts;
    r->type = type;
    strncpy(r->key, key, sizeof(r->key) - 1);
    r->key[sizeof(r->key) - 1] = '\0';
    strncpy(r->value, val, sizeof(r->value) - 1);
    r->value[sizeof(r->value) - 1] = '\0';
}

// 1. Алгоритм неблокувального порційного видалення (Keyset Batch Purge)
size_t purge_soft_deleted_batch(StorageTable *table, int64_t cutoff_ts, int64_t *cursor_id, size_t limit) {
    size_t purged_in_batch = 0;
    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < table->count) {
        StorageRecord *r = &table->records[read_idx];

        // Якщо запис знаходиться після нашого курсора, є м'яко видаленим і старішим за cutoff
        if (r->id > *cursor_id && r->type == ENTRY_TOMBSTONE && r->timestamp < cutoff_ts && purged_in_batch < limit) {
            *cursor_id = r->id;
            purged_in_batch++;
            read_idx++; // Пропускаємо запис (фізично вивільняємо зі сховища)
        } else {
            if (write_idx != read_idx) {
                table->records[write_idx] = table->records[read_idx];
            }
            write_idx++;
            read_idx++;
        }
    }
    table->count = write_idx;
    return purged_in_batch;
}

// 2. Алгоритм злиття надгробків LSM (LSM Tombstone Compactor)
StorageTable* compact_lsm_levels(const StorageTable *level_new, const StorageTable *level_old, int64_t current_ts) {
    StorageTable *merged = create_table(level_new->count + level_old->count);
    size_t i = 0, j = 0;

    while (i < level_new->count || j < level_old->count) {
        if (i < level_new->count && j < level_old->count) {
            int cmp = strcmp(level_new->records[i].key, level_old->records[j].key);

            if (cmp == 0) {
                // Конфлікт ключів: новіший рівень перемагає старий
                if (level_new->records[i].type == ENTRY_TOMBSTONE) {
                    // Якщо це надгробок, але він ще захищений (< GC_GRACE), ми повинні його зберегти
                    if (current_ts - level_new->records[i].timestamp < GC_GRACE_SECONDS) {
                        append_record(merged, level_new->records[i].id, level_new->records[i].key,
                                      "", level_new->records[i].timestamp, ENTRY_TOMBSTONE);
                    }
                    // Якщо старіший за GC_GRACE — надгробок і старі дані повністю знищуються
                } else {
                    append_record(merged, level_new->records[i].id, level_new->records[i].key,
                                  level_new->records[i].value, level_new->records[i].timestamp, ENTRY_DATA);
                }
                i++;
                j++; // Старий запис відкинуто
            } else if (cmp < 0) {
                append_record(merged, level_new->records[i].id, level_new->records[i].key,
                              level_new->records[i].value, level_new->records[i].timestamp, level_new->records[i].type);
                i++;
            } else {
                append_record(merged, level_old->records[j].id, level_old->records[j].key,
                              level_old->records[j].value, level_old->records[j].timestamp, level_old->records[j].type);
                j++;
            }
        } else if (i < level_new->count) {
            append_record(merged, level_new->records[i].id, level_new->records[i].key,
                          level_new->records[i].value, level_new->records[i].timestamp, level_new->records[i].type);
            i++;
        } else {
            append_record(merged, level_old->records[j].id, level_old->records[j].key,
                          level_old->records[j].value, level_old->records[j].timestamp, level_old->records[j].type);
            j++;
        }
    }
    return merged;
}

int main(void) {
    StorageTable *db = create_table(10);
    append_record(db, 1, "user:1", "Alice", 100, ENTRY_DATA);
    append_record(db, 2, "user:2", "Bob", 200, ENTRY_TOMBSTONE); // М'яко видалений
    append_record(db, 3, "user:3", "Charlie", 300, ENTRY_DATA);
    append_record(db, 4, "user:4", "David", 250, ENTRY_TOMBSTONE); // М'яко видалений

    int64_t cursor = 0;
    int64_t cutoff = 500;
    size_t batch = 0;

    printf("Початок батчевого очищення сховища...\n");
    while (true) {
        size_t deleted = purge_soft_deleted_batch(db, cutoff, &cursor, 2);
        if (deleted == 0) break;
        batch++;
        printf("Батч #%zu: успішно видалено %zu записів. Курсор id=%lld\n", batch, deleted, (long long)cursor);
    }

    printf("Залишилося живих записів у таблиці: %zu\n", db->count);
    free_table(db);
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <algorithm>
#include <cstdint>

enum class EntryType {
    Data,
    Tombstone
};

struct StorageRecord {
    int64_t id;
    int64_t timestamp;
    EntryType type;
    std::string key;
    std::string value;
};

class StorageTable {
public:
    void append(int64_t id, std::string_view key, std::string_view value, int64_t ts, EntryType type) {
        records_.push_back({id, ts, type, std::string(key), std::string(value)});
    }

    [[nodiscard]] size_t size() const noexcept { return records_.size(); }
    [[nodiscard]] const std::vector<StorageRecord>& records() const noexcept { return records_; }

    // 1. Keyset Batch Purge: ітеративне видалення застарілих надгробків (Erase-Remove Idiom)
    size_t purge_batch(int64_t cutoff_ts, int64_t& cursor_id, size_t limit) {
        size_t purged_count = 0;

        auto it = std::remove_if(records_.begin(), records_.end(), [&](const StorageRecord& r) {
            if (r.id > cursor_id && r.type == EntryType::Tombstone && r.timestamp < cutoff_ts && purged_count < limit) {
                cursor_id = r.id;
                ++purged_count;
                return true; // Фізично видаляємо з пам'яті
            }
            return false;
        });

        records_.erase(it, records_.end());
        return purged_count;
    }

    // 2. LSM Tombstone Compaction: злиття рівнів з урахуванням часу життя надгробка
    static StorageTable compact_levels(const StorageTable& level_new, 
                                       const StorageTable& level_old, 
                                       int64_t current_ts, 
                                       int64_t gc_grace_seconds = 864000) {
        StorageTable merged;
        size_t i = 0, j = 0;
        const auto& recs_new = level_new.records();
        const auto& recs_old = level_old.records();

        while (i < recs_new.size() || j < recs_old.size()) {
            if (i < recs_new.size() && j < recs_old.size()) {
                if (recs_new[i].key == recs_old[j].key) {
                    // Конфлікт ключів: новіший запис поглинає старий
                    if (recs_new[i].type == EntryType::Tombstone) {
                        // Якщо надгробок ще захищений grace period, зберігаємо його
                        if (current_ts - recs_new[i].timestamp < gc_grace_seconds) {
                            merged.append(recs_new[i].id, recs_new[i].key, "", recs_new[i].timestamp, EntryType::Tombstone);
                        }
                    } else {
                        merged.append(recs_new[i].id, recs_new[i].key, recs_new[i].value, recs_new[i].timestamp, EntryType::Data);
                    }
                    ++i;
                    ++j; // Старий запис повністю відкинуто
                } else if (recs_new[i].key < recs_old[j].key) {
                    merged.append(recs_new[i].id, recs_new[i].key, recs_new[i].value, recs_new[i].timestamp, recs_new[i].type);
                    ++i;
                } else {
                    merged.append(recs_old[j].id, recs_old[j].key, recs_old[j].value, recs_old[j].timestamp, recs_old[j].type);
                    ++j;
                }
            } else if (i < recs_new.size()) {
                merged.append(recs_new[i].id, recs_new[i].key, recs_new[i].value, recs_new[i].timestamp, recs_new[i].type);
                ++i;
            } else {
                merged.append(recs_old[j].id, recs_old[j].key, recs_old[j].value, recs_old[j].timestamp, recs_old[j].type);
                ++j;
            }
        }
        return merged;
    }

private:
    std::vector<StorageRecord> records_;
};

int main() {
    StorageTable db;
    db.append(1, "user:1", "Alice", 100, EntryType::Data);
    db.append(2, "user:2", "Bob", 200, EntryType::Tombstone);
    db.append(3, "user:3", "Charlie", 300, EntryType::Data);
    db.append(4, "user:4", "David", 250, EntryType::Tombstone);

    int64_t cursor = 0;
    const int64_t cutoff = 500;
    size_t batch = 0;

    std::cout << "Початок батчевого очищення таблиці...\n";
    while (true) {
        size_t deleted = db.purge_batch(cutoff, cursor, 2);
        if (deleted == 0) break;
        ++batch;
        std::cout << "Батч #" << batch << ": успішно видалено " << deleted 
                  << " записів. Курсор id=" << cursor << "\n";
    }

    std::cout << "Залишилося живих записів у таблиці: " << db.size() << "\n";
    return 0;
}
```
:::

---

### Аналіз інженерних пасток та виробничих збоїв

1. **Конфлікти блокувань зовнішніх ключів (Foreign Key Deadlocks):** Якщо таблиця, з якої видаляються дані, має дочірні зв'язки без створеного індексу за стовпцем зовнішнього ключа, кожен оператор `DELETE` ініціює повне послідовне сканування (Sequential Scan) дочірньої таблиці зі спільним блокуванням. Це миттєво викликає взаємні блокування (Deadlocks) із клієнтськими транзакціями вставки нових замовлень.
2. **Аномалія воскресіння в LSM (LSM Ghost Resurrection):** Якщо під час злиття SSTable рівня L0 з рівнем L1 надгробок буде знищено лише тому, що він збігся з записом у L1, але при цьому старіший дублікат цього ключа все ще лежить на рівні L2, старі дані спливуть назад під час наступного читання. Надгробок дозволено знищувати лише тоді, коли він опустився на найглибший рівень дерева (L_max), або коли всі SSTable старіших рівнів гарантовано не перетинаються з діапазоном ключів цього надгробка.
3. **Засмічення буферного пулу (Buffer Pool Thrashing):** Якщо для пошуку застарілих записів не використовується частковий індекс `WHERE deleted_at IS NOT NULL`, фоновий процес вичитує гігабайти холодних сторінок у пам'ять, витісняючи з кешу оперативні гарячі індекси бізнес-транзакцій.
4. **Метрики спостережуваності очищувача:** Виробничий контур зобов'язаний збирати три ключові показники: швидкість видалення (`rows_purged_per_second`), обсяг згенерованого журналу транзакцій (`wal_bytes_per_batch`) та середній час очікування блокувань (`lock_wait_ms`), що дозволяє динамічно адаптувати розмір батчу під поточне навантаження на систему.
