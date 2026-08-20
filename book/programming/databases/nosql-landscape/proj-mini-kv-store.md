# ⚙️ Розробка міні-NoSQL сховища: Key-Value та Append-Only Log

Рушії Key-Value сховищ (таких як Bitcask, Redis або RocksDB) поєднують простоту інтерфейсу з колосальною пропускною здатністю завдяки використанню виключно послідовного запису на диск (Append-Only Log) та утриманню індексу зміщень у оперативній пам'яті.

У цьому практичному проєкті ми розробимо повноцінний мініатюрний Key-Value рушій мовами C та C++, побудований за архітектурою Bitcask: операції `SET` та `DELETE` дописуються в кінець журналу, а операція `GET` знаходить зміщення файлу через хеш-таблицю в пам'яті за константний час `O(1)`.

---

### Архітектура системи та формат бінарного журналу

Кожен запис у файлі журналу (`data.db`) серіалізується у бінарному форматі:

```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────────┐
│ Timestamp    │ Key Size     │ Value Size   │ Key Bytes    │ Value Bytes      │
│ (8 bytes)    │ (2 bytes)    │ (4 bytes)    │ (K bytes)    │ (V bytes)        │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────────┘
```

1. **Журнал на диску (`data.db`)**: Файл, куди всі операції записуються строго послідовно (Sequential Write), що максимізує швидкість дискового вводу-виводу.
2. **Індекс у пам'яті (`KeyDir`)**: Хеш-таблиця, що зіставляє ключ сутності зі структурою `RecordOffset { file_id, value_pos, value_sz, timestamp }`.
3. **Видалення сутностей (Tombstones)**: Видалення записується у файл як спеціальне значення нульової довжини (Tombstone), що видаляє ключ з індексу в пам'яті.
4. **Ущільнення (Compaction)**: Фоновий процес, який зливає старі записи та видаляє перезаписані значення, вивільняючи дисковий простір.

---

### Повна реалізація мовами C та C++

Нижче наведено вихідний код рушія, написаний за стандартами C99 та C++17 без сторонніх залежностей.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_ENTRIES 1024
#define MAX_KEY_LEN 64
#define MAX_VAL_LEN 256
#define DB_FILENAME "mini_kv_data.db"

#pragma pack(push, 1)
typedef struct {
    uint64_t timestamp;
    uint16_t key_len;
    uint32_t val_len;
} record_header_t;
#pragma pack(pop)

typedef struct {
    char key[MAX_KEY_LEN];
    long file_offset;
    uint32_t val_len;
} keydir_entry_t;

typedef struct {
    keydir_entry_t entries[MAX_ENTRIES];
    size_t count;
    FILE *db_file;
} kv_store_t;

int kv_init(kv_store_t *store) {
    store->count = 0;
    store->db_file = fopen(DB_FILENAME, "a+b");
    if (!store->db_file) return -1;
    return 0;
}

int kv_set(kv_store_t *store, const char *key, const char *value) {
    uint16_t klen = (uint16_t)strlen(key);
    uint32_t vlen = (uint32_t)strlen(value);

    fseek(store->db_file, 0, SEEK_END);
    long record_offset = ftell(store->db_file);

    record_header_t hdr;
    hdr.timestamp = (uint64_t)time(NULL);
    hdr.key_len = klen;
    hdr.val_len = vlen;

    // 1. Послідовний запис у журнал (Append-Only)
    fwrite(&hdr, sizeof(record_header_t), 1, store->db_file);
    fwrite(key, 1, klen, store->db_file);
    fwrite(value, 1, vlen, store->db_file);
    fflush(store->db_file);

    // 2. Оновлення індексу в пам'яті (KeyDir)
    long val_offset = record_offset + sizeof(record_header_t) + klen;

    for (size_t i = 0; i < store->count; ++i) {
        if (strcmp(store->entries[i].key, key) == 0) {
            store->entries[i].file_offset = val_offset;
            store->entries[i].val_len = vlen;
            return 0;
        }
    }

    if (store->count < MAX_ENTRIES) {
        strncpy(store->entries[store->count].key, key, MAX_KEY_LEN - 1);
        store->entries[store->count].file_offset = val_offset;
        store->entries[store->count].val_len = vlen;
        store->count++;
    }

    return 0;
}

