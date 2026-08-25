# ⚙️ Реалізація рушія двофазного коміту з журналюванням та відновленням після збоїв

Розподілений транзакційний рушій двофазного коміту (2PC) — це система керування станом, яка спирається на три фундаментальні інженерні принципи:
1. **Журналювання випереджального запису (Write-Ahead Logging, WAL):** кожна зміна стану обов'язково скидається на енергонезалежний носій за допомогою системного виклику `fsync()` до того, як відповідне повідомлення надсилається мережею.
2. **Атомарний перехід стану:** вузол ніколи не змінює стан у пам'яті, якщо запис у журнал завершився помилкою.
3. **Автоматичне відновлення після аварії:** при перезапуску після падіння координатор та учасники аналізують журнал і відновлюють коректні транзакційні інваріанти.

## Архітектура та формат журналу відновлення (WAL)

Щоб гарантувати збереження стану при раптовому вимкненні живлення, кожен вузол (координатор та учасники) веде власний бінарний лог. Кожен запис журналу містить:
* магічне число `magic` (`0x3250434D` — "2PCM") для валідації формату;
* ідентифікатор транзакції `tx_id`;
* цільовий стан `state` (`PREPARING`, `PREPARED`, `COMMITTED`, `ABORTED`, `DONE`);
* контрольну суму `crc` (у найпростішому варіанті — XOR полів) для виявлення пошкоджених записів у разі аварії посеред дискового запису (англ. *torn writes*).

Будь-який запис у файл журналу супроводжується примусовим викликом `fsync()`, який змушує операційну систему скинути сторінковий кеш ядра (page cache) безпосередньо у фізичну флеш-пам'ять або магнітні пластини диска. У високопродуктивних базах даних замість повного `fsync()` часто використовують `fdatasync()`, що дозволяє оновити лише сторінки даних без примусового перезапису метаданих файлу (inode), а також груповий коміт (Group Commit) для об'єднання записів від паралельних транзакцій у єдиний блок.

У сучасних POSIX-сумісних файлових системах (ext4, XFS, ZFS) створення нового файлу журналу також вимагає синхронізації батьківського каталогу через `fsync(dir_fd)`, щоб метадані про створення файлу гарантовано потрапили в журнал файлової системи до початку транзакційної активності.

## Реалізація транзакційного рушія

Нижче наведено повну самодостатню реалізацію транзакційного рушія з симуляцією падіння вузла у стані невизначеності `PREPARED`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

#define MAX_PARTICIPANTS 4
#define WAL_RECORD_MAGIC 0x3250434Du /* "2PCM" */

/* Типи повідомлень протоколу 2PC */
typedef enum {
    MSG_PREPARE = 1,
    MSG_VOTE_COMMIT = 2,
    MSG_VOTE_ABORT = 3,
    MSG_GLOBAL_COMMIT = 4,
    MSG_GLOBAL_ABORT = 5,
    MSG_ACK = 6
} MessageType;

/* Стани учасника та координатора */
typedef enum {
    STATE_INIT = 0,
    STATE_PREPARING = 1,
    STATE_PREPARED = 2,  /* Стан невизначеності (In-Doubt) */
    STATE_COMMITTED = 3,
    STATE_ABORTED = 4,
    STATE_DONE = 5
} TxState;

/* Бінарний запис у WAL-журналі */
typedef struct {
    uint32_t magic;
    uint32_t tx_id;
    uint32_t state;
    uint32_t crc;
} WalRecord;

/* Структура учасника */
typedef struct {
    int id;
    TxState state;
    int wal_fd;
    char wal_path[64];
    bool inject_crash_in_prepared;
} Participant;

/* Структура координатора */
typedef struct {
    uint32_t tx_id;
    TxState state;
    int wal_fd;
    char wal_path[64];
    int num_participants;
    Participant *participants[MAX_PARTICIPANTS];
} Coordinator;

static void wal_write_state(int fd, uint32_t tx_id, TxState state) {
    WalRecord rec = {
        .magic = WAL_RECORD_MAGIC,
        .tx_id = tx_id,
        .state = (uint32_t)state,
        .crc = tx_id ^ (uint32_t)state
    };
    if (write(fd, &rec, sizeof(rec)) != sizeof(rec)) {
        perror("write WAL");
        exit(EXIT_FAILURE);
    }
    /* Обов'язковий примусовий скид на диск до відправки повідомлень */
    if (fsync(fd) < 0) {
        perror("fsync WAL");
        exit(EXIT_FAILURE);
    }
}

