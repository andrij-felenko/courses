# ⚙️ Парсер бінарного журналу транзакцій та генератор подій CDC

Побудова власного або інтегрованого рушія захоплення змінних даних (CDC) вимагає глибокого розуміння двійкового формату журналу транзакцій та коректної обробки життєвого циклу транзакцій. На відміну від звичайного читання файлів, парсер транзакційного журналу стикається з трьома фундаментальними системними викликами:

1. **Паралельне переплетення операцій (Transaction Interleaving)**: У багатопотоковій системі записи різних активних транзакцій потрапляють у журнал у довільному хронологічному порядку. Парсер не може одразу випромінювати подію при читанні рядка, оскільки транзакція ще не зафіксована і згодом може бути відкочена (`ROLLBACK`).
2. **Фільтрація анульованих транзакцій (Abort Elimination)**: Якщо транзакція завершилася аварійно або виконала команду `ABORT`, усі накопичені нею зміни мають бути безслідно видалені з оперативної пам'яті парсера без надсилання споживачам.
3. **Збереження монотонного зсуву (Offset / LSN Tracking)**: Для забезпечення семантики доставки «щонайменше один раз» (at-least-once) та коректного відновлення після збоїв парсер повинен відстежувати найстарший безпечний номер LSN (`confirmed_flush_lsn`), до якого всі транзакції вже повністю оброблені та підтверджені.

---

### Архітектура двійкового формату журналу

Розгляньмо компактний двійковий протокол транзакційного журналу, який моделює основні структурні елементи реальних рушіїв (зокрема протоколу PostgreSQL `pgoutput` та MySQL Binlog RBR).

Кожен запис журналу складається з уніфікованого заголовка фіксованого розміру та змінного корисного навантаження:

```text
+-------------------+--------------------+------------------+-------------------+
| Record Type (1 B) | Length (4 B, LE)   | LSN (8 B, LE)    | XID (8 B, LE)     |
+-------------------+--------------------+------------------+-------------------+
| Payload (Length - 21 байтів):                                                 |
| - BEGIN:  Timestamp (8 B)                                                     |
| - INSERT: TableId (4 B), PK (8 B), DataLen (4 B), DataBytes (N B)             |
| - UPDATE: TableId (4 B), PK (8 B), OldLen (4 B), OldBytes, NewLen, NewBytes   |
| - DELETE: TableId (4 B), PK (8 B), OldLen (4 B), OldBytes (N B)               |
| - COMMIT: CommitLSN (8 B), CommitTimestamp (8 B)                              |
| - ABORT:  AbortTimestamp (8 B)                                                |
+-------------------------------------------------------------------------------+
```

Заголовок довжиною 21 байт визначає тип операції, повну довжину повідомлення, унікальний порядковий номер журналу (LSN) та ідентифікатор транзакції (XID). Поле `Length` дозволяє парсеру валідувати межі пам'яті до початку десеріалізації тіла запису, захищаючи процес від аварійного завершення при читанні пошкодженого двійкового потоку.

---

### Покроковий розбір алгоритму вичитування

Конвеєр обробки транзакційного журналу виконується за строго детерміністичним алгоритмом скінченного автомата:

1. **Стрімінгова валідація заголовка**: Парсер перевіряє наявність у буфері щонайменше 21 байта. Якщо байтів недостатньо, процес очікує надходження наступного мережевого пакету або порції з диска.
2. **Маршрутизація за станом транзакції**:
   * При отриманні `REC_BEGIN` створюється новий контекст транзакції в хеш-таблиці `active_transactions_`. Фіксується початковий LSN.
   * При отриманні мутацій (`INSERT`, `UPDATE`, `DELETE`) корисне навантаження додається до динамічного масиву записів поточної транзакції. Жодних мережевих викликів до зовнішніх споживачів на цьому етапі не виконується.
   * При отриманні `REC_ABORT` контекст транзакції миттєво знищується, а вся виділена пам'ять звільняється без генерації вихідних подій.
   * При отриманні `REC_COMMIT` рушій ітерується по всіх накопичених записах транзакції у порядку їх первинного виконання, формує фінальні структури подій (зокрема перед- та після-образи рядків) та відправляє їх у цільовий потік. Лише після успішної відправки оновлюється локальний показник `confirmed_flush_lsn`.

---

### Реалізація потокового парсера та транзакційного буфера

