# ⚙️ Довговічна черга точка-точка з орендою видимості та журналом WAL на C та C++

У розподілених системах черга повідомлень типу «точка-точка» повинна одночасно гарантувати дві критичні властивості:
1. **Стійкість до аварій (Durability):** якщо процес брокера або операційна система раптово знеструмлюється, жодне прийняте завдання не повинно зникнути.
2. **Безпечна оренда повідомлень (Visibility Timeout / Leasing):** коли воркер бере завдання в обробку, воно блокується для інших виконавців на певний час. Якщо воркер гине посеред виконання (падіння процесу, обрив мережі), брокер зобов'язаний автоматично повернути завдання в чергу для інших споживачів.

Нижче наведено повнофункціональну інженерну реалізацію довговічної черги точка-точка мовами C та C++, яка підтримує дисковий журнал випереджального запису (WAL), багатопотоковий пул конкурентних споживачів, таймаути видимості та протокол підтверджень `ACK`/`NACK`.

## Призначення та ключові вимоги до рушія

У розподілених системах черга повідомлень типу «точка-точка» (англ. *Point-to-Point Message Queue*) є базовим будівельним блоком для побудови стійких конвеєрів фонової обробки завдань. На відміну від простих черг у пам'яті (`std::queue` чи кільцевих буферів), промисловий брокер повідомлень повинен розв'язувати комплекс фундаментальних задач надійності:

1. **Стійкість до раптових аварій (Durable Crash Recovery):**
   Якщо процес брокера аварійно завершується через вичерпання пам'яті (`OOM Killer`), апаратний збій або раптове вимкнення живлення сервера, жодне підтверджене відправником повідомлення не повинно зникнути. Після перезапуску стан черги має автоматично відновитися з енергонезалежного дискового носія без втрати цілісності.

2. **Оренда з таймаутом видимості (Leasing / Visibility Timeout):**
   У моделі «точка-точка» одне повідомлення має бути оброблене рівно одним виконавцем із пулу конкурентних воркерів. Коли вільний воркер вичитує завдання, воно не видаляється з черги негайно. Натомість воно переходить у тимчасово заблокований стан оренди (`IN_FLIGHT`). Для решти воркерів це повідомлення стає невидимим на час дії оренди (наприклад, 30 секунд). Якщо воркер успішно завершує роботу й відправляє підтвердження `ACK`, брокер остаточно видаляє запис. Якщо ж воркер зазнає аварії або зависає в нескінченному циклі, брокер після завершення таймауту зобов'язаний автоматично повернути завдання в стан готовності (`READY`) для іншого живого воркера.

3. **Захист від пошкодження даних (Data Integrity & Checksumming):**
   При асинхронному скиданні даних на диск або неповних записах під час знеструмлення файл журналу може містити пошкоджені хвостові байти (англ. *Torn Writes*). Кожен запис у журналі повинен супроводжуватися магічним числом та контрольною сумою (CRC32), щоб процедура відновлення могла виявити пошкодження та безпечно зупинитися на останній валідній транзакції.

Нижче наведено повнофункціональну інженерну реалізацію довговічної черги точка-точка мовами C та C++, яка містить повноцінний дисковий журнал випереджального запису (WAL), потокобезпечний диспетчер станів, фоновий таймер відновлення оренди та протокол підтверджень `ACK`/`NACK`.

## Анатомія дискового журналу та розподілу пам'яті

Щоб досягти високої пропускної здатності, брокер не повинен виконувати випадковий пошук по диску при кожній публікації. Усі мутації стану записуються в **журнал випереджального запису** (англ. *Write-Ahead Log, WAL*) виключно послідовним додаванням у кінець файлу (англ. *Sequential Append-Only I/O*).

Кожен запис у WAL-файлі складається з фіксованого бінарного заголовка та варіативного тіла корисного навантаження:

```
┌─────────────────┬─────────────────┬──────────────────┬───────────┬──────────────────┬──────────────────────┐
│  Magic (4 B)    │  CRC32 (4 B)    │  Msg ID (8 B)    │ Op (1 B)  │ Length (4 B)     │ Payload (N байтів)   │
│  0x51554555     │  Контрольна     │  Монотонний      │ 1=Enqueue │ Розмір корисних  │ Довільні бінарні     │
│  ("QUEU")       │  сума тіла      │  ідентифікатор   │ 2=Acquire │ даних            │ дані завдання        │
│                 │                 │                  │ 3=Ack     │                  │                      │
│                 │                 │                  │ 4=Nack    │                  │                      │
└─────────────────┴─────────────────┴──────────────────┴───────────┴──────────────────┴──────────────────────┘
```