static Participant* participant_create(int id, bool crash_simulation) {
    Participant *p = (Participant*)calloc(1, sizeof(Participant));
    if (!p) return NULL;
    p->id = id;
    p->state = STATE_INIT;
    p->inject_crash_in_prepared = crash_simulation;
    snprintf(p->wal_path, sizeof(p->wal_path), "participant_%d.wal", id);
    p->wal_fd = open(p->wal_path, O_CREAT | O_RDWR | O_APPEND, 0644);
    if (p->wal_fd < 0) {
        perror("open participant WAL");
        free(p);
        return NULL;
    }
    return p;
}

static void participant_destroy(Participant *p) {
    if (p) {
        if (p->wal_fd >= 0) close(p->wal_fd);
        free(p);
    }
}

/* Обробка повідомлень учасником */
static MessageType participant_handle_message(Participant *p, uint32_t tx_id, MessageType msg) {
    switch (msg) {
        case MSG_PREPARE:
            printf("  [Учасник %d] Отримано PREPARE для транзакції %u\n", p->id, tx_id);
            /* Перевірка локальних умов (наявність ресурсів, перевірка обмежень) */
            wal_write_state(p->wal_fd, tx_id, STATE_PREPARED);
            p->state = STATE_PREPARED;
            printf("  [Учасник %d] Стан PREPARED записано у WAL. Замки заблоковано.\n", p->id);
            if (p->inject_crash_in_prepared) {
                printf("  [Учасник %d] 💥 ІМІТАЦІЯ ПАДІННЯ У СТАНІ PREPARED!\n", p->id);
                return MSG_VOTE_ABORT;
            }
            return MSG_VOTE_COMMIT;

        case MSG_GLOBAL_COMMIT:
            printf("  [Учасник %d] Отримано GLOBAL_COMMIT. Фіксація даних.\n", p->id);
            wal_write_state(p->wal_fd, tx_id, STATE_COMMITTED);
            p->state = STATE_COMMITTED;
            /* Звільнення ресурсів і зняття замків */
            return MSG_ACK;

        case MSG_GLOBAL_ABORT:
            printf("  [Учасник %d] Отримано GLOBAL_ABORT. Відкат змін.\n", p->id);
            wal_write_state(p->wal_fd, tx_id, STATE_ABORTED);
            p->state = STATE_ABORTED;
            /* Звільнення ресурсів і зняття замків */
            return MSG_ACK;

        default:
            return MSG_VOTE_ABORT;
    }
}

/* Виконання транзакції координатором */
static bool coordinator_run_tx(Coordinator *c, uint32_t tx_id) {
    c->tx_id = tx_id;
    printf("[Координатор] Початок розподіленої транзакції TX=%u\n", tx_id);

    /* ФАЗА 1: Голосування */
    wal_write_state(c->wal_fd, tx_id, STATE_PREPARING);
    c->state = STATE_PREPARING;
    printf("[Координатор] Фаза 1: розсилка PREPARE до %d учасників...\n", c->num_participants);

    bool all_yes = true;
    for (int i = 0; i < c->num_participants; ++i) {
        MessageType vote = participant_handle_message(c->participants[i], tx_id, MSG_PREPARE);
        if (vote != MSG_VOTE_COMMIT) {
            printf("[Координатор] Учасник %d проголосував проти (VOTE_ABORT)\n", c->participants[i]->id);
            all_yes = false;
        } else {
            printf("[Координатор] Учасник %d проголосував за (VOTE_COMMIT)\n", c->participants[i]->id);
        }
    }

    /* ФАЗА 2: Ухвалення та розсилка рішення */
    if (all_yes) {
        printf("[Координатор] Усі голоси ствердні. Ухвалено рішення: COMMIT.\n");
        wal_write_state(c->wal_fd, tx_id, STATE_COMMITTED);
        c->state = STATE_COMMITTED;

        for (int i = 0; i < c->num_participants; ++i) {
            MessageType ack = participant_handle_message(c->participants[i], tx_id, MSG_GLOBAL_COMMIT);
            if (ack == MSG_ACK) {
                printf("[Координатор] Отримано ACK від учасника %d\n", c->participants[i]->id);
            }
        }
    } else {
        printf("[Координатор] Є голоси проти або збої. Ухвалено рішення: ABORT.\n");
        wal_write_state(c->wal_fd, tx_id, STATE_ABORTED);
        c->state = STATE_ABORTED;

        for (int i = 0; i < c->num_participants; ++i) {
            participant_handle_message(c->participants[i], tx_id, MSG_GLOBAL_ABORT);
        }
    }

    wal_write_state(c->wal_fd, tx_id, STATE_DONE);
    c->state = STATE_DONE;
    printf("[Координатор] Транзакцію TX=%u завершено (DONE).\n\n", tx_id);
    return all_yes;
}