Нижче наведено повноцінну реалізацію парсера двійкового журналу та генератора подій CDC на мовах C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define WAL_MAGIC 0x57414C31 /* "WAL1" */

typedef enum {
    REC_BEGIN  = 0x01,
    REC_INSERT = 0x02,
    REC_UPDATE = 0x03,
    REC_DELETE = 0x04,
    REC_COMMIT = 0x05,
    REC_ABORT  = 0x06
} RecordType;

typedef struct {
    uint8_t  type;
    uint32_t length;
    uint64_t lsn;
    uint64_t xid;
    uint32_t table_id;
    uint64_t pk;
    uint64_t timestamp;
    char    *before_data;
    char    *after_data;
} ChangeRecord;

typedef struct {
    uint64_t      xid;
    uint64_t      begin_lsn;
    uint64_t      begin_ts;
    ChangeRecord *records;
    size_t        count;
    size_t        capacity;
} TxBuffer;

typedef struct {
    TxBuffer **tx_table;
    size_t     tx_capacity;
    uint64_t   last_confirmed_lsn;
} CdcEngine;

CdcEngine* cdc_create(size_t max_concurrent_tx) {
    CdcEngine *engine = (CdcEngine*)calloc(1, sizeof(CdcEngine));
    if (!engine) return NULL;
    engine->tx_capacity = max_concurrent_tx;
    engine->tx_table = (TxBuffer**)calloc(max_concurrent_tx, sizeof(TxBuffer*));
    if (!engine->tx_table) {
        free(engine);
        return NULL;
    }
    return engine;
}

static TxBuffer* cdc_find_or_create_tx(CdcEngine *engine, uint64_t xid) {
    size_t empty_idx = engine->tx_capacity;
    for (size_t i = 0; i < engine->tx_capacity; ++i) {
        if (engine->tx_table[i] && engine->tx_table[i]->xid == xid) {
            return engine->tx_table[i];
        }
        if (!engine->tx_table[i] && empty_idx == engine->tx_capacity) {
            empty_idx = i;
        }
    }
    if (empty_idx == engine->tx_capacity) return NULL;

    TxBuffer *tx = (TxBuffer*)calloc(1, sizeof(TxBuffer));
    if (!tx) return NULL;
    tx->xid = xid;
    tx->capacity = 16;
    tx->records = (ChangeRecord*)calloc(tx->capacity, sizeof(ChangeRecord));
    if (!tx->records) {
        free(tx);
        return NULL;
    }
    engine->tx_table[empty_idx] = tx;
    return tx;
}

static void cdc_free_tx(CdcEngine *engine, uint64_t xid) {
    for (size_t i = 0; i < engine->tx_capacity; ++i) {
        if (engine->tx_table[i] && engine->tx_table[i]->xid == xid) {
            TxBuffer *tx = engine->tx_table[i];
            for (size_t j = 0; j < tx->count; ++j) {
                free(tx->records[j].before_data);
                free(tx->records[j].after_data);
            }
            free(tx->records);
            free(tx);
            engine->tx_table[i] = NULL;
            return;
        }
    }
}

static void cdc_emit_event(const ChangeRecord *rec, uint64_t commit_lsn, uint64_t commit_ts) {
    const char *op_str = "UNKNOWN";
    if (rec->type == REC_INSERT) op_str = "c"; /* create */
    else if (rec->type == REC_UPDATE) op_str = "u"; /* update */
    else if (rec->type == REC_DELETE) op_str = "d"; /* delete */

    printf("{\"op\":\"%s\",\"lsn\":%llu,\"commit_lsn\":%llu,\"xid\":%llu,\"table_id\":%u,\"pk\":%llu,\"ts\":%llu,",
           op_str, (unsigned long long)rec->lsn, (unsigned long long)commit_lsn,
           (unsigned long long)rec->xid, rec->table_id,
           (unsigned long long)rec->pk, (unsigned long long)commit_ts);

    printf("\"before\":%s%s%s,",
           rec->before_data ? "\"" : "", rec->before_data ? rec->before_data : "null", rec->before_data ? "\"" : "");
    printf("\"after\":%s%s%s}\n",
           rec->after_data ? "\"" : "", rec->after_data ? rec->after_data : "null", rec->after_data ? "\"" : "");
}