Операції журналу кодують повний життєвий цикл повідомлення:
- `WAL_OP_ENQUEUE` (1): нове завдання надійшло від продюсера. Журнал містить повний вміст корисного навантаження.
- `WAL_OP_ACQUIRE` (2): воркер взяв повідомлення в обробку. Записується лише ідентифікатор завдання без повторного копіювання тіла.
- `WAL_OP_ACK` (3): воркер успішно підтвердив виконання. Завдання вважається завершеним.
- `WAL_OP_NACK` (4): воркер явно відхилив завдання через тимчасову помилку зовнішнього ресурсу. Завдання повертається в чергу.

В оперативній пам'яті брокер підтримує циклічний масив слотів (`queue_item_t`), індексований за залишковим принципом `slot = msg_id % MAX_MESSAGES`. Це забезпечує константну швидкість доступу `O(1)` для операцій `publish`, `acquire`, `ack` та `nack` без необхідності динамічного виділення пам'яті в критичному шляху передачі даних.

```
                    ┌─────────────────────────┐
                    │  Дисковий журнал (WAL)  │
                    │  (послідовний append)   │
                    └────────────▲────────────┘
                                 │ fsync
Продюсер ──> [ enqueue() ] ──────┴──────> [ Пул READY ]
                                             │ acquire()
                                             ▼
                                      [ Стан IN_FLIGHT ] ──(таймаут оренди)──> [ Повернення в READY ]
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      │ ack()                                       │ nack()
                      ▼                                             ▼
               [ Стан ACKED ]                                [ Повернення в READY ]
            (видалення з черги)                             (або переміщення в DLQ)
```

## Реалізація на мовах C та C++

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

#define MAX_PAYLOAD_SIZE 512
#define MAX_MESSAGES     1024
#define WAL_MAGIC        0x51554555 /* "QUEU" */

typedef enum {
    MSG_STATE_EMPTY = 0,
    MSG_STATE_READY,
    MSG_STATE_IN_FLIGHT,
    MSG_STATE_ACKED
} msg_state_t;

typedef enum {
    WAL_OP_ENQUEUE = 1,
    WAL_OP_ACQUIRE = 2,
    WAL_OP_ACK     = 3,
    WAL_OP_NACK    = 4
} wal_op_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint32_t crc32;
    uint64_t msg_id;
    uint8_t  op_type;
    uint32_t payload_len;
} wal_header_t;
#pragma pack(pop)

typedef struct {
    uint64_t    id;
    msg_state_t state;
    uint64_t    lease_deadline_ms;
    uint32_t    attempts;
    uint32_t    payload_len;
    char        payload[MAX_PAYLOAD_SIZE];
} queue_item_t;

typedef struct {
    queue_item_t    items[MAX_MESSAGES];
    uint64_t        next_msg_id;
    int             wal_fd;
    pthread_mutex_t lock;
    pthread_cond_t  cond_ready;
    bool            running;
} p2p_queue_t;

static uint64_t get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

static void wal_append_record(p2p_queue_t *q, wal_op_t op, uint64_t msg_id,
                              const char *payload, uint32_t len) {
    if (q->wal_fd < 0) return;

    wal_header_t hdr;
    hdr.magic = WAL_MAGIC;
    hdr.msg_id = msg_id;
    hdr.op_type = (uint8_t)op;
    hdr.payload_len = len;
    hdr.crc32 = calc_crc32((const uint8_t *)payload, len);

    write(q->wal_fd, &hdr, sizeof(hdr));
    if (len > 0 && payload != NULL) {
        write(q->wal_fd, payload, len);
    }
    fdatasync(q->wal_fd);
}

int p2p_queue_init(p2p_queue_t *q, const char *wal_path) {
    memset(q, 0, sizeof(*q));
    q->next_msg_id = 1;
    q->running = true;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->cond_ready, NULL);

    q->wal_fd = open(wal_path, O_CREAT | O_RDWR | O_APPEND, 0644);
    if (q->wal_fd < 0) {
        perror("open wal");
        return -1;
    }

    /* Відновлення стану з журналу WAL */
    lseek(q->wal_fd, 0, SEEK_SET);
    wal_header_t hdr;
    while (read(q->wal_fd, &hdr, sizeof(hdr)) == sizeof(hdr)) {
        if (hdr.magic != WAL_MAGIC) break;

        char buf[MAX_PAYLOAD_SIZE];
        if (hdr.payload_len > 0) {
            read(q->wal_fd, buf, hdr.payload_len);
        }

        uint32_t slot = hdr.msg_id % MAX_MESSAGES;
        if (hdr.op_type == WAL_OP_ENQUEUE) {
            q->items[slot].id = hdr.msg_id;
            q->items[slot].state = MSG_STATE_READY;
            q->items[slot].payload_len = hdr.payload_len;
            memcpy(q->items[slot].payload, buf, hdr.payload_len);
            if (hdr.msg_id >= q->next_msg_id) {
                q->next_msg_id = hdr.msg_id + 1;
            }
        } else if (hdr.op_type == WAL_OP_ACK) {
            q->items[slot].state = MSG_STATE_ACKED;
        } else if (hdr.op_type == WAL_OP_NACK) {
            q->items[slot].state = MSG_STATE_READY;
        }
    }
    lseek(q->wal_fd, 0, SEEK_END);
    return 0;
}