int kv_get(kv_store_t *store, const char *key, char *out_val, size_t max_out) {
    for (size_t i = 0; i < store->count; ++i) {
        if (strcmp(store->entries[i].key, key) == 0) {
            long offset = store->entries[i].file_offset;
            uint32_t vlen = store->entries[i].val_len;

            if (vlen >= max_out) return -2; // Буфер замалий

            fseek(store->db_file, offset, SEEK_SET);
            fread(out_val, 1, vlen, store->db_file);
            out_val[vlen] = '\0';
            return 0;
        }
    }
    return -1; // Ключ не знайдено
}

int kv_delete(kv_store_t *store, const char *key) {
    // Запис маркеру видалення (Tombstone з довжиною значення 0)
    uint16_t klen = (uint16_t)strlen(key);
    record_header_t hdr;
    hdr.timestamp = (uint64_t)time(NULL);
    hdr.key_len = klen;
    hdr.val_len = 0; // Маркер Tombstone

    fseek(store->db_file, 0, SEEK_END);
    fwrite(&hdr, sizeof(record_header_t), 1, store->db_file);
    fwrite(key, 1, klen, store->db_file);
    fflush(store->db_file);

    // Видалення з індексу KeyDir
    for (size_t i = 0; i < store->count; ++i) {
        if (strcmp(store->entries[i].key, key) == 0) {
            store->entries[i] = store->entries[store->count - 1];
            store->count--;
            return 0;
        }
    }
    return -1;
}

void kv_close(kv_store_t *store) {
    if (store->db_file) {
        fclose(store->db_file);
        store->db_file = NULL;
    }
}
```
@tab C++
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <chrono>
#include <vector>
#include <optional>

namespace mini_nosql {

struct KeyDirEntry {
    std::streampos value_offset;
    uint32_t value_size;
    uint64_t timestamp;
};

class MiniKVStore {
public:
    explicit MiniKVStore(const std::string& filename) : filename_(filename) {
        file_.open(filename_, std::ios::in | std::ios::out | std::ios::binary | std::ios::app);
        if (!file_.is_open()) {
            // Створення файлу, якщо не існує
            file_.open(filename_, std::ios::out | std::ios::binary);
            file_.close();
            file_.open(filename_, std::ios::in | std::ios::out | std::ios::binary | std::ios::app);
        }
    }

    ~MiniKVStore() {
        if (file_.is_open()) {
            file_.close();
        }
    }

    void set(const std::string& key, const std::string& value) {
        file_.seekp(0, std::ios::end);
        std::streampos record_pos = file_.tellp();

        uint64_t ts = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        uint16_t klen = static_cast<uint16_t>(key.size());
        uint32_t vlen = static_cast<uint32_t>(value.size());

        // Запис заголовка та даних строго послідовно
        file_.write(reinterpret_cast<const char*>(&ts), sizeof(ts));
        file_.write(reinterpret_cast<const char*>(&klen), sizeof(klen));
        file_.write(reinterpret_cast<const char*>(&vlen), sizeof(vlen));
        file_.write(key.data(), klen);
        file_.write(value.data(), vlen);
        file_.flush();

        std::streampos val_pos = record_pos + static_cast<std::streamoff>(sizeof(ts) + sizeof(klen) + sizeof(vlen) + klen);

        // Оновлення індексу в пам'яті
        keydir_[key] = {val_pos, vlen, ts};
    }

    std::optional<std::string> get(const std::string& key) {
        auto it = keydir_.find(key);
        if (it == keydir_.end()) {
            return std::nullopt;
        }

        file_.seekg(it->second.value_offset);
        std::string result(it->second.value_size, '\0');
        file_.read(&result[0], it->second.value_size);

        return result;
    }

    bool remove(const std::string& key) {
        auto it = keydir_.find(key);
        if (it == keydir_.end()) return false;

        file_.seekp(0, std::ios::end);
        uint64_t ts = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        uint16_t klen = static_cast<uint16_t>(key.size());
        uint32_t vlen = 0; // Tombstone

        file_.write(reinterpret_cast<const char*>(&ts), sizeof(ts));
        file_.write(reinterpret_cast<const char*>(&klen), sizeof(klen));
        file_.write(reinterpret_cast<const char*>(&vlen), sizeof(vlen));
        file_.write(key.data(), klen);
        file_.flush();

        keydir_.erase(it);
        return true;
    }

private:
    std::string filename_;
    std::fstream file_;
    std::unordered_map<std::string, KeyDirEntry> keydir_;
};

} // namespace mini_nosql
```
:::