bool cdc_process_record(CdcEngine *engine, const uint8_t *buf, size_t buf_len) {
    if (buf_len < 21) return false;

    uint8_t type = buf[0];
    uint32_t len = *(const uint32_t*)(buf + 1);
    uint64_t lsn = *(const uint64_t*)(buf + 5);
    uint64_t xid = *(const uint64_t*)(buf + 13);

    if (buf_len < len) return false;
    const uint8_t *payload = buf + 21;

    if (type == REC_BEGIN) {
        TxBuffer *tx = cdc_find_or_create_tx(engine, xid);
        if (!tx) return false;
        tx->begin_lsn = lsn;
        tx->begin_ts = *(const uint64_t*)(payload);
        return true;
    }

    if (type == REC_ABORT) {
        /* Відкат транзакції: очищуємо буфер без генерації подій */
        cdc_free_tx(engine, xid);
        return true;
    }

    if (type == REC_COMMIT) {
        TxBuffer *tx = cdc_find_or_create_tx(engine, xid);
        if (!tx) return false;

        uint64_t commit_lsn = *(const uint64_t*)(payload);
        uint64_t commit_ts = *(const uint64_t*)(payload + 8);

        /* Випромінюємо всі накопичені події підтвердженої транзакції */
        for (size_t i = 0; i < tx->count; ++i) {
            cdc_emit_event(&tx->records[i], commit_lsn, commit_ts);
        }

        engine->last_confirmed_lsn = commit_lsn;
        cdc_free_tx(engine, xid);
        return true;
    }

    /* Обробка мутацій рядків: накопичення у буфер транзакції */
    TxBuffer *tx = cdc_find_or_create_tx(engine, xid);
    if (!tx) return false;

    if (tx->count >= tx->capacity) {
        size_t new_cap = tx->capacity * 2;
        ChangeRecord *new_recs = (ChangeRecord*)realloc(tx->records, new_cap * sizeof(ChangeRecord));
        if (!new_recs) return false;
        tx->records = new_recs;
        tx->capacity = new_cap;
    }

    ChangeRecord *rec = &tx->records[tx->count++];
    memset(rec, 0, sizeof(ChangeRecord));
    rec->type = type;
    rec->lsn = lsn;
    rec->xid = xid;
    rec->table_id = *(const uint32_t*)(payload);
    rec->pk = *(const uint64_t*)(payload + 4);

    if (type == REC_INSERT) {
        uint32_t data_len = *(const uint32_t*)(payload + 12);
        rec->after_data = (char*)calloc(data_len + 1, 1);
        if (rec->after_data) memcpy(rec->after_data, payload + 16, data_len);
    } else if (type == REC_UPDATE) {
        uint32_t old_len = *(const uint32_t*)(payload + 12);
        rec->before_data = (char*)calloc(old_len + 1, 1);
        if (rec->before_data) memcpy(rec->before_data, payload + 16, old_len);

        uint32_t new_len = *(const uint32_t*)(payload + 16 + old_len);
        rec->after_data = (char*)calloc(new_len + 1, 1);
        if (rec->after_data) memcpy(rec->after_data, payload + 20 + old_len, new_len);
    } else if (type == REC_DELETE) {
        uint32_t old_len = *(const uint32_t*)(payload + 12);
        rec->before_data = (char*)calloc(old_len + 1, 1);
        if (rec->before_data) memcpy(rec->before_data, payload + 16, old_len);
    }

    return true;
}