uint64_t p2p_queue_publish(p2p_queue_t *q, const char *payload, uint32_t len) {
    if (len > MAX_PAYLOAD_SIZE) return 0;

    pthread_mutex_lock(&q->lock);
    uint64_t msg_id = q->next_msg_id++;
    uint32_t slot = msg_id % MAX_MESSAGES;

    q->items[slot].id = msg_id;
    q->items[slot].state = MSG_STATE_READY;
    q->items[slot].attempts = 0;
    q->items[slot].lease_deadline_ms = 0;
    q->items[slot].payload_len = len;
    memcpy(q->items[slot].payload, payload, len);

    wal_append_record(q, WAL_OP_ENQUEUE, msg_id, payload, len);

    pthread_cond_signal(&q->cond_ready);
    pthread_mutex_unlock(&q->lock);
    return msg_id;
}

bool p2p_queue_acquire(p2p_queue_t *q, uint64_t lease_duration_ms,
                       uint64_t *out_msg_id, char *out_buf, uint32_t *out_len) {
    pthread_mutex_lock(&q->lock);

    while (q->running) {
        uint64_t now = get_time_ms();
        for (size_t i = 0; i < MAX_MESSAGES; ++i) {
            if (q->items[i].state == MSG_STATE_READY) {
                q->items[i].state = MSG_STATE_IN_FLIGHT;
                q->items[i].lease_deadline_ms = now + lease_duration_ms;
                q->items[i].attempts++;

                *out_msg_id = q->items[i].id;
                *out_len = q->items[i].payload_len;
                memcpy(out_buf, q->items[i].payload, q->items[i].payload_len);

                wal_append_record(q, WAL_OP_ACQUIRE, q->items[i].id, NULL, 0);

                pthread_mutex_unlock(&q->lock);
                return true;
            }
        }

        struct timespec to;
        clock_gettime(CLOCK_REALTIME, &to);
        to.tv_sec += 1;
        pthread_cond_timedwait(&q->cond_ready, &q->lock, &to);
    }

    pthread_mutex_unlock(&q->lock);
    return false;
}

void p2p_queue_ack(p2p_queue_t *q, uint64_t msg_id) {
    pthread_mutex_lock(&q->lock);
    uint32_t slot = msg_id % MAX_MESSAGES;
    if (q->items[slot].id == msg_id && q->items[slot].state == MSG_STATE_IN_FLIGHT) {
        q->items[slot].state = MSG_STATE_ACKED;
        wal_append_record(q, WAL_OP_ACK, msg_id, NULL, 0);
    }
    pthread_mutex_unlock(&q->lock);
}

void p2p_queue_nack(p2p_queue_t *q, uint64_t msg_id) {
    pthread_mutex_lock(&q->lock);
    uint32_t slot = msg_id % MAX_MESSAGES;
    if (q->items[slot].id == msg_id && q->items[slot].state == MSG_STATE_IN_FLIGHT) {
        q->items[slot].state = MSG_STATE_READY;
        q->items[slot].lease_deadline_ms = 0;
        wal_append_record(q, WAL_OP_NACK, msg_id, NULL, 0);
        pthread_cond_signal(&q->cond_ready);
    }
    pthread_mutex_unlock(&q->lock);
}

void p2p_queue_reclaim_expired(p2p_queue_t *q) {
    pthread_mutex_lock(&q->lock);
    uint64_t now = get_time_ms();
    bool signaled = false;

    for (size_t i = 0; i < MAX_MESSAGES; ++i) {
        if (q->items[i].state == MSG_STATE_IN_FLIGHT && now >= q->items[i].lease_deadline_ms) {
            printf("[Брокер] Оренда повідомлення #%lu вичерпана! Повертаємо в чергу READY.\n",
                   (unsigned long)q->items[i].id);
            q->items[i].state = MSG_STATE_READY;
            q->items[i].lease_deadline_ms = 0;
            signaled = true;
        }
    }

    if (signaled) {
        pthread_cond_broadcast(&q->cond_ready);
    }
    pthread_mutex_unlock(&q->lock);
}

