# ⚙️ Транзакційний рушій з журналом попереднього запису (WAL) та аварійним відновленням

Транзакційні гарантії часто сприймаються як магічна властивість бази даних, проте в основі рушія лежить простий і строгий детермінований алгоритм керування журналом і пам'яттю. Цей проєкт реалізує самостійний вбудований транзакційний рушій типу «ключ–значення» з підтримкою неподільності (Atomicity), ізоляції на основі блокувань (Isolation), довговічності через журнал попереднього запису (Durability) та трифазного відновлення стану після аварійного відключення живлення за спрощеною схемою ARIES (Analysis, Redo, Undo).

## Архітектура міні-рушія та життєвий цикл даних

Рушій працює з фіксованим простором числових ключів та значень і будується на взаємодії чотирьох ключових підсистем, кожна з яких відповідає за свою ланку гарантій ACID:

1. **Сховище даних у пам'яті (*Buffer Pool*)**: масив сторінок або таблиця записів, що зберігає актуальний стан ключів у оперативній пам'яті. Кожен запис має мітку `page_lsn` — монотонно зростаючий номер останнього запису в журналі WAL, який змінював цей конкретний ключ. Ця мітка дозволяє підсистемі відновлення точно знати, чи були зміни вже застосовані до сторінки.
2. **Журнал попереднього запису (*Write-Ahead Log, WAL*)**: файл на диску, у який послідовно записуються структуровані бінарні записи змін. Кожен запис отримує унікальний глобальний ідентифікатор **LSN** (*Log Sequence Number*). Запис у файл WAL відбувається виключно шляхом послідовного додавання (*append-only*), що забезпечує максимальну швидкість вводу-виводу.
3. **Менеджер блокувань (*Lock Manager*)**: реалізує строге двофазне блокування (*Strict 2PL*). Коли транзакція намагається модифікувати значення ключа, вона зобов'язана попередньо захопити ексклюзивний замок на цей ключ. Усі захоплені замки утримуються до самого моменту завершення транзакції (виклику `commit` або `abort`), що повністю унеможливлює аномалії брудного читання та брудного запису.
4. **Підсистема відновлення (*Recovery Manager*)**: компонент, що активується під час запуску системи після аварійного збою чи вимикання живлення. Вона аналізує вміст журналу WAL на диску, визначає стан кожної транзакції на момент аварії та повертає базу даних до узгодженого стану.

### Структура запису журналу (WAL Record)

Кожен бінарний запис у файлі журналу містить вичерпну інформацію, необхідну для відновлення системи в обох напрямках — вперед (*REDO*) та назад (*UNDO*):

```
+---------+----------+----------+--------+---------+---------+
| LSN (8) | TxnID(8) | Type (4) | Key(4) | OldVal  | NewVal  |
+---------+----------+----------+--------+---------+---------+
```

Призначення полів та типи записів:
- `lsn` — унікальний порядковий номер запису в журналі.
- `txn_id` — числовий ідентифікатор транзакції, яка виконала дію.
- `type` — тип операції:
  - `LOG_BEGIN` — початок нової транзакції; фіксує появу активного транзакційного контексту.
  - `LOG_UPDATE` — модифікація ключа. Містить старе значення `old_val` (використовується для скасування змін транзакції) та нове значення `new_val` (використовується для накату змін після збою).
  - `LOG_COMMIT` — успішна фіксація транзакції. Запис цього типу обов'язково супроводжується системним викликом `fsync()`, який примушує контролер диска скинути всі буферизовані байти на фізичний носій.
  - `LOG_ABORT` — явне скасування транзакції, після якого всі її модифікації вважаються анульованими.

## Алгоритм відновлення після збою (Recovery Cycle)

Відновлення після збою реалізує спрощену модель алгоритму ARIES і складається з трьох послідовних фаз:

1. **Фаза аналізу (*Analysis Pass*)**:
   Рушій відкриває файл журналу WAL і сканує його від початку до кінця. Під час сканування формується список транзакцій, які перебували у стані `ACTIVE` у момент збою. Якщо для транзакції зустрічається запис `LOG_BEGIN`, вона додається до списку активних; якщо згодом зустрічається `LOG_COMMIT` або `LOG_ABORT`, вона видаляється зі списку. Наприкінці аналізу в пам'яті лишається точний перелік незавершених (збійних) транзакцій (*Loser Transactions*).

2. **Фаза повторення (*REDO Pass*)**:
   Рушій знову сканує журнал від початку файлу і послідовно застосовує всі операції `LOG_UPDATE`, записуючи `new_val` у таблицю оперативної пам'яті та оновлюючи `page_lsn`. Ця дія виконується для **всіх** транзакцій без винятку — як зафіксованих, так і незафіксованих. Цей принцип («повторення історії») повертає пам'ять системи в точний стан, який існував за мікросекунду до аварії.

3. **Фаза скасування (*UNDO Pass*)**:
   Рушій сканує журнал у зворотному напрямку (від кінця файлу до початку) і знаходить усі операції `LOG_UPDATE`, що належали збійним незавершеним транзакціям. Для кожної такої операції значення ключа в таблиці замінюється на `old_val`. У результаті всі незафіксовані зміни безслідно зникають, а база даних приходить у коректний узгоджений стан.

## Реалізація на C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

#define MAX_KEYS 1024
#define WAL_PATH "minidb.wal"

typedef enum {
    LOG_BEGIN = 1,
    LOG_UPDATE = 2,
    LOG_COMMIT = 3,
    LOG_ABORT = 4
} LogType;

typedef struct {
    uint64_t lsn;
    uint64_t txn_id;
    uint32_t type;
    uint32_t key;
    int32_t old_val;
    int32_t new_val;
} WalRecord;

typedef struct {
    int32_t val;
    uint64_t page_lsn;
    uint64_t lock_owner; // 0 = unlocked, >0 = txn_id
} TableEntry;

typedef struct {
    TableEntry entries[MAX_KEYS];
    int wal_fd;
    uint64_t next_lsn;
    uint64_t next_txn_id;
} Engine;

bool engine_init(Engine *eng) {
    memset(eng->entries, 0, sizeof(eng->entries));
    eng->next_lsn = 1;
    eng->next_txn_id = 1;
    eng->wal_fd = open(WAL_PATH, O_CREAT | O_RDWR | O_APPEND, 0644);
    return eng->wal_fd >= 0;
}

void engine_close(Engine *eng) {
    if (eng->wal_fd >= 0) {
        fsync(eng->wal_fd);
        close(eng->wal_fd);
        eng->wal_fd = -1;
    }
}

uint64_t append_wal(Engine *eng, uint64_t txn_id, LogType type,
                    uint32_t key, int32_t old_v, int32_t new_v, bool flush) {
    WalRecord rec = {
        .lsn = eng->next_lsn++,
        .txn_id = txn_id,
        .type = (uint32_t)type,
        .key = key,
        .old_val = old_v,
        .new_val = new_v
    };
    write(eng->wal_fd, &rec, sizeof(rec));
    if (flush) {
        fsync(eng->wal_fd);
    }
    return rec.lsn;
}

uint64_t txn_begin(Engine *eng) {
    uint64_t tid = eng->next_txn_id++;
    append_wal(eng, tid, LOG_BEGIN, 0, 0, 0, false);
    return tid;
}

bool txn_update(Engine *eng, uint64_t tid, uint32_t key, int32_t new_v) {
    if (key >= MAX_KEYS) return false;
    TableEntry *entry = &eng->entries[key];

    // Песимістичне блокування (2PL): перевірка власника замка
    if (entry->lock_owner != 0 && entry->lock_owner != tid) {
        return false; // Конфлікт блокування
    }
    entry->lock_owner = tid;

    int32_t old_v = entry->val;
    // Запис у WAL ПЕРЕД зміною даних у пам'яті (Undo/Redo Invariant)
    uint64_t lsn = append_wal(eng, tid, LOG_UPDATE, key, old_v, new_v, false);

    entry->val = new_v;
    entry->page_lsn = lsn;
    return true;
}