---

### Інженерний аналіз та переваги архітектури Bitcask

1. **Висока швидкість запису (Sequential I/O)**: Додавання нових даних відбувається без випадкового переміщення головок HDD чи блоків SSD (Random Writes). Запис виконується зі швидкістю пропускної здатності дискової шини.
2. **Константна швидкість читання O(1)**: Пошук за ключем не потребує обходу B-Tree чи читання кількох блоків індексів; адреса значення знаходиться в один крок через хеш-таблицю `KeyDir`.
3. **Швидке відновлення після аварій (Crash Recovery)**: У разі раптового збою живлення цілісність даних не порушується, оскільки старі записи залишаються незмінними в журналі, а неповний останній запис відсікається під час валідації довжини.
4. **Процедура фонового злиття (Compaction & Merge)**: Оскільки старі значення ключів накопичуються в журналі, періодично запускається фоновий потік, який читає `data.db`, відфільтровує застарілі та видалені Tombstone-записи і записує компактний новий файл, перемикаючи активний файловий дескриптор.
5. **Обмеження моделі**: Усі ключі зобов'язані вміщатися в оперативну пам'ять (RAM). Якщо обсяг ключів перевищує розмір пам'яті, переходять до архітектур **LSM-Tree** (RocksDB, LevelDB) зі зберіганням розріджених індексів на диску.
6. **Контроль цілісності через CRC32**: У промислових реалізаціях заголовок кожного запису містить 4-байтну контрольну суму CRC32 для виявлення апаратного пошкодження секторів накопичувача під час читання.
7. **Асинхронний дисковий злив (fsync strategy)**: Для досягнення балансу між надійністю та швидкістю виклик `fsync()` можна виконувати не на кожен запит, а періодично (раз на 1 секунду, як у Redis `appendfsync everysec`), що знижує навантаження на підсистему вводу-виводу ціною потенційної втрати 1 секунди останніх транзакцій при аварії живлення.
8. **Підтримка блокувань читачів та письменників (RWLock)**: Одночасне читання багатьма потоками виконується паралельно без блокувань (Lock-Free або Shared Lock), тоді як операція запису `SET` блокує файл лише на час переміщення файлового вказівника та додавання байтів у кінець файлу.
9. **Формування Hint-файлів для миттєвого старту**: Під час злиття (Merge) рушій додатково генерує бінарний файл підказок `.hint`, який містить копію структури `KeyDir` на диску. При перезапуску процесу замість читання гігабайтів журналу даних рушій за частки секунди завантажує `.hint` у пам'ять.
10. **Ізоляція пам'яті та Memory-Mapped I/O (mmap)**: Для виключення зайвого копіювання байтів між простором ядра (Kernel Space) та простором користувача (User Space) читання файлів журналу можна реалізувати через системний виклик `mmap()`.
11. **Шардування індексу в пам'яті (Concurrent Partitioned Map)**: При роботі з сотнями мільйонів ключів єдина хеш-таблиця `KeyDir` розбивається на 32 або 64 незалежні шарди (Bucket Partitioning) з окремими м'ютексами для усунення блокувального суперництва між робочими потоками процесу.
12. **Стиснення даних на льоту (Snappy / LZ4 Compression)**: Для економії дискового простору значення перед записом у файл стискаються швидкими потоковими алгоритмами, а в заголовку прапорцем відзначається тип стиснення.
13. **Ротація файлів журналів (Log Segment Segmentation)**: При досягненні файлом розміру 1–2 ГБ поточний сегмент переводиться в режим тільки для читання (Immutable Read-Only), а для нових записів відкривається новий активний сегмент із монотонно зростаючим числовим ідентифікатором.
14. **Гарантії атомарності пакетного запису (Atomic Multi-Set Batching)**: Запис декількох ключів у межах однієї транзакції огортається спільним маркером пакету (Batch Header) з кількістю операцій, гарантуючи, що клієнт побачить або всі оновлені ключі одночасно, або жодного при раптовому збої.