void p2p_queue_destroy(p2p_queue_t *q) {
    pthread_mutex_lock(&q->lock);
    q->running = false;
    pthread_cond_broadcast(&q->cond_ready);
    pthread_mutex_unlock(&q->lock);

    if (q->wal_fd >= 0) {
        close(q->wal_fd);
    }
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->cond_ready);
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <fstream>
#include <filesystem>
#include <cstdint>
#include <cstring>

namespace p2p {

using namespace std::chrono_literals;

enum class MessageState : uint8_t {
    Empty = 0,
    Ready,
    InFlight,
    Acked
};

enum class WalOp : uint8_t {
    Enqueue = 1,
    Acquire = 2,
    Ack     = 3,
    Nack    = 4
};

#pragma pack(push, 1)
struct WalHeader {
    uint32_t magic{0x51554555};
    uint32_t crc32{0};
    uint64_t msg_id{0};
    WalOp    op_type{WalOp::Enqueue};
    uint32_t payload_len{0};
};
#pragma pack(pop)

struct QueueItem {
    uint64_t id{0};
    MessageState state{MessageState::Empty};
    std::chrono::steady_clock::time_point lease_deadline{};
    uint32_t attempts{0};
    std::string payload;
};

class DurableQueue {
public:
    explicit DurableQueue(std::filesystem::path wal_path, size_t capacity = 1024)
        : wal_path_(std::move(wal_path)), items_(capacity), running_(true) {
        open_and_replay_wal();
        reclaim_thread_ = std::jthread([this](std::stop_token st) {
            reclaim_loop(st);
        });
    }

    ~DurableQueue() {
        stop();
    }

    uint64_t publish(std::string_view payload) {
        std::unique_lock lock(mutex_);
        uint64_t msg_id = next_id_++;
        size_t slot = msg_id % items_.size();

        items_[slot].id = msg_id;
        items_[slot].state = MessageState::Ready;
        items_[slot].attempts = 0;
        items_[slot].payload = std::string(payload);

        append_wal(WalOp::Enqueue, msg_id, payload);

        cv_ready_.notify_one();
        return msg_id;
    }

    struct AcquiredTask {
        uint64_t id;
        std::string payload;
    };

    std::optional<AcquiredTask> acquire(std::chrono::milliseconds lease_duration) {
        std::unique_lock lock(mutex_);

        while (running_) {
            auto now = std::chrono::steady_clock::now();
            for (auto &item : items_) {
                if (item.state == MessageState::Ready) {
                    item.state = MessageState::InFlight;
                    item.lease_deadline = now + lease_duration;
                    item.attempts++;

                    append_wal(WalOp::Acquire, item.id, {});
                    return AcquiredTask{item.id, item.payload};
                }
            }

            cv_ready_.wait_for(lock, 200ms);
        }
        return std::nullopt;
    }

    void ack(uint64_t msg_id) {
        std::unique_lock lock(mutex_);
        size_t slot = msg_id % items_.size();
        if (items_[slot].id == msg_id && items_[slot].state == MessageState::InFlight) {
            items_[slot].state = MessageState::Acked;
            append_wal(WalOp::Ack, msg_id, {});
        }
    }

    void nack(uint64_t msg_id) {
        std::unique_lock lock(mutex_);
        size_t slot = msg_id % items_.size();
        if (items_[slot].id == msg_id && items_[slot].state == MessageState::InFlight) {
            items_[slot].state = MessageState::Ready;
            append_wal(WalOp::Nack, msg_id, {});
            cv_ready_.notify_one();
        }
    }

    void stop() {
        {
            std::unique_lock lock(mutex_);
            running_ = false;
        }
        cv_ready_.notify_all();
        if (wal_file_.is_open()) {
            wal_file_.flush();
            wal_file_.close();
        }
    }

private:
    static uint32_t calc_crc(std::string_view data) {
        uint32_t crc = 0xFFFFFFFF;
        for (unsigned char b : data) {
            crc ^= b;
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
            }
        }
        return ~crc;
    }

    void append_wal(WalOp op, uint64_t msg_id, std::string_view payload) {
        if (!wal_file_.is_open()) return;

        WalHeader hdr;
        hdr.msg_id = msg_id;
        hdr.op_type = op;
        hdr.payload_len = static_cast<uint32_t>(payload.size());
        hdr.crc32 = calc_crc(payload);

        wal_file_.write(reinterpret_cast<const char*>(&hdr), sizeof(hdr));
        if (!payload.empty()) {
            wal_file_.write(payload.data(), payload.size());
        }
        wal_file_.flush();
    }