void txn_commit(Engine *eng, uint64_t tid) {
    // Надійний запис COMMIT у WAL із викликом fsync (Durability)
    append_wal(eng, tid, LOG_COMMIT, 0, 0, 0, true);

    // Звільнення блокувань (Strict 2PL)
    for (uint32_t k = 0; k < MAX_KEYS; ++k) {
        if (eng->entries[k].lock_owner == tid) {
            eng->entries[k].lock_owner = 0;
        }
    }
}

void txn_abort(Engine *eng, uint64_t tid) {
    // Скасування: читаємо WAL у зворотному напрямку для відкату змін цієї транзакції
    off_t cur = lseek(eng->wal_fd, 0, SEEK_END);
    off_t pos = cur;
    WalRecord rec;

    while (pos >= (off_t)sizeof(WalRecord)) {
        pos -= sizeof(WalRecord);
        lseek(eng->wal_fd, pos, SEEK_SET);
        if (read(eng->wal_fd, &rec, sizeof(rec)) == sizeof(rec)) {
            if (rec.txn_id == tid && rec.type == LOG_UPDATE) {
                if (rec.key < MAX_KEYS) {
                    eng->entries[rec.key].val = rec.old_val;
                }
            }
        }
    }
    lseek(eng->wal_fd, cur, SEEK_SET);

    append_wal(eng, tid, LOG_ABORT, 0, 0, 0, true);

    for (uint32_t k = 0; k < MAX_KEYS; ++k) {
        if (eng->entries[k].lock_owner == tid) {
            eng->entries[k].lock_owner = 0;
        }
    }
}

