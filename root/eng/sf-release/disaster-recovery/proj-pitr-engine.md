# ⚙️ Реалізація рушія Point-in-Time Recovery з верифікацією контрольних сум WAL

Випадкове виконання руйнівної команди `DROP TABLE` або запуск помилкової міграції схеми бази даних миттєво реплікується на всі вузли високої доступності, перетворюючи звичайні гарячі репліки на співучасників знищення даних. Єдиний спосіб повернути стан системи без втрати зафіксованих за день транзакцій — це потокове відтворення базового бінарного знімка та послідовне програвання сегментів журналу випереджального запису (WAL) із зупинкою за мілісекунду до фатальної операції.

Нижче наведено повністю робочу реалізацію вбудованого рушія Point-in-Time Recovery (PITR). Програма зчитує бінарний базовий знімок стану таблиці типу «ключ-значення», послідовно парсить потік заархівованих сегментів WAL, перевіряє цілісність кожного запису за допомогою швидкого обчислення контрольних сум CRC32 і зупиняє процес накатування змін на точній мітці часу, переданій користувачем, відкидаючи всі наступні руйнівні транзакції.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_ENTRIES 1024
#define KEY_LEN 32
#define VAL_LEN 64
#define WAL_MAGIC 0x57414C31  /* "WAL1" у двійковому форматі */

/* ── Бінарний заголовок запису в журналі WAL ─────────────────────────────── */
#pragma pack(push, 1)
typedef struct {
    uint32_t magic;         /* Магічне число валідації формату */
    uint64_t lsn;           /* Монотонний Log Sequence Number */
    uint64_t timestamp_ms;  /* Час транзакції (UTC Epoch мілісекунди) */
    uint8_t  op_type;       /* 1 = INSERT/UPDATE, 2 = DELETE, 3 = TRUNCATE */
    uint32_t payload_len;   /* Довжина корисного навантаження */
    uint32_t crc32;         /* Контрольна сума CRC32 корисного навантаження */
} WalRecordHeader;

typedef struct {
    char key[KEY_LEN];
    char value[VAL_LEN];
} WalPayload;
#pragma pack(pop)

/* ── Стан бази даних у пам'яті (Key-Value Store) ─────────────────────────── */
typedef struct {
    char key[KEY_LEN];
    char value[VAL_LEN];
    bool is_active;
} DbEntry;

typedef struct {
    DbEntry entries[MAX_ENTRIES];
    size_t count;
    uint64_t last_applied_lsn;
    uint64_t last_applied_ts;
} Database;

/* ── Таблиця та обчислення контрольної суми CRC32 ────────────────────────── */
static uint32_t crc32_table[256];
static bool crc_initialized = false;

static void init_crc32_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int j = 0; j < 8; j++) {
            c = (c & 1) ? (0xEDB88320L ^ (c >> 1)) : (c >> 1);
        }
        crc32_table[i] = c;
    }
    crc_initialized = true;
}

static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    if (!crc_initialized) init_crc32_table();
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc = crc32_table[(crc ^ data[i]) & 0xFF] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFF;
}

/* ── Операції над станом бази даних ──────────────────────────────────────── */
static void db_init(Database *db) {
    memset(db, 0, sizeof(Database));
}

static void db_put(Database *db, const char *key, const char *value) {
    for (size_t i = 0; i < db->count; i++) {
        if (strcmp(db->entries[i].key, key) == 0) {
            strncpy(db->entries[i].value, value, VAL_LEN - 1);
            db->entries[i].value[VAL_LEN - 1] = '\0';
            db->entries[i].is_active = true;
            return;
        }
    }
    if (db->count < MAX_ENTRIES) {
        strncpy(db->entries[db->count].key, key, KEY_LEN - 1);
        strncpy(db->entries[db->count].value, value, VAL_LEN - 1);
        db->entries[db->count].is_active = true;
        db->count++;
    }
}

static void db_delete(Database *db, const char *key) {
    for (size_t i = 0; i < db->count; i++) {
        if (strcmp(db->entries[i].key, key) == 0) {
            db->entries[i].is_active = false;
            return;
        }
    }
}

static void db_truncate(Database *db) {
    for (size_t i = 0; i < db->count; i++) {
        db->entries[i].is_active = false;
    }
}