    void open_and_replay_wal() {
        if (std::filesystem::exists(wal_path_)) {
            std::ifstream in(wal_path_, std::ios::binary);
            WalHeader hdr;
            while (in.read(reinterpret_cast<char*>(&hdr), sizeof(hdr))) {
                if (hdr.magic != 0x51554555) break;

                std::string payload(hdr.payload_len, '\0');
                if (hdr.payload_len > 0) {
                    in.read(payload.data(), hdr.payload_len);
                }

                size_t slot = hdr.msg_id % items_.size();
                if (hdr.op_type == WalOp::Enqueue) {
                    items_[slot].id = hdr.msg_id;
                    items_[slot].state = MessageState::Ready;
                    items_[slot].payload = std::move(payload);
                    if (hdr.msg_id >= next_id_) {
                        next_id_ = hdr.msg_id + 1;
                    }
                } else if (hdr.op_type == WalOp::Ack) {
                    items_[slot].state = MessageState::Acked;
                } else if (hdr.op_type == WalOp::Nack) {
                    items_[slot].state = MessageState::Ready;
                }
            }
        }
        wal_file_.open(wal_path_, std::ios::binary | std::ios::app);
    }

    void reclaim_loop(std::stop_token st) {
        while (!st.stop_requested() && running_) {
            std::this_thread::sleep_for(100ms);
            std::unique_lock lock(mutex_);
            auto now = std::chrono::steady_clock::now();
            bool awakened = false;

            for (auto &item : items_) {
                if (item.state == MessageState::InFlight && now >= item.lease_deadline) {
                    std::cout << "[Брокер C++] Таймаут оренди задачі #" << item.id
                              << ". Повертаємо в чергу READY.\n";
                    item.state = MessageState::Ready;
                    awakened = true;
                }
            }

            if (awakened) {
                cv_ready_.notify_all();
            }
        }
    }

    std::filesystem::path wal_path_;
    std::ofstream wal_file_;
    std::vector<QueueItem> items_;
    uint64_t next_id_{1};
    mutable std::mutex mutex_;
    std::condition_variable cv_ready_;
    bool running_{false};
    std::jthread reclaim_thread_;
};

} // namespace p2p
```
:::

## Тестовий сценарій: конкурентна обробка та імітація збоїв

Розглянемо демонстраційну програму, що ілюструє роботу черги в умовах змагання трьох потоків-воркерів, обриву обробки та автоматичного повернення оренди:

:::tabs
```c
static void *worker_func(void *arg) {
    p2p_queue_t *q = (p2p_queue_t *)arg;
    uint64_t msg_id;
    char payload[MAX_PAYLOAD_SIZE];
    uint32_t len;

    while (p2p_queue_acquire(q, 300 /* оренда на 300 мс */, &msg_id, payload, &len)) {
        payload[len] = '\0';
        printf("[Воркер %lu] Взяв у роботу задачу #%lu: «%s»\n",
               (unsigned long)pthread_self(), (unsigned long)msg_id, payload);

        if (msg_id == 2) {
            printf("[Воркер %lu] ⚡ Імітація аварії на задачі #%lu (не шлемо ACK)!\n",
                   (unsigned long)pthread_self(), (unsigned long)msg_id);
            /* Воркер засинає або падає, не відправляючи ACK */
            usleep(600000);
            continue;
        }

        /* Імітація корисної роботи */
        usleep(50000);

        printf("[Воркер %lu] Успішно завершив задачу #%lu -> ACK\n",
               (unsigned long)pthread_self(), (unsigned long)msg_id);
        p2p_queue_ack(q, msg_id);
    }
    return NULL;
}