// Трифазне відновлення після аварійного збою
void engine_recover(Engine *eng) {
    int fd = open(WAL_PATH, O_RDONLY);
    if (fd < 0) return;

    // Фаза 1: Аналіз активних транзакцій
    #define MAX_TXNS 256
    uint64_t active_txns[MAX_TXNS];
    int active_cnt = 0;

    WalRecord rec;
    uint64_t max_lsn = 0;
    uint64_t max_tid = 0;

    while (read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
        if (rec.lsn > max_lsn) max_lsn = rec.lsn;
        if (rec.txn_id > max_tid) max_tid = rec.txn_id;

        if (rec.type == LOG_BEGIN) {
            if (active_cnt < MAX_TXNS) active_txns[active_cnt++] = rec.txn_id;
        } else if (rec.type == LOG_COMMIT || rec.type == LOG_ABORT) {
            for (int i = 0; i < active_cnt; ++i) {
                if (active_txns[i] == rec.txn_id) {
                    active_txns[i] = active_txns[--active_cnt];
                    break;
                }
            }
        }
    }

    // Фаза 2: REDO (повторення всіх змін)
    lseek(fd, 0, SEEK_SET);
    while (read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
        if (rec.type == LOG_UPDATE && rec.key < MAX_KEYS) {
            eng->entries[rec.key].val = rec.new_val;
            eng->entries[rec.key].page_lsn = rec.lsn;
        }
    }

    // Фаза 3: UNDO (скасування незафіксованих транзакцій)
    for (int i = 0; i < active_cnt; ++i) {
        uint64_t bad_tid = active_txns[i];
        off_t pos = lseek(fd, 0, SEEK_END);
        while (pos >= (off_t)sizeof(WalRecord)) {
            pos -= sizeof(WalRecord);
            lseek(fd, pos, SEEK_SET);
            if (read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
                if (rec.txn_id == bad_tid && rec.type == LOG_UPDATE) {
                    if (rec.key < MAX_KEYS) {
                        eng->entries[rec.key].val = rec.old_val;
                    }
                }
            }
        }
    }

    close(fd);
    eng->next_lsn = max_lsn + 1;
    eng->next_txn_id = max_tid + 1;
}
```
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <string_view>
#include <filesystem>
#include <fstream>
#include <cstdint>
#include <stdexcept>
#include <optional>
#include <unistd.h>
#include <fcntl.h>

namespace minidb {

enum class LogType : uint32_t {
    Begin = 1,
    Update = 2,
    Commit = 3,
    Abort = 4
};

#pragma pack(push, 1)
struct WalRecord {
    uint64_t lsn{0};
    uint64_t txn_id{0};
    LogType type{LogType::Begin};
    uint32_t key{0};
    int32_t old_val{0};
    int32_t new_val{0};
};
#pragma pack(pop)

struct TableEntry {
    int32_t val{0};
    uint64_t page_lsn{0};
    uint64_t lock_owner{0}; // 0 = unlocked
};

class TransactionEngine {
public:
    explicit TransactionEngine(std::string_view wal_path)
        : wal_path_(wal_path) {
        wal_fd_ = ::open(wal_path_.c_str(), O_CREAT | O_RDWR | O_APPEND, 0644);
        if (wal_fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити журнал WAL");
        }
    }

    ~TransactionEngine() noexcept {
        if (wal_fd_ >= 0) {
            ::fsync(wal_fd_);
            ::close(wal_fd_);
        }
    }

    // Заборона копіювання через володіння дескриптором файлу
    TransactionEngine(const TransactionEngine&) = delete;
    TransactionEngine& operator=(const TransactionEngine&) = delete;

    uint64_t begin_transaction() {
        uint64_t tid = next_txn_id_++;
        append_wal(tid, LogType::Begin, 0, 0, 0, false);
        return tid;
    }

    bool update(uint64_t tid, uint32_t key, int32_t new_v) {
        auto& entry = storage_[key];

        // Суворе двофазне блокування (Strict 2PL)
        if (entry.lock_owner != 0 && entry.lock_owner != tid) {
            return false; // Конфлікт блокування з іншою транзакцією
        }
        entry.lock_owner = tid;

        int32_t old_v = entry.val;
        // Undo/Redo Invariant: WAL записується ПЕРЕД оновленням пам'яті
        uint64_t lsn = append_wal(tid, LogType::Update, key, old_v, new_v, false);

        entry.val = new_v;
        entry.page_lsn = lsn;
        return true;
    }

    void commit(uint64_t tid) {
        // Durability: примусовий скид буфера WAL на постійний диск
        append_wal(tid, LogType::Commit, 0, 0, 0, true);
        release_locks(tid);
    }

    void abort(uint64_t tid) {
        // Скасування: відкат змін за допомогою записів у журналі
        rollback_active_records(tid);
        append_wal(tid, LogType::Abort, 0, 0, 0, true);
        release_locks(tid);
    }

    int32_t read(uint32_t key) const {
        auto it = storage_.find(key);
        return (it != storage_.end()) ? it->second.val : 0;
    }

    void recover() {
        if (!std::filesystem::exists(wal_path_)) return;

        int fd = ::open(wal_path_.c_str(), O_RDONLY);
        if (fd < 0) return;

        std::unordered_set<uint64_t> active_txns;
        uint64_t max_lsn = 0;
        uint64_t max_tid = 0;
        WalRecord rec;

        // Фаза 1: Аналіз активних транзакцій на момент збою
        while (::read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
            max_lsn = std::max(max_lsn, rec.lsn);
            max_tid = std::max(max_tid, rec.txn_id);

            if (rec.type == LogType::Begin) {
                active_txns.insert(rec.txn_id);
            } else if (rec.type == LogType::Commit || rec.type == LogType::Abort) {
                active_txns.erase(rec.txn_id);
            }
        }

        // Фаза 2: Повторення історії (REDO)
        ::lseek(fd, 0, SEEK_SET);
        while (::read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
            if (rec.type == LogType::Update) {
                auto& entry = storage_[rec.key];
                entry.val = rec.new_val;
                entry.page_lsn = rec.lsn;
            }
        }

        // Фаза 3: Скасування незафіксованих змін (UNDO)
        for (uint64_t uncommitted_tid : active_txns) {
            off_t pos = ::lseek(fd, 0, SEEK_END);
            while (pos >= static_cast<off_t>(sizeof(WalRecord))) {
                pos -= sizeof(WalRecord);
                ::lseek(fd, pos, SEEK_SET);
                if (::read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
                    if (rec.txn_id == uncommitted_tid && rec.type == LogType::Update) {
                        storage_[rec.key].val = rec.old_val;
                    }
                }
            }
        }

        ::close(fd);
        next_lsn_ = max_lsn + 1;
        next_txn_id_ = max_tid + 1;
    }

private:
    std::string wal_path_;
    int wal_fd_{-1};
    uint64_t next_lsn_{1};
    uint64_t next_txn_id_{1};
    std::unordered_map<uint32_t, TableEntry> storage_;

    uint64_t append_wal(uint64_t tid, LogType type, uint32_t key,
                        int32_t old_v, int32_t new_v, bool flush) {
        WalRecord rec{
            .lsn = next_lsn_++,
            .txn_id = tid,
            .type = type,
            .key = key,
            .old_val = old_v,
            .new_val = new_v
        };
        ::write(wal_fd_, &rec, sizeof(rec));
        if (flush) {
            ::fsync(wal_fd_);
        }
        return rec.lsn;
    }

    void rollback_active_records(uint64_t tid) {
        off_t cur = ::lseek(wal_fd_, 0, SEEK_END);
        off_t pos = cur;
        WalRecord rec;

        while (pos >= static_cast<off_t>(sizeof(WalRecord))) {
            pos -= sizeof(WalRecord);
            ::lseek(wal_fd_, pos, SEEK_SET);
            if (::read(wal_fd_, &rec, sizeof(rec)) == sizeof(rec)) {
                if (rec.txn_id == tid && rec.type == LogType::Update) {
                    storage_[rec.key].val = rec.old_val;
                }
            }
        }
        ::lseek(wal_fd_, cur, SEEK_SET);
    }

    void release_locks(uint64_t tid) {
        for (auto& [key, entry] : storage_) {
            if (entry.lock_owner == tid) {
                entry.lock_owner = 0;
            }
        }
    }
};

} // namespace minidb
```
:::