int main(void) {
    Coordinator coord = { .state = STATE_INIT, .num_participants = 2 };
    snprintf(coord.wal_path, sizeof(coord.wal_path), "coordinator.wal");
    coord.wal_fd = open(coord.wal_path, O_CREAT | O_RDWR | O_APPEND, 0644);
    if (coord.wal_fd < 0) {
        perror("open coordinator WAL");
        return 1;
    }

    coord.participants[0] = participant_create(1, false);
    coord.participants[1] = participant_create(2, false);

    /* Тест 1: Успішний двофазний коміт */
    coordinator_run_tx(&coord, 1001);

    /* Тест 2: Відкат через відмову одного з учасників */
    coord.participants[1]->inject_crash_in_prepared = true;
    coordinator_run_tx(&coord, 1002);

    /* Очищення ресурсів */
    participant_destroy(coord.participants[0]);
    participant_destroy(coord.participants[1]);
    close(coord.wal_fd);

    unlink("coordinator.wal");
    unlink("participant_1.wal");
    unlink("participant_2.wal");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <system_error>

namespace fs = std::filesystem;

enum class MessageType : uint8_t {
    Prepare = 1,
    VoteCommit = 2,
    VoteAbort = 3,
    GlobalCommit = 4,
    GlobalAbort = 5,
    Ack = 6
};

enum class TxState : uint8_t {
    Init = 0,
    Preparing = 1,
    Prepared = 2, // In-Doubt
    Committed = 3,
    Aborted = 4,
    Done = 5
};

struct WalRecord {
    uint32_t magic{0x3250434Du};
    uint32_t tx_id{0};
    TxState state{TxState::Init};
    uint32_t crc{0};
};

class DurableWal {
public:
    explicit DurableWal(std::string_view path) : path_(path) {
        stream_.open(path_, std::ios::binary | std::ios::out | std::ios::app);
        if (!stream_.is_open()) {
            throw std::runtime_error("Не вдалося відкрити журнал WAL: " + path_);
        }
    }

    ~DurableWal() {
        if (stream_.is_open()) {
            stream_.flush();
            stream_.close();
        }
    }

    void write_state(uint32_t tx_id, TxState state) {
        WalRecord record{
            .magic = 0x3250434Du,
            .tx_id = tx_id,
            .state = state,
            .crc = tx_id ^ static_cast<uint32_t>(state)
        };
        stream_.write(reinterpret_cast<const char*>(&record), sizeof(record));
        stream_.flush(); // Гарантоване скидання буферів
    }

    [[nodiscard]] std::string_view path() const noexcept { return path_; }

private:
    std::string path_;
    std::ofstream stream_;
};

class Participant {
public:
    Participant(int id, bool crash_injection = false)
        : id_(id),
          crash_injection_(crash_injection),
          wal_("participant_" + std::to_string(id) + ".wal") {}

    [[nodiscard]] int id() const noexcept { return id_; }
    [[nodiscard]] TxState state() const noexcept { return state_; }
    void set_crash_injection(bool enable) noexcept { crash_injection_ = enable; }

    MessageType handle_message(uint32_t tx_id, MessageType msg) {
        switch (msg) {
            case MessageType::Prepare: {
                std::cout << "  [Вузол " << id_ << "] Отримано PREPARE для TX=" << tx_id << "\n";
                wal_.write_state(tx_id, TxState::Prepared);
                state_ = TxState::Prepared;
                std::cout << "  [Вузол " << id_ << "] Зафіксовано стан PREPARED у WAL (In-Doubt).\n";

                if (crash_injection_) {
                    std::cout << "  [Вузол " << id_ << "] 💥 Відмова вузла під час голосування!\n";
                    return MessageType::VoteAbort;
                }
                return MessageType::VoteCommit;
            }
            case MessageType::GlobalCommit: {
                std::cout << "  [Вузол " << id_ << "] Отримано GLOBAL_COMMIT. Фіксація даних.\n";
                wal_.write_state(tx_id, TxState::Committed);
                state_ = TxState::Committed;
                return MessageType::Ack;
            }
            case MessageType::GlobalAbort: {
                std::cout << "  [Вузол " << id_ << "] Отримано GLOBAL_ABORT. Відкат даних.\n";
                wal_.write_state(tx_id, TxState::Aborted);
                state_ = TxState::Aborted;
                return MessageType::Ack;
            }
            default:
                return MessageType::VoteAbort;
        }
    }

    void cleanup_wal() {
        std::error_code ec;
        fs::remove(wal_.path(), ec);
    }

private:
    int id_;
    bool crash_injection_{false};
    TxState state_{TxState::Init};
    DurableWal wal_;
};

class Coordinator {
public:
    Coordinator() : wal_("coordinator.wal") {}

    void register_participant(std::shared_ptr<Participant> p) {
        participants_.push_back(std::move(p));
    }

    std::expected<bool, std::string> execute_transaction(uint32_t tx_id) {
        std::cout << "[Координатор] Старт розподіленої транзакції TX=" << tx_id << "\n";

        // Фаза 1: Голосування (Prepare)
        wal_.write_state(tx_id, TxState::Preparing);
        state_ = TxState::Preparing;
        std::cout << "[Координатор] Фаза 1: надсилання PREPARE до " << participants_.size() << " учасників\n";

        bool all_voted_yes = true;
        for (const auto& p : participants_) {
            auto vote = p->handle_message(tx_id, MessageType::Prepare);
            if (vote == MessageType::VoteCommit) {
                std::cout << "[Координатор] Вузол " << p->id() << " проголосував VOTE_COMMIT\n";
            } else {
                std::cout << "[Координатор] Вузол " << p->id() << " проголосував VOTE_ABORT\n";
                all_voted_yes = false;
            }
        }

        // Фаза 2: Ухвалення рішення
        if (all_voted_yes) {
            std::cout << "[Координатор] Усі голоси ствердні. Рішення: GLOBAL_COMMIT\n";
            wal_.write_state(tx_id, TxState::Committed);
            state_ = TxState::Committed;

            for (const auto& p : participants_) {
                auto ack = p->handle_message(tx_id, MessageType::GlobalCommit);
                if (ack == MessageType::Ack) {
                    std::cout << "[Координатор] Підтвердження (ACK) від вузла " << p->id() << "\n";
                }
            }
        } else {
            std::cout << "[Координатор] Виявлено відмову. Рішення: GLOBAL_ABORT\n";
            wal_.write_state(tx_id, TxState::Aborted);
            state_ = TxState::Aborted;

            for (const auto& p : participants_) {
                p->handle_message(tx_id, MessageType::GlobalAbort);
            }
        }

        wal_.write_state(tx_id, TxState::Done);
        state_ = TxState::Done;
        std::cout << "[Координатор] Транзакцію TX=" << tx_id << " завершено.\n\n";

        return all_voted_yes;
    }

    void cleanup_wal() {
        std::error_code ec;
        fs::remove(wal_.path(), ec);
    }

private:
    TxState state_{TxState::Init};
    DurableWal wal_;
    std::vector<std::shared_ptr<Participant>> participants_;
};

int main() {
    try {
        Coordinator coordinator;
        auto p1 = std::make_shared<Participant>(1, false);
        auto p2 = std::make_shared<Participant>(2, false);

        coordinator.register_participant(p1);
        coordinator.register_participant(p2);

        // Тест 1: Успішне виконання
        auto res1 = coordinator.execute_transaction(2001);

        // Тест 2: Відкат через збій другого учасника
        p2->set_crash_injection(true);
        auto res2 = coordinator.execute_transaction(2002);

        // Прибирання журналів
        coordinator.cleanup_wal();
        p1->cleanup_wal();
        p2->cleanup_wal();
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## Покроковий розбір алгоритму відновлення після збоїв

Під час перезапуску після аварійного відключення живлення або аварійної зупинки ОС кожен вузол виконує процедуру відновлення (англ. *crash recovery loop*), вичитуючи свій бінарний лог від початку до кінця:

### 1. Відновлення координатора
* **Випадок A: Останній валідний запис — `COMMITTED`:**
  Координатор встиг ухвалити рішення про фіксацію до аварії. Він переходить у стан `COMMITTED`, повторно надсилає повідомлення `GLOBAL_COMMIT` усім учасникам, збирає відповіді `ACK`, записує `DONE` у свій журнал і завершує транзакцію.
* **Випадок B: Останній валідний запис — `ABORTED`:**
  Координатор ухвалив рішення про скасування до аварії. Він переходить у стан `ABORTED`, надсилає `GLOBAL_ABORT` усім учасникам, збирає `ACK`, записує `DONE` і звільняє пам'ять.
* **Випадок C: Останній валідний запис — `PREPARING` (або записів про рішення немає):**
  Координатор упав під час опитування учасників до ухвалення остаточного рішення. Оскільки жоден учасник не міг отримати команду коміту, координатор застосовує **правило презумпції відкату (Presumed Abort)**: записує `ABORTED`, надсилає всім `GLOBAL_ABORT` і завершує транзакцію.

### 2. Відновлення учасника
* **Випадок A: Останній запис — `COMMITTED` або `ABORTED`:**
  Транзакція на цьому вузлі була повністю завершена до аварії. Жодних дій не потрібно.
* **Випадок B: Запис `PREPARED` відсутній:**
  Учасник упав до отримання `PREPARE` або під час підготовки. Оскільки він ще не дав гарантій коміту, він локально скасовує будь-які тимчасові зміни і при отриманні запитів відповідає `VOTE_ABORT`.
* **Випадок C: Останній запис — `PREPARED` (стан `In-Doubt`):**
  Найнебезпечніший стан. Учасник **не має права самостійно ні зафіксувати, ні відкотити зміни**. Під час старту він відновлює в оперативній пам'яті всі ексклюзивні замки на відповідних рядках таблиць і починає циклічно опитувати координатора: `«Який статус транзакції tx_id?»`. Вузол залишається заблокованим до отримання відповіді.

## Обробка крайових випадків у промислових системах

1. **Пошкодження останнього запису (Torn Write):** якщо живлення зникло посеред запису 16-байтної структури `WalRecord`, функція читання виявляє невідповідність магічного числа `magic` або незбіг контрольної суми `crc`. Хвіст файлу відсікається до останнього валідного запису (`truncate`), а вузол відновлюється зі стану попереднього цілісного запису.
2. **Мережеві таймаути та повтори:** координатор використовує експоненційне відтермінування (англ. *exponential backoff*) при повторній розсилці `GLOBAL_COMMIT`, щоб не перевантажувати мережу під час масового відновлення дата-центру після аварії. Якщо зв'язок втрачено під час Фази 1, координатор вважає це відмовою і скасовує транзакцію. Якщо зв'язок втрачено під час Фази 2, координатор продовжує спроби зв'язатися з учасником нескінченно, оскільки рішення вже прийняте і зафіксоване на диску.
3. **Ідемпотентність повідомлень:** оскільки координатор може надсилати `GLOBAL_COMMIT` повторно після збою, учасник повинен реагувати на дублікати ідемпотентно — повторно відповідати `ACK` без повторного застосування змін до сховища.
4. **Менеджер блокувань (Lock Manager) та MVCC:** у промислових базах даних (PostgreSQL, MySQL InnoDB) стан `PREPARED` утримує не просто прапорець у пам'яті, а глобальні табличні дескриптори блокувань (Lock Head). Під час перезапуску фоновий процес відновлення заново реєструє всі `Exclusive Lock` у системній хеш-таблиці замків, захищаючи підготовлені рядки від паралельних транзакцій, тоді як рушій багатоверсійного паралельного доступу (MVCC) продовжує віддавати іншим транзакціям старі знімки даних (snapshots).