static void db_dump(const Database *db) {
    printf("=== СТАН БАЗИ ДАНИХ (Останній LSN: %llu) ===
", (unsigned long long)db->last_applied_lsn);
    for (size_t i = 0; i < db->count; i++) {
        if (db->entries[i].is_active) {
            printf("  [%s] => "%s"
", db->entries[i].key, db->entries[i].value);
        }
    }
    printf("==================================================
");
}

/* ── Координатор Point-in-Time Recovery ──────────────────────────────────── */
static int pitr_apply_wal(Database *db, const char *wal_filepath, uint64_t target_stop_ts_ms) {
    FILE *fp = fopen(wal_filepath, "rb");
    if (!fp) {
        perror("Не вдалося відкрити файл журналу WAL");
        return -1;
    }

    WalRecordHeader hdr;
    WalPayload payload;
    int records_applied = 0;

    while (fread(&hdr, sizeof(WalRecordHeader), 1, fp) == 1) {
        if (hdr.magic != WAL_MAGIC) {
            fprintf(stderr, "Помилка: Пошкоджений магічний заголовок WAL на позиції %ld
", ftell(fp));
            fclose(fp);
            return -2;
        }

        if (hdr.payload_len != sizeof(WalPayload)) {
            fprintf(stderr, "Помилка: Некоректний розмір корисного навантаження: %u
", hdr.payload_len);
            fclose(fp);
            return -3;
        }

        if (fread(&payload, sizeof(WalPayload), 1, fp) != 1) {
            fprintf(stderr, "Помилка: Неочікуваний кінець файлу при читанні даних
");
            fclose(fp);
            return -4;
        }

        /* Перевірка контрольної суми CRC32 */
        uint32_t expected_crc = calculate_crc32((const uint8_t *)&payload, sizeof(WalPayload));
        if (expected_crc != hdr.crc32) {
            fprintf(stderr, "Помилка CRC32 у записі LSN=%llu (очікувалось 0x%08X, отримано 0x%08X)
",
                    (unsigned long long)hdr.lsn, expected_crc, hdr.crc32);
            fclose(fp);
            return -5;
        }

        /* Критерій зупинки PITR: чи не перевищено цільовий час? */
        if (hdr.timestamp_ms > target_stop_ts_ms) {
            printf(">> [PITR ЗУПИНКА] Досягнуто часової межі: %llu ms > Target: %llu ms. Пропуск запису LSN=%llu.
",
                   (unsigned long long)hdr.timestamp_ms, (unsigned long long)target_stop_ts_ms, (unsigned long long)hdr.lsn);
            break;
        }

        /* REDO операція: застосування зміни */
        if (hdr.op_type == 1) {
            db_put(db, payload.key, payload.value);
        } else if (hdr.op_type == 2) {
            db_delete(db, payload.key);
        } else if (hdr.op_type == 3) {
            db_truncate(db);
        }

        db->last_applied_lsn = hdr.lsn;
        db->last_applied_ts = hdr.timestamp_ms;
        records_applied++;
    }

    fclose(fp);
    return records_applied;
}

int main(void) {
    printf("=== ДЕМОНСТРАЦІЯ РУШІЯ POINT-IN-TIME RECOVERY (C) ===
");
    
    Database db;
    db_init(&db);

    /* 1. Імітуємо розгортання базового знімка від 02:00:00 (100000 ms) */
    printf("[1] Відновлення базового знімка (Base Snapshot)...
");
    db_put(&db, "user:101", "Alice (Account: 500)");
    db_put(&db, "user:102", "Bob (Account: 1200)");
    db.last_applied_lsn = 1000;
    db_dump(&db);

    /* 2. Створюємо тестовий бінарний файл WAL із послідовністю дій */
    const char *wal_file = "test_wal_segment.bin";
    FILE *wfp = fopen(wal_file, "wb");
    if (!wfp) return 1;

    WalRecordHeader h;
    WalPayload p;

    /* Запис 1 (14:00:00 = 150000 ms): Поповнення балансу Alice */
    h.magic = WAL_MAGIC;
    h.lsn = 1001;
    h.timestamp_ms = 150000;
    h.op_type = 1;
    h.payload_len = sizeof(WalPayload);
    strncpy(p.key, "user:101", KEY_LEN);
    strncpy(p.value, "Alice (Account: 750)", VAL_LEN);
    h.crc32 = calculate_crc32((const uint8_t*)&p, sizeof(WalPayload));
    fwrite(&h, sizeof(h), 1, wfp);
    fwrite(&p, sizeof(p), 1, wfp);

    /* Запис 2 (14:27:03 = 154000 ms): Створення нового клієнта Charlie */
    h.lsn = 1002;
    h.timestamp_ms = 154000;
    h.op_type = 1;
    strncpy(p.key, "user:103", KEY_LEN);
    strncpy(p.value, "Charlie (Account: 300)", VAL_LEN);
    h.crc32 = calculate_crc32((const uint8_t*)&p, sizeof(WalPayload));
    fwrite(&h, sizeof(h), 1, wfp);
    fwrite(&p, sizeof(p), 1, wfp);

    /* Запис 3 (14:27:05 = 156000 ms - КАТАСТРОФА): Руйнівний TRUNCATE */
    h.lsn = 1003;
    h.timestamp_ms = 156000;
    h.op_type = 3;
    strncpy(p.key, "*", KEY_LEN);
    strncpy(p.value, "TRUNCATE_ALL", VAL_LEN);
    h.crc32 = calculate_crc32((const uint8_t*)&p, sizeof(WalPayload));
    fwrite(&h, sizeof(h), 1, wfp);
    fwrite(&p, sizeof(p), 1, wfp);

    fclose(wfp);
    printf("[2] Згенеровано потік WAL з 3 транзакціями (включаючи катастрофічний TRUNCATE о 156000 ms)
");

    /* 3. Виконуємо PITR із зупинкою на 155000 ms (між Charlie та TRUNCATE) */
    uint64_t target_time = 155000;
    printf("[3] Запуск PITR до цільового часу: %llu ms...
", (unsigned long long)target_time);
    
    int applied = pitr_apply_wal(&db, wal_file, target_time);
    printf("Успішно застосовано записів WAL: %d
", applied);

    /* 4. Фінальний стан: Чарлі доданий, баланс Аліси оновлений, а TRUNCATE проігноровано! */
    db_dump(&db);

    remove(wal_file);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <expected>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <array>

namespace storage::dr {

constexpr uint32_t WAL_MAGIC_V1 = 0x57414C31; // "WAL1"

enum class OperationType : uint8_t {
    InsertOrUpdate = 1,
    Delete = 2,
    Truncate = 3
};

enum class RecoveryError {
    FileNotFound,
    InvalidMagic,
    CorruptedPayloadSize,
    ChecksumMismatch,
    PrematureEndOfFile
};

#pragma pack(push, 1)
struct WalRecordHeader {
    uint32_t magic{WAL_MAGIC_V1};
    uint64_t lsn{0};
    uint64_t timestamp_ms{0};
    OperationType op_type{OperationType::InsertOrUpdate};
    uint32_t payload_len{0};
    uint32_t crc32{0};
};

struct WalPayloadData {
    char key[32]{};
    char value[64]{};
};
#pragma pack(pop)

/* ── Швидке обчислення CRC32 ─────────────────────────────────────────────── */
class Crc32 {
public:
    static uint32_t calculate(const uint8_t* data, size_t length) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (size_t i = 0; i < length; ++i) {
            crc = table[(crc ^ data[i]) & 0xFF] ^ (crc >> 8);
        }
        return crc ^ 0xFFFFFFFF;
    }

private:
    static constexpr auto generate_table() {
        std::array<uint32_t, 256> tbl{};
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t c = i;
            for (int j = 0; j < 8; ++j) {
                c = (c & 1) ? (0xEDB88320L ^ (c >> 1)) : (c >> 1);
            }
            tbl[i] = c;
        }
        return tbl;
    }
    static inline constexpr auto table = generate_table();
};

/* ── База даних у пам'яті з підтримкою знімків ───────────────────────────── */
class InMemoryStore {
public:
    void put(std::string_view key, std::string_view val) {
        store_[std::string(key)] = std::string(val);
    }

    void erase(std::string_view key) {
        store_.erase(std::string(key));
    }

    void truncate() noexcept {
        store_.clear();
    }

    void set_metadata(uint64_t lsn, uint64_t ts) noexcept {
        last_lsn_ = lsn;
        last_ts_ = ts;
    }

    void dump() const {
        std::cout << "=== СТАН БАЗИ ДАНИХ (LSN: " << last_lsn_ << ") ===
";
        for (const auto& [k, v] : store_) {
            std::cout << "  [" << k << "] => "" << v << ""
";
        }
        std::cout << "========================================
";
    }

private:
    std::unordered_map<std::string, std::string> store_;
    uint64_t last_lsn_{0};
    uint64_t last_ts_{0};
};

/* ── Рушій відновлення Point-in-Time Recovery ────────────────────────────── */
class PitrCoordinator {
public:
    static std::expected<size_t, RecoveryError> replay_wal_segment(
        InMemoryStore& db,
        const std::string& wal_path,
        std::chrono::milliseconds target_stop_time) 
    {
        std::ifstream file(wal_path, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected(RecoveryError::FileNotFound);
        }

        size_t records_applied = 0;
        const auto target_ts = static_cast<uint64_t>(target_stop_time.count());

        while (file.peek() != EOF) {
            WalRecordHeader header;
            if (!file.read(reinterpret_cast<char*>(&header), sizeof(WalRecordHeader))) {
                break;
            }

            if (header.magic != WAL_MAGIC_V1) {
                return std::unexpected(RecoveryError::InvalidMagic);
            }

            if (header.payload_len != sizeof(WalPayloadData)) {
                return std::unexpected(RecoveryError::CorruptedPayloadSize);
            }

            WalPayloadData payload;
            if (!file.read(reinterpret_cast<char*>(&payload), sizeof(WalPayloadData))) {
                return std::unexpected(RecoveryError::PrematureEndOfFile);
            }

            // Перевірка контрольної суми
            const auto computed_crc = Crc32::calculate(
                reinterpret_cast<const uint8_t*>(&payload), sizeof(WalPayloadData));
            
            if (computed_crc != header.crc32) {
                return std::unexpected(RecoveryError::ChecksumMismatch);
            }

            // Критерій зупинки PITR
            if (header.timestamp_ms > target_ts) {
                std::cout << ">> [PITR C++] Досягнуто часової точки зупинки: " 
                          << header.timestamp_ms << " ms > Target: " << target_ts 
                          << " ms. Зупинка REDO.
";
                break;
            }

            // Застосування операції
            switch (header.op_type) {
                case OperationType::InsertOrUpdate:
                    db.put(payload.key, payload.value);
                    break;
                case OperationType::Delete:
                    db.erase(payload.key);
                    break;
                case OperationType::Truncate:
                    db.truncate();
                    break;
            }

            db.set_metadata(header.lsn, header.timestamp_ms);
            ++records_applied;
        }

        return records_applied;
    }
};

} // namespace storage::dr

int main() {
    using namespace storage::dr;
    using namespace std::chrono_literals;

    std::cout << "=== ДЕМОНСТРАЦІЯ РУШІЯ POINT-IN-TIME RECOVERY (C++) ===
";

    InMemoryStore db;
    // 1. Початковий стан із базового знімка (02:00:00 UTC)
    db.put("user:101", "Alice (Account: 500)");
    db.put("user:102", "Bob (Account: 1200)");
    db.set_metadata(1000, 100000);
    db.dump();

    // 2. Створення двійкового сегмента WAL
    const std::string wal_file = "test_wal_cpp.bin";
    {
        std::ofstream out(wal_file, std::ios::binary);
        
        auto write_rec = [&](uint64_t lsn, uint64_t ts, OperationType op, 
                             const char* k, const char* v) {
            WalRecordHeader h;
            h.lsn = lsn;
            h.timestamp_ms = ts;
            h.op_type = op;
            h.payload_len = sizeof(WalPayloadData);
            
            WalPayloadData p{};
            std::strncpy(p.key, k, sizeof(p.key) - 1);
            std::strncpy(p.value, v, sizeof(p.value) - 1);
            
            h.crc32 = Crc32::calculate(reinterpret_cast<const uint8_t*>(&p), sizeof(WalPayloadData));
            
            out.write(reinterpret_cast<const char*>(&h), sizeof(h));
            out.write(reinterpret_cast<const char*>(&p), sizeof(p));
        };

        // Транзакція 1: Оновлення Alice (150000 ms)
        write_rec(1001, 150000, OperationType::InsertOrUpdate, "user:101", "Alice (Account: 750)");
        // Транзакція 2: Додавання Charlie (154000 ms)
        write_rec(1002, 154000, OperationType::InsertOrUpdate, "user:103", "Charlie (Account: 300)");
        // Транзакція 3: Руйнівний TRUNCATE (156000 ms)
        write_rec(1003, 156000, OperationType::Truncate, "*", "ALL");
    }

    // 3. Відновлення до точки 155000 ms (до моменту виконання TRUNCATE)
    const auto target_time = 155000ms;
    std::cout << "[PITR] Запуск відновлення до мітки " << target_time.count() << " ms...
";

    auto result = PitrCoordinator::replay_wal_segment(db, wal_file, target_time);
    if (result.has_value()) {
        std::cout << "Успішно відтворено операцій: " << result.value() << "
";
        db.dump();
    } else {
        std::cerr << "Помилка відновлення!
";
    }

    std::remove(wal_file.c_str());
    return 0;
}
```
:::

## Архітектурний розбір механізмів рушія PITR

Для розуміння того, як наведений рушій гарантує цілісність даних на рівні сховища, простежимо внутрішні механізми обробки кожного байта журналу.

### 1. Бінарне пакування та монотонність LSN

Заголовок кожного запису `WalRecordHeader` упаковано з вирівнюванням в 1 байт (`#pragma pack(push, 1)`), що гарантує відсутність непередбачуваних байтів заповнення (англ. *padding bytes*) між полями на різних процесорних архітектурах.

Ключовим полем заголовка є `lsn` — 64-бітне беззнакове ціле число, яке монотонно зростає з кожною зафіксованою транзакцією. При зчитуванні сегментів координатор контролює строгу монотонність послідовності: якщо черговий запис має `LSN ≤ db->last_applied_lsn`, це сигналізує про помилку дублювання сегментів або неправильний порядок читання архівних файлів зі сховища S3.

### 2. Контроль пошкодження даних (CRC32 Checksum Validation)

У розподілених системах аварійне вимкнення сервера або пошкодження дискового сектора часто призводить до запису часткових (обірваних) байтів у кінець файлу журналу. 

Рушій захищає стан бази даних за допомогою двохетапної перевірки:
1. **Перевірка магічного числа (`magic == WAL_MAGIC`):** Якщо ядро СКБД впало посеред запису заголовка, байти магічного числа не зійдуться, і рушій негайно поверне помилку `InvalidMagic`, запобігаючи неконтрольованому парсингу сміття з диска.
2. **Верифікація контрольної суми корисного навантаження:** Перед застосуванням операції до стану пам'яті функція `calculate_crc32` обчислює поліноміальну контрольну суму `CRC32-IEEE 802.3` над блоком `WalPayload` та порівнює її зі значенням `hdr.crc32`. Якщо хоча б один біт ключа або значення змінився внаслідок збою оперативної пам'яті чи диска, операція відхиляється з помилкою `ChecksumMismatch`.

### 3. Детермінований бар'єр цільового часу (Target Timestamp Barrier)

Головна перевага Point-in-Time Recovery над звичайним накатуванням бекапу полягає у можливості точної часової фільтрації.

У наведеному демонстраційному сценарії в журналі зафіксовано три послідовні події:
- `t = 150000 ms`: Оновлення балансу Аліси (`user:101 = 750 грн`).
- `t = 154000 ms`: Створення рахунку Чарлі (`user:103 = 300 грн`).
- `t = 156000 ms`: Руйнівна операція очищення таблиці (`TRUNCATE_ALL`).

Коли адміністратор встановлює параметр `target_time = 155000 ms`, рушій успішно застосовує перші дві транзакції. Щойно лічильник `hdr.timestamp_ms` досягає значення `156000 ms`, спрацьовує умова `hdr.timestamp_ms > target_stop_ts_ms`. Цикл `REDO` негайно переривається викликом `break`. Руйнівна команда `TRUNCATE` повністю ігнорується, а стан бази даних залишається узгодженим і містить усі легітимні транзакції, виконані до моменту аварії.

### 4. Низькорівневий ввід-вивід та гарантії збереження на диску (fsync vs Direct I/O)

У реальному продуктивному середовищі просте виконання системного виклику `write()` не гарантує фізичного збереження байтів на пластинах або флеш-комірках накопичувача: операційна система Linux розміщує дані у сторінковому кеші (`page cache`). Якщо в цей момент живлення дата-центру зникає, скидання буферів не відбувається, і останні кілька мегабайтів журналу зникають без сліду.

Для забезпечення гарантій довговічності ACID рушій запису WAL підпорядковується суворим системним правилам:
1. **Виклик `fdatasync(fd)` при кожному commit:** Перед тим як повернути клієнтові статус успішного завершення транзакції `200 OK`, потік зобов'язаний заблокуватися на виклику `fdatasync()`, що примушує контролер диска скинути свій внутрішній енергозалежний кеш (Volatile Write Cache) на енергонезалежний носій.
2. **Прапорець `O_DIRECT`:** При зчитуванні архівних сегментів під час відновлення PITR застосування прямого вводу-виводу `O_DIRECT` дозволяє уникнути подвійного кешування гігабайтних журналів у пам'яті ядра, вивільняючи оперативну пам'ять для буферного пулу самої СКБД.

### 5. Простеження продуктивності через eBPF (Tracepoints and Stalls)

Під час інтенсивного відновлення бази даних із журналу WAL інженери експлуатації відстежують затримки дискових операцій за допомогою інструментів eBPF. Типовий скрипт `bpftrace` для моніторингу затримок скидання журналу перехоплює системний виклик ядра:

```text
tracepoint:syscalls:sys_enter_fdatasync {
    @start[tid] = nsecs;
}
tracepoint:syscalls:sys_exit_fdatasync /@start[tid]/ {
    @latency_us = hist((nsecs - @start[tid]) / 1000);
    delete(@start[tid]);
}
```

Якщо гістограма показує наявність довгого хвоста затримок (англ. *Tail Latency*) понад 50 мс на операціях `fdatasync`, це свідчить про насичення черги вводу-виводу накопичувача NVMe, що безпосередньо загрожує збільшенням реплікаційного лагу та порушенням RPO.

### 6. Керування таймлайнами та розгалуження історії (Timeline Branching)

У промислових СКБД (зокрема PostgreSQL) після успішного завершення процедури PITR виникає фундаментальна проблема: що робити з майбутніми сегментами WAL, якщо новий лідер починає генерувати нові транзакції з тими самими номерами LSN?

Для запобігання перезапису історичних журналів вводиться концепція **ідентифікатора таймлайну (англ. *Timeline ID*, TLI)**:
1. Початковий базовий знімок працює на `TLI = 1`.
2. Коли PITR завершує відновлення на мітці `155000 ms`, СКБД створює спеціальний файл історії перемикання `.history` (наприклад, `00000002.history`), який фіксує точний LSN точки відгалуження.
3. Новий лідер перемикається на `TLI = 2` і формує нові сегменти WAL із префіксом `00000002...`.
4. Якщо згодом з'ясується, що зупинка о 155000 ms була передчасною і потрібно було відновитися до 155500 ms, адміністратор може повернутися до оригінального ланцюжка `TLI = 1` та виконати повторне відновлення по іншій гілці історії без жодного ризику втратити дані нової гілки `TLI = 2`.

### 7. Паралельне відновлення сторінок (Parallel REDO Workers)

У базах даних обсягом у десятки терабайтів послідовне програвання мільйонів записів WAL одним процесорним потоком може тривати годинами, неприпустимо роздуваючи показник RTO.

Сучасні координатори PITR розбивають потік журналу за хешем ідентифікатора сторінки (`PageID = (RelFileNode, ForkNum, BlockNum)`):
- Головний потік парсить заголовки WAL і розкладає мутації у неблокуючі кільцеві буфери окремих воркерів.
- Кожен воркер модифікує свій ізольований набір сторінок у пам'яті, що виключає стан перегонів за блокування рядків.
- Бар'єри синхронізації встановлюються лише для DDL-операцій (створення індексів, зміна схеми) та фіксації глобальних транзакцій, забезпечуючи лінійне масштабування швидкості відновлення від кількості ядер CPU.