void cdc_destroy(CdcEngine *engine) {
    if (!engine) return;
    for (size_t i = 0; i < engine->tx_capacity; ++i) {
        if (engine->tx_table[i]) {
            TxBuffer *tx = engine->tx_table[i];
            for (size_t j = 0; j < tx->count; ++j) {
                free(tx->records[j].before_data);
                free(tx->records[j].after_data);
            }
            free(tx->records);
            free(tx);
        }
    }
    free(engine->tx_table);
    free(engine);
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <span>
#include <cstdint>
#include <cstring>
#include <format>
#include <optional>

enum class RecordType : uint8_t {
    Begin  = 0x01,
    Insert = 0x02,
    Update = 0x03,
    Delete = 0x04,
    Commit = 0x05,
    Abort  = 0x06
};

struct ChangeRecord {
    RecordType  type;
    uint64_t    lsn;
    uint64_t    xid;
    uint32_t    table_id;
    uint64_t    pk;
    std::string before_data;
    std::string after_data;
};

struct TxState {
    uint64_t xid;
    uint64_t begin_lsn;
    uint64_t begin_ts;
    std::vector<ChangeRecord> records;
};

class CdcEngine {
public:
    explicit CdcEngine(size_t reserve_tx = 1024) {
        active_transactions_.reserve(reserve_tx);
    }

    bool process_record(std::span<const uint8_t> buffer) {
        if (buffer.size() < 21) return false;

        const auto type = static_cast<RecordType>(buffer[0]);
        uint32_t length = 0;
        uint64_t lsn = 0;
        uint64_t xid = 0;

        std::memcpy(&length, buffer.data() + 1, sizeof(length));
        std::memcpy(&lsn, buffer.data() + 5, sizeof(lsn));
        std::memcpy(&xid, buffer.data() + 13, sizeof(xid));

        if (buffer.size() < length) return false;
        auto payload = buffer.subspan(21, length - 21);

        switch (type) {
            case RecordType::Begin: {
                uint64_t ts = 0;
                if (payload.size() >= sizeof(ts)) {
                    std::memcpy(&ts, payload.data(), sizeof(ts));
                }
                active_transactions_[xid] = TxState{
                    .xid = xid,
                    .begin_lsn = lsn,
                    .begin_ts = ts,
                    .records = {}
                };
                return true;
            }

            case RecordType::Abort: {
                active_transactions_.erase(xid);
                return true;
            }

            case RecordType::Commit: {
                auto it = active_transactions_.find(xid);
                if (it == active_transactions_.end()) return false;

                uint64_t commit_lsn = 0;
                uint64_t commit_ts = 0;
                if (payload.size() >= 16) {
                    std::memcpy(&commit_lsn, payload.data(), sizeof(commit_lsn));
                    std::memcpy(&commit_ts, payload.data() + 8, sizeof(commit_ts));
                }

                for (const auto &rec : it->second.records) {
                    emit_event(rec, commit_lsn, commit_ts);
                }

                last_confirmed_lsn_ = commit_lsn;
                active_transactions_.erase(it);
                return true;
            }

            case RecordType::Insert:
            case RecordType::Update:
            case RecordType::Delete: {
                auto it = active_transactions_.find(xid);
                if (it == active_transactions_.end()) return false;

                if (payload.size() < 12) return false;
                uint32_t table_id = 0;
                uint64_t pk = 0;
                std::memcpy(&table_id, payload.data(), sizeof(table_id));
                std::memcpy(&pk, payload.data() + 4, sizeof(pk));

                ChangeRecord rec{
                    .type = type,
                    .lsn = lsn,
                    .xid = xid,
                    .table_id = table_id,
                    .pk = pk,
                    .before_data = {},
                    .after_data = {}
                };

                if (type == RecordType::Insert) {
                    uint32_t dlen = 0;
                    std::memcpy(&dlen, payload.data() + 12, sizeof(dlen));
                    if (payload.size() >= 16 + dlen) {
                        rec.after_data.assign(reinterpret_cast<const char*>(payload.data() + 16), dlen);
                    }
                } else if (type == RecordType::Update) {
                    uint32_t old_len = 0;
                    std::memcpy(&old_len, payload.data() + 12, sizeof(old_len));
                    if (payload.size() >= 16 + old_len + 4) {
                        rec.before_data.assign(reinterpret_cast<const char*>(payload.data() + 16), old_len);
                        uint32_t new_len = 0;
                        std::memcpy(&new_len, payload.data() + 16 + old_len, sizeof(new_len));
                        if (payload.size() >= 20 + old_len + new_len) {
                            rec.after_data.assign(reinterpret_cast<const char*>(payload.data() + 20 + old_len), new_len);
                        }
                    }
                } else if (type == RecordType::Delete) {
                    uint32_t old_len = 0;
                    std::memcpy(&old_len, payload.data() + 12, sizeof(old_len));
                    if (payload.size() >= 16 + old_len) {
                        rec.before_data.assign(reinterpret_cast<const char*>(payload.data() + 16), old_len);
                    }
                }

                it->second.records.push_back(std::move(rec));
                return true;
            }
        }
        return false;
    }

    [[nodiscard]] uint64_t confirmed_flush_lsn() const noexcept {
        return last_confirmed_lsn_;
    }

private:
    void emit_event(const ChangeRecord &rec, uint64_t commit_lsn, uint64_t commit_ts) const {
        std::string_view op = "u";
        if (rec.type == RecordType::Insert) op = "c";
        else if (rec.type == RecordType::Delete) op = "d";

        std::string before_val = rec.before_data.empty() ? "null" : std::format("\"{}\"", rec.before_data);
        std::string after_val = rec.after_data.empty() ? "null" : std::format("\"{}\"", rec.after_data);

        std::cout << std::format(
            "{{\"op\":\"{}\",\"lsn\":{},\"commit_lsn\":{},\"xid\":{},\"table_id\":{},\"pk\":{},\"ts\":{},\"before\":{},\"after\":{}}}\n",
            op, rec.lsn, commit_lsn, rec.xid, rec.table_id, rec.pk, commit_ts, before_val, after_val
        );
    }

    std::unordered_map<uint64_t, TxState> active_transactions_;
    uint64_t last_confirmed_lsn_ = 0;
};
```
:::

---

### Наскрізний приклад обробки змішаного потоку подій

Щоб наочно побачити роботу скінченного автомата, простежимо покроковий стан пам'яті парсера при проходженні тестової послідовності з двох конкурентних транзакцій: транзакції `XID=101` (успішне замовлення) та транзакції `XID=102` (скасована операція).

У вхідному потоці байти чергуються в такому хронологічному порядку:

1. `LSN 1000 | XID 101 | BEGIN`: Парсер створює буфер `TxState` для `101`.
2. `LSN 1050 | XID 102 | BEGIN`: Створюється паралельний буфер для `102`.
3. `LSN 1100 | XID 101 | INSERT orders (id=1, total=500)`: Додається запис у чергу `101`.
4. `LSN 1150 | XID 102 | UPDATE accounts (id=42, bal=0)`: Додається запис у чергу `102`.
5. `LSN 1200 | XID 102 | ABORT`: Буфер `102` видаляється. Жодних подій про зміну балансу рахунку #42 назовні не надходить.
6. `LSN 1250 | XID 101 | COMMIT`: Рушій вивантажує подію `orders: id=1` зі статусом `op="c"` у вихідний потік і зсуває `confirmed_flush_lsn` до `1250`.

У результаті зовнішні споживачі бачать виключно узгоджену послідовність підтверджених змін, уникаючи забруднення кешів та аналітичних сховищ «брудними» даними незавершених або відкочених транзакцій.

---

### Системні пастки та оптимізація продуктивності

При промисловій експлуатації потокових парсерів CDC розробники стикаються з критичними граничними випадками, які вимагають спеціальних інженерних рішень:

#### 1. Вичерпання оперативної пам'яті через масивні транзакції (Buffer Spilling)
Якщо транзакція модифікує 10 000 000 рядків в одній пакетній операції `UPDATE`, спроба утримувати всі кортежі в оперативній пам'яті призведе до спрацьовування системного OOM Killer. 
*Промислове рішення*: Застосування дворівневого буфера. Коли розмір накопичених даних для одного `XID` перевищує встановлений ліміт (наприклад, 64 МБ), парсер відкриває локальний асинхронний дисковий файл і скидає надлишкові записи на NVMe-накопичувач. Під час обробки `COMMIT` дані вичитуються з диска блоками.

#### 2. Зміна структури таблиці (Schema Drift) посеред потоку
Якщо посеред транзакційного журналу виконано оператор `ALTER TABLE orders ADD COLUMN discount NUMERIC`, фізичне кодування кортежів після точки виконання DDL змінюється.
*Промислове рішення*: Парсер підтримує версіонований реєстр схем. Кожна таблиця має історію версій `(TableId, SchemaVersion)`. Коли парсер десеріалізує кортеж із номером `LSN`, він застосовує саме ту версію схеми, яка була валідною в момент формування цього конкретного LSN.

#### 3. Нульове копіювання пам'яті (Zero-Copy Parsing)
При високому навантаженні (понад 100 000 подій на секунду) виділення пам'яті через `malloc` або створення тимчасових об'єктів `std::string` на кожен стовпчик стає головним джерелом деградації процесора та фрагментації купи.
*Промислове рішення*: Використання арени пам'яті (Arena / Monotonic Buffer Resource) або типів `std::string_view` та `std::span`, які вказують безпосередньо на байти у вхідному кільцевому буфері мережевого сокета до моменту його перезапису.