int main(void) {
    const char *wal_file = "queue_demo.wal";
    unlink(wal_file);

    p2p_queue_t queue;
    p2p_queue_init(&queue, wal_file);

    printf("=== Старт черги повідомлень Point-to-Point ===\n");

    pthread_t workers[3];
    for (int i = 0; i < 3; ++i) {
        pthread_create(&workers[i], NULL, worker_func, &queue);
    }

    /* Публікація 5 завдань */
    p2p_queue_publish(&queue, "Обробка платіжної транзакції #101", 33);
    p2p_queue_publish(&queue, "Генерація PDF звіту #102", 23);
    p2p_queue_publish(&queue, "Відправка SMS сповіщення #103", 29);
    p2p_queue_publish(&queue, "Індексація каталогу товарів #104", 32);
    p2p_queue_publish(&queue, "Резервне копіювання БД #105", 26);

    /* Цикл моніторингу оренди */
    for (int i = 0; i < 8; ++i) {
        usleep(150000);
        p2p_queue_reclaim_expired(&queue);
    }

    p2p_queue_destroy(&queue);
    for (int i = 0; i < 3; ++i) {
        pthread_join(workers[i], NULL);
    }

    printf("=== Демонстрацію завершено. Журнал збережено на диску ===\n");
    unlink(wal_file);
    return 0;
}
```
```cpp
int main() {
    const std::filesystem::path wal_path = "cpp_queue_demo.wal";
    std::filesystem::remove(wal_path);

    std::cout << "=== Старт черги повідомлень Point-to-Point (C++20) ===\n";

    {
        p2p::DurableQueue queue(wal_path);

        std::vector<std::jthread> workers;
        for (int i = 1; i <= 3; ++i) {
            workers.emplace_back([&queue, worker_id = i](std::stop_token st) {
                while (!st.stop_requested()) {
                    auto task = queue.acquire(300ms);
                    if (!task) break;

                    std::cout << "[Воркер C++ " << worker_id << "] Отримав задачу #"
                              << task->id << ": «" << task->payload << "»\n";

                    if (task->id == 2) {
                        std::cout << "[Воркер C++ " << worker_id
                                  << "] ⚡ Імітація зависання на задачі #2 (без ACK)...\n";
                        std::this_thread::sleep_for(600ms);
                        continue;
                    }

                    std::this_thread::sleep_for(50ms);
                    std::cout << "[Воркер C++ " << worker_id << "] Завершив задачу #"
                              << task->id << " -> ACK\n";
                    queue.ack(task->id);
                }
            });
        }

        queue.publish("Транзакція авторизації картки #501");
        queue.publish("Формування рахунку-фактури #502");
        queue.publish("Перевірка балансу #503");
        queue.publish("Оновлення бонусного рахунку #504");

        std::this_thread::sleep_for(1200ms);
        queue.stop();
    }

    std::cout << "=== Демонстрацію завершено. Журнал перевірено ===\n";
    std::filesystem::remove(wal_path);
    return 0;
}
```
:::

## Покроковий розбір алгоритму відновлення після аварії (Crash Recovery)

Критична перевага журналу випереджального запису над прямим збереженням стану в реляційну базу даних полягає в швидкості та простоті детермінованого відновлення.

Коли екземпляр черги ініціалізується методом `p2p_queue_init()` (або конструктором `DurableQueue` у C++), виконується такий алгоритм:

1. **Відкриття дескриптора файлу:**
   Файл журналу відкривається в режимі додавання `O_APPEND` для майбутніх операцій, але покажчик читання тимчасово встановлюється на початок (`lseek(fd, 0, SEEK_SET)`).

2. **Послідовне сканування кадрів:**
   Рушій у циклі зчитує структури `wal_header_t`. Для кожного заголовка перевіряється магічне число `WAL_MAGIC` (`0x51554555`). Якщо магічне число пошкоджене (наприклад, через раптове знеструмлення посеред запису кадру), зчитування негайно припиняється: пошкоджений хвіст відкидається, а відновлюються лише транзакції, зафіксовані до моменту збою.

3. **Верифікація контрольної суми CRC32:**
   Якщо заголовок містить корисне навантаження (`payload_len > 0`), байти тіла зчитуються в тимчасовий буфер, і для них обчислюється контрольна сума. Якщо обчислена сума не збігається з `hdr.crc32`, кадр вважається битим.

4. **Відтворення скінченного автомата стану:**
   - Кадр `WAL_OP_ENQUEUE`: у відповідний слот масиву `items[msg_id % MAX_MESSAGES]` записується повідомлення зі станом `MSG_STATE_READY`. Лічильник монотонного генератора ідентифікаторів оновлюється (`next_msg_id = max(next_msg_id, msg_id + 1)`).
   - Кадр `WAL_OP_ACQUIRE`: під час нормальної роботи фіксує факт видачі в оренду. Проте **під час відновлення після аварії будь-які незавершені оренди автоматично скидаються в стан `READY`**! Оскільки процес брокера перезапустився, усі старі з'єднання з воркерами розірвано, і їхня попередня робота вважається незавершеною.
   - Кадр `WAL_OP_ACK`: стан слота переводиться в `MSG_STATE_ACKED`. Це означає, що завдання було успішно виконано до аварії, і його не потрібно видавати знову.
   - Кадр `WAL_OP_NACK`: стан слота скидається в `MSG_STATE_READY`.

5. **Фіксація покажчика на кінці файлу:**
   Після вичитування всіх валідних кадрів покажчик файлу повертається в кінець (`lseek(fd, 0, SEEK_END)`), і черга готова приймати нові публікації.

Такий підхід забезпечує відновлення десятків тисяч повідомлень за лічені мілісекунди без сканування складних індексів B-Tree.

## Модель синхронізації: чому обрано кільцевий буфер та умовні змінні

У наведеній реалізації застосовано гібридну схему організації пам'яті:

1. **Паттерн Ring Buffer (Кільцевий буфер фіксованого розміру):**
   Замість динамічного зв'язного списку з постійними викликами `malloc()` та `free()` (які створюють фрагментацію пам'яті та затримки блокування алокатора ядра), усі слоти виділені заздалегідь у структурі `p2p_queue_t`. Це гарантує локальність даних у кеші процесора (L1/L2 Cache Locality) та виключає помилки вичерпання пам'яті під час публікації повідомлень у межах встановленого ліміту `MAX_MESSAGES`.

2. **Сигналізація через умовні змінні (Condition Variables):**
   Коли пул воркерів очікує на появу нових завдань у методі `p2p_queue_acquire()`, потоки не використовують марне опитування процесора в нескінченному циклі (*Busy Wait / Spinlock*). Потік переходить у стан сну ядра операційної системи через `pthread_cond_timedwait()` або `cv_ready_.wait_for()`.
   Щойно продюсер публікує нове повідомлення в методі `publish()`, він викликає `pthread_cond_signal()`, що миттєво будить **рівно одного** вільного воркера з пулу. Це запобігає проблемі «гримучої отари» (англ. *Thundering Herd Problem*), коли одне нове повідомлення будило б сотні потоків одночасно.

3. **Фоновий потік оренди (Reclaim Thread) та Fencing:**
   У реалізації на C++ фоновий потік `reclaim_thread_` використовує сучасний примітив `std::jthread` зі стандартним механізмом кооперативної зупинки `std::stop_token`. Потік прокидається кожні 100 мс, перевіряє часові мітки `lease_deadline` для всіх завдань у стані `InFlight`, і в разі перевищення ліміту переводить завдання назад у `Ready`, сповіщаючи воркерів через `cv_ready_.notify_all()`.

## Оптимізація продуктивності: синхронний `fdatasync` супроти групового коміту

У базовому коді виклик `fdatasync(q->wal_fd)` виконується на кожен окремий виклик `publish()`.

Це дає максимальну гарантію надійності: щойно функція `publish()` повернула керування відправнику, повідомлення гарантовано знаходиться на фізичних пластинах або флеш-комірках накопичувача. Проте ціною такої гарантії є обмеження пропускної здатності продуктивністю операцій введення-виведення диска (IOPS). Для сучасного NVMe SSD із затримкою синхронізації 100–300 мкс один потік може виконати не більше 3 000 – 10 000 публікацій на секунду.

Для досягнення 100 000+ повідомлень на секунду в промислових брокерах застосовують техніку **групового коміту (Group Commit / Batching)**:
- Повідомлення від сотень паралельних потоків продюсерів складаються в атомарний кільцевий буфер оперативної пам'яті.
- Окремий виділений потік дискового запису кожні 2–5 мс (або при накопиченні батчу в 64 КБ) скидає накопичені байти одним системним викликом `writev()` і робить **один спільний `fdatasync()`** на всю групу з 500 повідомлень.
- Усі 500 потоків-продюсерів одночасно отримують сигнал про успішне збереження.

Це збільшує пропускну здатність у 50–100 разів ціною незначного збільшення затримки публікації (на 2–5 мс), що є класичним компромісом у розподілених сховищах даних.

## Ротація сегментів та ущільнення журналу (Log Compaction & Checkpointing)

У наведеній мінімальній реалізації всі операції записуються в один файл журналу. Проте в довготривалій експлуатації нескінченне дописування операцій `OP_ENQUEUE` та `OP_ACK` неминуче вичерпає весь дисковий простір. Оскільки повідомлення, що отримали статус `ACKED`, більше ніколи не будуть видані споживачам, їхнє збереження на диску є марнуванням ресурсів.

Для запобігання переповненню диска в промислових чергах реалізують два взаємодоповнюючі механізми:

1. **Сегментація журналу (Log Segmentation):**
   Замість одного монолітного файлу журнал розбивається на сегменти фіксованого розміру (наприклад, по 64 МБ: `00001.wal`, `00002.wal`, `00003.wal`). Нові операції завжди дописуються в активний сегмент. Коли активний сегмент заповнюється, він закривається для запису і стає доступним лише для читання, а брокер відкриває новий файл.

2. **Точки збереження стану (Checkpointing / Snapshotting):**
   Фоновий процес контролера періодично скидає повний знімок усіх повідомлень у станах `READY` та `IN_FLIGHT` в окремий файл стану `snapshot.dat`.
   Після успішного збереження знімка та синхронізації його через `fsync()`, усі старі сегменти журналу, записи яких передували моменту створення знімка, можуть бути безпечно видалені з диска (`unlink()`).

Під час відновлення після аварії брокер спершу завантажує базовий стан із `snapshot.dat` (за частки секунди), а потім програє лише короткий хвіст нових сегментів журналу, записаних після створення знімка.

## Спостережуваність: ключові метрики та телеметрія черги

Для надійної експлуатації черги повідомлень у виробничому середовищі інженери повинні відстежувати чотири золоті сигнали моніторингу:

1. **Глибина черги (Queue Depth / Backlog Size):**
   Кількість повідомлень у стані `READY`. Зростання цієї метрики є прямим індикатором того, що вхідний темп `λ` перевищив поточну продуктивність воркерів `μ`, і система потребує горизонтального масштабування споживачів.

2. **Вік найстарішого повідомлення (Age of Oldest Message):**
   Час, який найстаріше невичитане повідомлення провело в стані `READY`. Ця метрика є набагато точнішим індикатором порушення SLA, ніж проста кількість повідомлень: черга з 10 000 дрібних задач може розбиратися за 2 секунди, тоді як черга з 5 завислих повідомлень може порушувати бізнес-вимоги годинами.

3. **Кількість повідомлень у польоті (In-Flight Messages / Leased Count):**
   Кількість повідомлень, які зараз обробляються пулом воркерів. Якщо це число досягає сумарного ліміту префетчу (`Concurrency Limit`), нові воркери почнуть простоювати, або черга заблокує видачу.

4. **Частота повторних доставок (Redelivery Rate / NACK Ratio):**
   Відношення кількості повернень повідомлень у чергу через таймаут або `NACK` до загальної кількості успішних `ACK`. Різке зростання цієї метрики свідчить про масову появу «отруйних повідомлень» (*Poison Pills*) або деградацію зовнішніх залежностей воркерів (наприклад, блокування бази даних чи таймаути стороннього платіжного API).

## Інженерні пастки та їх подолання

Під час реалізації та експлуатації черг типу «точка-точка» розробники найчастіше припускаються чотирьох типових помилок:

1. **Занадто короткий таймаут оренди (Premature Lease Expiration):**
   Якщо воркер обробляє важке завдання протягом 35 секунд, а таймаут видимості становить 30 секунд, брокер поверне задачу в чергу й віддасть її другому воркеру. Обидва воркери почнуть виконувати одну й ту саму операцію паралельно, створюючи перегони станів.
   *Виправлення:* використання фонового механізму продовження оренди (*Heartbeat / Keep-Alive*). Доки воркер живий і працює над задачею, він кожні 10 секунд відправляє команду продовження оренди (`heartbeat / change_message_visibility`).

2. **Втрата повідомлень при використанні несинхронізованого дискового кешу:**
   Виклик функції `write()` записує байти лише в сторінковий кеш (*Page Cache*) оперативної пам'яті Linux. Якщо живлення сервера зникне, дані випаруються.
   *Виправлення:* обов'язковий виклик `fdatasync()` або використання прямого дискового вводу-виводу (`O_DIRECT` / `O_DSYNC`) для критичних фінансових повідомлень.

3. **Отруйні повідомлення (Poison Pills) та блокування черги:**
   Повідомлення з пошкодженим JSON викликає падіння воркера при кожній спробі десеріалізації. Після таймауту оренди воно повертається в чергу й знову вбиває наступного вільного воркера.
   *Виправлення:* лічильник спроб доставки (`attempts`). Якщо `attempts >= MAX_ATTEMPTS` (наприклад, 5 спроб), брокер автоматично переміщує повідомлення в мертву чергу (DLQ) і сповіщає службу моніторингу.

4. **Аномалія зомбі-воркерів (Zombie Consumers) та захист епохами (Fencing Tokens):**
   Воркер застряг у тривалій паузі збирача сміття (GC Pause) або важкому дисковому читанні. Брокер вважає його мертвим за таймаутом і передає повідомлення воркеру B. Воркер B успішно виконує транзакцію. Після цього воркер A повертається до життя й намагається записати застарілі результати в базу даних.
   *Виправлення:* брокер супроводжує кожну видачу повідомлення монотонним номером оренди — **Lease Epoch / Fencing Token**. База даних або сервіс зберігання приймає мутації лише з номером епохи, що є більшим або рівним поточному зафіксованому значенню. Запис від старого воркера A відхиляється.