## Інженерні підводні камені та тестування аварійних збоїв

1. **Порядок `write` та `fsync`**:
   Якщо рушій оновить значення в оперативній пам'яті до того, як запис WAL з'явиться в буфері журналу, раптове аварійне скидання сторінки на диск операційною системою спричинить непоправне порушення атомарності. На диску опиниться нове значення, але в журналі не буде запису UNDO для його скасування при збої. Інваріант попереднього запису вимагає суворого дотримання черговості: спочатку запис у лог, і лише потім — зміна в пам'яті.

2. **Частковий запис блоків (*Torn Writes*)**:
   Накопичувачі записують дані секторами (512 або 4096 байтів). Якщо знеструмлення станеться посеред запису сектора, WAL-запис буде пошкоджено. Промислові рушії (наприклад, PostgreSQL та InnoDB) використовують контрольну суму (CRC32) для кожного запису журналу та спеціальні механізми подвійного запису (*Doublewrite Buffer*), щоб виявляти пошкоджені записи під час аналізу.

3. **Стрес-тестування відновлення (Crash Simulation)**:
   Для верифікації коректності відновлення виконується паралельний запуск кількох потоків транзакцій із раптовим надсиланням сигналу `kill -9` (`SIGKILL`) або примусовим аварійним виходом (`_exit(1)`). Після перезапуску викликається `engine_recover()`, і виконується перевірка інваріантів: сума значень на всіх рахунках повинна залишатися строго рівною початковій сумі, а всі частково виконані транзакції мають бути повністю відкочені.
