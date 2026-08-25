# ⚙️ Пул конкурентних споживачів: оренда повідомлень, поновлення лізи та захист від отрути

Розподілена черга задач стикається з трьома критичними ризиками під час паралельної обробки пулом воркерів:
1. **Збій воркера посеред виконання:** повідомлення має бути надійно повернене в чергу й передане іншому доступному воркеру без втрати бізнес-даних.
2. **Передчасне завершення оренди (Visibility Timeout Race):** якщо воркер виконує важку задачу довше за стандартний таймаут видимості, брокер помилково вирішить, що воркер загинув, і віддасть ту саму задачу другому споживачу. Це спричиняє паралельне подвійне виконання.
3. **Отруйні повідомлення (Poison Pills):** некоректні дані, які викликають збій або аварійне завершення обробника, не повинні нескінченно повертатися в чергу й валити воркери по колу; після ліміту спроб їх слід ізолювати в мертву чергу (DLQ).

Нижче наведено робочу реалізацію конкурентного пулу споживачів, що імітує поведінку промислового брокера повідомлень з підтримкою оренди (*message leasing*), таймаутів видимості (*visibility timeouts*), фонового поновлення оренди (*heartbeat lease renewal*), лічильника спроб доставки та маршрутизації в мертву чергу (DLQ).

## Архітектура моделі та скінченний автомат стану повідомлення

У нашій моделі брокер черги оперує повідомленнями, кожне з яких описується структурою з ідентифікатором, корисним навантаженням (*payload*), тривалістю виконання, лічильником спроб та часовою міткою закінчення оренди `lease_expiry`.

Повідомлення проходить через скінченний автомат із чотирьох станів:
- `AVAILABLE` (Доступне) — повідомлення знаходиться в загальній черзі й готове до видачі будь-якому вільному воркеру;
- `IN_FLIGHT` (В обробці) — повідомлення тимчасово видане конкретному воркеру на фіксований інтервал оренди (таймаут видимості). Для інших воркерів воно стає невидимим;
- `COMPLETED` (Завершене) — воркер надіслав явне підтвердження успіху (`ACK`), після чого повідомлення вважається успішно виконаним і вилучається з обробки;
- `DEAD` (Мертве) — кількість невдалих спроб обробки перевищила ліміт `MAX_DELIVERY_ATTEMPTS`. Брокер перехоплює таке повідомлення й ізолює його в DLQ, припиняючи видачу воркерам.

```
       [Публікація продюсером]
                 │
                 ▼
          ┌─────────────┐
          │  AVAILABLE  │ ◄──────────────────────┐
          └──────┬──────┘                        │
                 │                               │
        Оренда (acquireLease)             NACK / Таймаут
                 │                         (спроби ≤ MAX)
                 ▼                               │
          ┌─────────────┐                        │
          │  IN_FLIGHT  ├────────────────────────┤
          └──────┬──────┘                        │
                 │                               │
         ┌───────┴────────┐                      │
         │                │                      │
   ACK (успіх)      NACK / Таймаут               │
         │          (спроби > MAX)               │
         ▼                ▼                      │
  ┌─────────────┐  ┌─────────────┐               │
  │  COMPLETED  │  │    DEAD     │ (DLQ ізоляція)│
  └─────────────┘  └─────────────┘               │
```

Кожен воркер у пулі функціонує в незалежному потоці виконання. Якщо час виконання задачі перевищує встановлений таймаут видимості, воркер запускає фоновий механізм *heartbeat*, який періодично подовжує час оренди повідомлення в брокера, запобігаючи передчасній повторній видачі задачі іншим споживачам.

## Реалізація пулу споживачів: C та C++

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>

#define MAX_QUEUE_CAPACITY 64
#define MAX_WORKERS 4
#define DEFAULT_VISIBILITY_TIMEOUT_SEC 2
#define MAX_DELIVERY_ATTEMPTS 3

typedef enum {
    MSG_AVAILABLE,
    MSG_IN_FLIGHT,
    MSG_COMPLETED,
    MSG_DEAD
} msg_state_t;

typedef struct {
    int id;
    char payload[64];
    int work_duration_sec;    /* скільки секунд триває робота */
    bool should_fail;         /* чи імітує повідомлення збій */
    int delivery_count;       /* кількість спроб доставки */
    time_t lease_expiry;      /* момент закінчення оренди (UNIX timestamp) */
    msg_state_t state;
} message_t;

typedef struct {
    message_t items[MAX_QUEUE_CAPACITY];
    int count;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    bool is_shutdown;
} queue_broker_t;

/* Ініціалізація брокера черги */
void queue_init(queue_broker_t *q) {
    memset(q, 0, sizeof(*q));
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    q->is_shutdown = false;
}

/* Знищення ресурсів брокера */
void queue_destroy(queue_broker_t *q) {
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_empty);
}

/* Публікація повідомлення продюсером */
bool queue_publish(queue_broker_t *q, int id, const char *payload, int duration_sec, bool fail) {
    pthread_mutex_lock(&q->lock);
    if (q->count >= MAX_QUEUE_CAPACITY) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    message_t *m = &q->items[q->count++];
    m->id = id;
    strncpy(m->payload, payload, sizeof(m->payload) - 1);
    m->payload[sizeof(m->payload) - 1] = '\0';
    m->work_duration_sec = duration_sec;
    m->should_fail = fail;
    m->delivery_count = 0;
    m->lease_expiry = 0;
    m->state = MSG_AVAILABLE;

    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

/* Отримання задачі воркером з орендою на visibility_sec */
message_t* queue_receive_lease(queue_broker_t *q, int worker_id, int visibility_sec) {
    pthread_mutex_lock(&q->lock);
    time_t now;

    while (!q->is_shutdown) {
        now = time(NULL);
        message_t *chosen = NULL;

        /* Шукаємо повідомлення: або доступне нове, або прострочене In-Flight */
        for (int i = 0; i < q->count; ++i) {
            message_t *m = &q->items[i];
            if (m->state == MSG_AVAILABLE) {
                chosen = m;
                break;
            } else if (m->state == MSG_IN_FLIGHT && m->lease_expiry <= now) {
                printf("[Broker] Оренда для M#%d минула! Повторна видача.\n", m->id);
                chosen = m;
                break;
            }
        }

        if (chosen != NULL) {
            chosen->delivery_count++;
            if (chosen->delivery_count > MAX_DELIVERY_ATTEMPTS) {
                printf("[Broker → DLQ] M#%d перевищив ліміт спроб (%d) -> Мертва черга!\n",
                       chosen->id, chosen->delivery_count);
                chosen->state = MSG_DEAD;
                continue; /* шукаємо далі */
            }

            chosen->state = MSG_IN_FLIGHT;
            chosen->lease_expiry = now + visibility_sec;
            pthread_mutex_unlock(&q->lock);
            return chosen;
        }

        /* Якщо готових задач немає, очікуємо сигналу або таймауту 1 секунда */
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        ts.tv_sec += 1;
        pthread_cond_timedwait(&q->not_empty, &q->lock, &ts);
    }

    pthread_mutex_unlock(&q->lock);
    return NULL;
}

/* Подовження оренди повідомлення (Heartbeat) */
bool queue_renew_lease(queue_broker_t *q, int msg_id, int additional_sec) {
    pthread_mutex_lock(&q->lock);
    time_t now = time(NULL);

    for (int i = 0; i < q->count; ++i) {
        message_t *m = &q->items[i];
        if (m->id == msg_id && m->state == MSG_IN_FLIGHT) {
            m->lease_expiry = now + additional_sec;
            pthread_mutex_unlock(&q->lock);
            return true;
        }
    }

    pthread_mutex_unlock(&q->lock);
    return false;
}

/* Підтвердження успішної обробки (ACK) */
void queue_ack(queue_broker_t *q, int msg_id) {
    pthread_mutex_lock(&q->lock);
    for (int i = 0; i < q->count; ++i) {
        message_t *m = &q->items[i];
        if (m->id == msg_id && m->state == MSG_IN_FLIGHT) {
            m->state = MSG_COMPLETED;
            printf("[Broker] ACK підтверджено для M#%d -> Завершено.\n", msg_id);
            break;
        }
    }
    pthread_mutex_unlock(&q->lock);
}

/* Відмова від обробки (NACK) з негайним поверненням у чергу */
void queue_nack(queue_broker_t *q, int msg_id) {
    pthread_mutex_lock(&q->lock);
    for (int i = 0; i < q->count; ++i) {
        message_t *m = &q->items[i];
        if (m->id == msg_id && m->state == MSG_IN_FLIGHT) {
            m->state = MSG_AVAILABLE;
            m->lease_expiry = 0;
            printf("[Broker] NACK отримано для M#%d -> Повернуто в чергу.\n", msg_id);
            pthread_cond_signal(&q->not_empty);
            break;
        }
    }
    pthread_mutex_unlock(&q->lock);
}

/* Контекст потоку воркера */
typedef struct {
    int worker_id;
    queue_broker_t *broker;
} worker_ctx_t;

/* Головний цикл воркера */
void* worker_thread_fn(void *arg) {
    worker_ctx_t *ctx = (worker_ctx_t*)arg;
    printf("[Worker-%d] Запущено й готовий до прийому задач.\n", ctx->worker_id);

    while (!ctx->broker->is_shutdown) {
        message_t *msg = queue_receive_lease(ctx->broker, ctx->worker_id, DEFAULT_VISIBILITY_TIMEOUT_SEC);
        if (msg == NULL) {
            if (ctx->broker->is_shutdown) break;
            continue;
        }

        int msg_id = msg->id;
        int duration = msg->work_duration_sec;
        bool should_fail = msg->should_fail;

        printf("[Worker-%d] Взяв M#%d («%s»), час: %d с (спроба %d)\n",
               ctx->worker_id, msg_id, msg->payload, duration, msg->delivery_count);

        /* Імітація обробки з фоновим поновленням лізи */
        int elapsed = 0;
        bool failed = false;

        while (elapsed < duration) {
            sleep(1);
            elapsed++;

            if (should_fail && elapsed >= 1) {
                printf("[Worker-%d] ✖ Помилка обробки M#%d!\n", ctx->worker_id, msg_id);
                queue_nack(ctx->broker, msg_id);
                failed = true;
                break;
            }

            /* Якщо задача довга, кожну секунду поновлюємо лізу на 2 секунди */
            if (elapsed < duration) {
                queue_renew_lease(ctx->broker, msg_id, DEFAULT_VISIBILITY_TIMEOUT_SEC);
                printf("[Worker-%d] ⟳ Поновлено лізу для M#%d (пройшло %d/%d с)\n",
                       ctx->worker_id, msg_id, elapsed, duration);
            }
        }

        if (!failed) {
            queue_ack(ctx->broker, msg_id);
            printf("[Worker-%d] ✔ Успішно виконано M#%d\n", ctx->worker_id, msg_id);
        }
    }

    printf("[Worker-%d] Зупиняється.\n", ctx->worker_id);
    return NULL;
}

int main(void) {
    queue_broker_t broker;
    queue_init(&broker);

    pthread_t threads[MAX_WORKERS];
    worker_ctx_t contexts[MAX_WORKERS];

    for (int i = 0; i < MAX_WORKERS; ++i) {
        contexts[i].worker_id = i + 1;
        contexts[i].broker = &broker;
        pthread_create(&threads[i], NULL, worker_thread_fn, &contexts[i]);
    }

    /* Публікація тестових задач */
    queue_publish(&broker, 101, "Швидка задача (1с)", 1, false);
    queue_publish(&broker, 102, "Важка задача (4с + Heartbeat)", 4, false);
    queue_publish(&broker, 103, "Отруйна задача (викличе збій)", 1, true);
    queue_publish(&broker, 104, "Звичайна задача (2с)", 2, false);

    /* Чекаємо завершення обробки задач */
    sleep(7);

    /* Коректна зупинка пулу (Graceful Shutdown) */
    pthread_mutex_lock(&broker.lock);
    broker.is_shutdown = true;
    pthread_cond_broadcast(&broker.not_empty);
    pthread_mutex_unlock(&broker.lock);

    for (int i = 0; i < MAX_WORKERS; ++i) {
        pthread_join(threads[i], NULL);
    }

    queue_destroy(&broker);
    printf("Всі воркери коректно зупинені.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <optional>
#include <memory>
#include <atomic>
#include <stop_token>

using namespace std::chrono_literals;

enum class MessageState {
    Available,
    InFlight,
    Completed,
    Dead
};

struct Message {
    int id;
    std::string payload;
    std::chrono::seconds workDuration;
    bool shouldFail;
    int deliveryCount{0};
    std::chrono::steady_clock::time_point leaseExpiry;
    MessageState state{MessageState::Available};
};

class CompetingQueueBroker {
public:
    explicit CompetingQueueBroker(int maxCapacity = 64, int maxAttempts = 3)
        : maxCapacity_(maxCapacity), maxDeliveryAttempts_(maxAttempts) {}

    bool publish(int id, std::string payload, std::chrono::seconds duration, bool shouldFail) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (messages_.size() >= maxCapacity_) {
            return false;
        }

        messages_.push_back(std::make_unique<Message>(Message{
            id,
            std::move(payload),
            duration,
            shouldFail,
            0,
            std::chrono::steady_clock::time_point{},
            MessageState::Available
        }));

        cv_.notify_one();
        return true;
    }

    // Оренда задачі воркером з контролем таймауту видимості
    std::unique_ptr<Message>* acquireLease(std::chrono::seconds visibilityTimeout, std::stop_token stopToken) {
        std::unique_lock<std::mutex> lock(mutex_);

        while (!stopToken.stop_requested() && !isShutdown_) {
            auto now = std::chrono::steady_clock::now();
            std::unique_ptr<Message>* candidate = nullptr;

            for (auto& msg : messages_) {
                if (msg->state == MessageState::Available) {
                    candidate = &msg;
                    break;
                }
                if (msg->state == MessageState::InFlight && msg->leaseExpiry <= now) {
                    std::cout << "[Broker] Таймаут оренди для M#" << msg->id << " минув! Повторна видача.\n";
                    candidate = &msg;
                    break;
                }
            }

            if (candidate) {
                auto& msg = *candidate;
                msg->deliveryCount++;
                if (msg->deliveryCount > maxDeliveryAttempts_) {
                    std::cout << "[Broker → DLQ] M#" << msg->id 
                              << " перевищив ліміт спроб -> Переміщено в мертву чергу!\n";
                    msg->state = MessageState::Dead;
                    continue;
                }

                msg->state = MessageState::InFlight;
                msg->leaseExpiry = now + visibilityTimeout;
                return candidate;
            }

            cv_.wait_for(lock, 500ms);
        }

        return nullptr;
    }

    void renewLease(int msgId, std::chrono::seconds additionalTime) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::steady_clock::now();
        for (auto& msg : messages_) {
            if (msg->id == msgId && msg->state == MessageState::InFlight) {
                msg->leaseExpiry = now + additionalTime;
                return;
            }
        }
    }

    void acknowledge(int msgId) {
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto& msg : messages_) {
            if (msg->id == msgId && msg->state == MessageState::InFlight) {
                msg->state = MessageState::Completed;
                std::cout << "[Broker] ACK підтверджено для M#" << msgId << " (Виконано).\n";
                return;
            }
        }
    }

    void reject(int msgId) {
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto& msg : messages_) {
            if (msg->id == msgId && msg->state == MessageState::InFlight) {
                msg->state = MessageState::Available;
                msg->leaseExpiry = {};
                std::cout << "[Broker] NACK для M#" << msgId << " -> Повернуто в чергу.\n";
                cv_.notify_one();
                return;
            }
        }
    }

    void shutdown() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            isShutdown_ = true;
        }
        cv_.notify_all();
    }

private:
    const size_t maxCapacity_;
    const int maxDeliveryAttempts_;
    std::vector<std::unique_ptr<Message>> messages_;
    std::mutex mutex_;
    std::condition_variable cv_;
    bool isShutdown_{false};
};

// RAII обгортка для подовження лізи (Heartbeat)
class LeaseHeartbeat {
public:
    LeaseHeartbeat(CompetingQueueBroker& broker, int msgId, std::chrono::seconds interval, std::chrono::seconds leaseDuration)
        : broker_(broker), msgId_(msgId), interval_(interval), leaseDuration_(leaseDuration), running_(true) {
        worker_ = std::jthread([this](std::stop_token st) {
            while (!st.stop_requested() && running_) {
                std::this_thread::sleep_for(interval_);
                if (!running_) break;
                broker_.renewLease(msgId_, leaseDuration_);
                std::cout << "[Heartbeat] ⟳ Поновлено оренду для M#" << msgId_ << "\n";
            }
        });
    }

    ~LeaseHeartbeat() {
        stop();
    }

    void stop() {
        running_ = false;
        if (worker_.joinable()) {
            worker_.request_stop();
        }
    }

private:
    CompetingQueueBroker& broker_;
    int msgId_;
    std::chrono::seconds interval_;
    std::chrono::seconds leaseDuration_;
    std::atomic<bool> running_{false};
    std::jthread worker_;
};

void runWorker(int workerId, CompetingQueueBroker& broker, std::stop_token stopToken) {
    std::cout << "[Worker-" << workerId << "] Запущено.\n";
    constexpr auto visibilityTimeout = 2s;

    while (!stopToken.stop_requested()) {
        auto* msgPtr = broker.acquireLease(visibilityTimeout, stopToken);
        if (!msgPtr || stopToken.stop_requested()) {
            break;
        }

        const auto& msg = **msgPtr;
        const int msgId = msg.id;
        const auto duration = msg.workDuration;
        const bool shouldFail = msg.shouldFail;

        std::cout << "[Worker-" << workerId << "] Взяв M#" << msgId 
                  << " («" << msg.payload << "»), час: " << duration.count() 
                  << "с (спроба " << msg.deliveryCount << ")\n";

        // Якщо робота перевищує половину таймауту видимості, вмикаємо фоновий Heartbeat
        std::optional<LeaseHeartbeat> heartbeat;
        if (duration >= visibilityTimeout) {
            heartbeat.emplace(broker, msgId, 1s, visibilityTimeout);
        }

        bool success = true;
        if (shouldFail) {
            std::this_thread::sleep_for(500ms);
            std::cout << "[Worker-" << workerId << "] ✖ Помилка обробки M#" << msgId << "!\n";
            heartbeat.reset();
            broker.reject(msgId);
            success = false;
        } else {
            std::this_thread::sleep_for(duration);
        }

        if (success) {
            heartbeat.reset();
            broker.acknowledge(msgId);
            std::cout << "[Worker-" << workerId << "] ✔ Успішно завершив M#" << msgId << "\n";
        }
    }

    std::cout << "[Worker-" << workerId << "] Зупинився.\n";
}

int main() {
    CompetingQueueBroker broker;
    std::vector<std::jthread> workers;

    for (int i = 1; i <= 4; ++i) {
        workers.emplace_back([i, &broker](std::stop_token st) {
            runWorker(i, broker, st);
        });
    }

    broker.publish(201, "Швидка задача (1с)", 1s, false);
    broker.publish(202, "Важка задача (4с + Heartbeat)", 4s, false);
    broker.publish(203, "Отруйна задача (викличе NACK)", 1s, true);
    broker.publish(204, "Паралельна задача (2с)", 2s, false);

    std::this_thread::sleep_for(7s);

    broker.shutdown();
    for (auto& w : workers) {
        w.request_stop();
    }

    std::cout << "Всі ресурси пулу успішно вивільнено.\n";
    return 0;
}
```
:::

## Покроковий розбір реалізації мовою C

Реалізація мовою C демонструє роботу розподіленого брокера на рівні низькорівневих системних примітивів POSIX Threads:

1. **Захист стану брокера (`pthread_mutex_t`):**
   Усі операції модифікації списку повідомлень — додавання нових задач (`queue_publish`), зміна статусу на `MSG_IN_FLIGHT` (`queue_receive_lease`), оновлення лізи (`queue_renew_lease`), а також фіксація `MSG_COMPLETED` чи повернення `MSG_AVAILABLE` — відбуваються строго під захистом блокування `q->lock`. Це повністю усуває стан гонки між паралельними воркерами, які одночасно звертаються до черги за новими задачами.

2. **Очікування та пробудження через умовні змінні (`pthread_cond_t`):**
   Коли в черзі немає доступних задач, потік воркера не витрачає процесорний час у холостому циклі (*busy waiting*). Він переходить у режим сну за допомогою виклику `pthread_cond_timedwait(&q->not_empty, &q->lock, &ts)`.
   Зверніть увагу: ми навмисно використовуємо `timedwait` із таймаутом у 1 секунду замість нескінченного `pthread_cond_wait`. Це необхідно тому, що повідомлення в стані `MSG_IN_FLIGHT` може стати простроченим у пам'яті брокера самостійно (внаслідок аварії іншого воркера), без виклику `queue_publish` чи нового сигналу. Періодичне пробудження кожну секунду гарантує, що вільний воркер помітить прострочену лізу й підхопить покинуту задачу.

3. **Двоетапне сканування черги:**
   Функція `queue_receive_lease` виконує пошук задачі за двома критеріями: спочатку перевіряються нові повідомлення зі статусом `MSG_AVAILABLE`, а потім — повідомлення `MSG_IN_FLIGHT`, чий дедлайн `lease_expiry` став меншим або рівним поточному моменту `now`. Якщо повідомлення перевищило `MAX_DELIVERY_ATTEMPTS` (3 невдалі спроби), брокер переводить його в статус `MSG_DEAD` (Dead Letter Queue) та продовжує пошук, не віддаючи зіпсований об'єкт воркеру.

4. **Коректне завершення роботи (Graceful Shutdown):**
   Функція зупинки блокує м'ютекс, виставляє прапорець `is_shutdown = true` і викликає широкомовне сповіщення `pthread_cond_broadcast(&broker.not_empty)`. Це миттєво будить усі сплячі воркер-потоки, які перевіряють прапорець зупинки, виходять із внутрішнього циклу `while (!is_shutdown)` і завершують своє виконання. Головний потік викликає `pthread_join`, гарантуючи, що жоден робочий потік не буде примусово обірвано посеред виконання.

## Покроковий розбір реалізації мовою C++20

Версія на сучасному C++20 демонструє ідіоматичний підхід до керування пам'яттю, потоками та виключеннями:

1. **Керування пам'яттю через розумні вказівники:**
   Усі повідомлення зберігаються у векторі `std::vector<std::unique_ptr<Message>>`. Це усуває необхідність ручного керування пам'яттю, запобігає витокам і забезпечує стабільність вказівників на об'єкти повідомлень у пам'яті навіть при додаванні нових елементів.

2. **Кооперативне скасування через `std::stop_token`:**
   У C++20 потоки `std::jthread` мають вбудовану підтримку механізму кооперативного переривання. Метод `acquireLease` приймає аргумент `std::stop_token`. Коли головний потік викликає `w.request_stop()`, воркер не вбивається операційною системою примусово; замість цього перевірка `stopToken.stop_requested()` повертає `true`, що дозволяє воркеру акуратно завершити поточну задачу, звільнити локальні структури даних і коректно вийти.

3. **Ідіома RAII для поновлення оренди (`LeaseHeartbeat`):**
   Клас `LeaseHeartbeat` використовує концепцію *Resource Acquisition Is Initialization*. Створення екземпляра класу автоматично запускає фоновий потік `std::jthread`, який періодично надсилає виклики `broker.renewLease(...)`.
   Коли обробка задачі завершується (успіхом або помилкою), викликається деструктор `~LeaseHeartbeat()` або метод `heartbeat.reset()`. Деструктор атомарно скидає прапорець `running_ = false` та надсилає запит на зупинку фонового потоку. Якщо під час обробки бізнес-логіки виникне виключення C++, стек автоматично розгорнеться (*stack unwinding*), деструктор коректно зупинить фоновий потік, і брокер поверне повідомлення іншим воркерам без зависання фонових демонів.

## Покрокове простеження виконання та аналіз консольного логу

Розглянемо, як виконується програма при публікації тестового набору задач:

```
[Worker-1] Запущено.
[Worker-2] Запущено.
[Worker-3] Запущено.
[Worker-4] Запущено.
[Worker-1] Взяв M#201 («Швидка задача (1с)»), час: 1с (спроба 1)
[Worker-2] Взяв M#202 («Важка задача (4с + Heartbeat)»), час: 4с (спроба 1)
[Worker-3] Взяв M#203 («Отруйна задача (викличе NACK)»), час: 1с (спроба 1)
[Worker-4] Взяв M#204 («Паралельна задача (2с)»), час: 2с (спроба 1)
```

1. **Паралельний розбір:** усі 4 воркери миттєво підхоплюють по одній задачі, розподіляючи навантаження на всі доступні ядра процесора.
2. **Обробка помилки та відкат (M#203):** через 500 мс Воркер 3 фіксує збій і викликає `reject()`. Брокер повертає задачу в чергу зі статусом `Available`.
3. **Захист важкої задачі через Heartbeat (M#202):**
   - Базовий таймаут видимості становить 2 секунди.
   - Воркер 2 на першій та другій секундах надсилає сигнали: `[Heartbeat] ⟳ Поновлено оренду для M#202`.
   - Брокер подовжує лізу, тому повідомлення `M#202` залишається невидимим для решти вільних воркерів.
4. **Повторні спроби та ізоляція в DLQ:**
   - Вільні Воркер 1 та Воркер 4 підхоплюють відхилену задачу `M#203`, намагаються її виконати й також зазнають збою (спроби 2 і 3).
   - На 4-й спробі брокер перехоплює повідомлення: `[Broker → DLQ] M#203 перевищив ліміт спроб -> Переміщено в мертву чергу!`.
5. **Фініш та Graceful Shutdown:** після 7 секунд роботи брокер викликає `shutdown()`, усі 4 воркери коректно завершують роботу й закривають потік.

## Глибокий аналіз паралелізму, моделі пам'яті та синхронізації

Розподілений або багатопотоковий пул конкурентних споживачів стикається з тонкими системними ефектами на рівні процесорних ядер та операційної системи.

### 1. Системні виклики та механізм Futex у Linux

У версії на мові C виклик `pthread_cond_timedwait` безпосередньо транслюється бібліотекою `glibc` у системний виклик ядра Linux `sys_futex` (*Fast Userspace Mutex*).

Механізм роботи futex мінімізує накладні витрати:
- **Швидкий шлях (Fast Path):** захоплення вільного м'ютекса виконується в просторі користувача за одну атомарну інструкцію процесора (`CMPXCHG` на архітектурі x86_64) без перемикання контексту в простір ядра.
- **Повільний шлях (Slow Path):** якщо м'ютекс зайнятий або черга порожня, потік робить системний виклик `futex(FUTEX_WAIT_BITSET)`, і планувальник ядра переводить потік у стан сну `TASK_INTERRUPTIBLE`, видаляючи його з черги виконання CPU до надходження сигналу або вичерпання дедлайну `timespec`.

Використання `timedwait` із фіксованим кроком в 1 секунду захищає систему від «забутих» повідомлень: якщо воркер впав без виклику `NACK`, брокер не надсилає явного сигналу `signal()`, але черговий прохід сплячих воркерів через секунду автоматично підхопить прострочену задачу.

### 2. Захист від гонки застарілої оренди: фенсинг-токени (Fencing Tokens)

У розподілених системах класичний таймаут видимості може підвести, якщо воркер зазнав тривалої зупинки збирача сміття (*Stop-the-World GC Pause*) або завис на дисковому I/O.

Розглянемо небезпечний сценарій:
1. Воркер 1 бере задачу `M#101` і засинає на 35 секунд через GC-паузу.
2. Брокер фіксує таймаут (30 с) і видає `M#101` Воркеру 2.
3. Воркер 2 успішно виконує задачу й записує результат у сховище.
4. Воркер 1 прокидається від GC-паузи, вважає, що він досі володіє задачею, і перезаписує результат Воркера 2 застарілими даними!

```
Захист через Fencing Token (монотонне покоління лізи):
Брокер генерує токен: [M#101, Generation = 1] ──> Воркер 1 (заснув на GC)
Брокер перевидає:     [M#101, Generation = 2] ──> Воркер 2 ──> Запис у БД (OK, Gen=2)
Воркер 1 прокидається: Спроба запису з Gen=1 ──> БД відхиляє: «Gen 1 < поточного 2!»
```

У нашій реалізації роль покоління виконує поле `delivery_count` (або монотонний лічильник `lease_epoch`). При записі в кінцеве сховище воркер зобов'язаний передавати поточний номер спроби, а база даних відхиляє будь-які зміни, якщо збережений номер версії є новішим.

### 3. Конфлікти блокувань (Lock Contention) та шардування черги

У наведеному прикладі всі воркери звертаються до єдиного м'ютекса `q->lock` (або `mutex_` у C++). При 4–8 потоках витрати на блокування складають менше 0.1% процесорного часу.

Проте при масштабуванні пулу до сотень потоків або десятків тисяч операцій на секунду єдиний м'ютекс стає пляшковим горлом через конфлікти кеш-ліній процесора (*Cache Line Bouncing* між ядрами).

Для подолання цієї проблеми у високонавантажених системах застосовують дві техніки:
- **Шардовані черги (Sharded Lock Queues):** замість однієї черги брокер підтримує масив із `N` незалежних підчерг (наприклад, 16 підчерг), кожна зі своїм власним м'ютексом. Воркери випадковим чином або через Round-Robin опитують різні шарди, знижуючи конкуренцію в 16 разів.
- **Кільцевий безблокувальний буфер (Lock-Free Ring Buffer / MPMC Queue):** використання атомарних покажчиків `std::atomic<size_t>` голови та хвоста черги з інструкціями `compare_exchange_weak`, що дозволяє воркерам забирати задачі без взаємного блокування потоків на рівні операційної системи.

### 4. Моделі пам'яті: послідовна узгодженість та бар'єри пам'яті

У багатопотокових пулах обробників коректність синхронізації залежить від апаратної моделі пам'яті (*Memory Model*):
- На архітектурі **x86_64** апаратне забезпечення надає сильну модель TSO (*Total Store Order*), де операції запису не переставляються між собою.
- На архітектурах **ARM64** (процесори Apple Silicon, AWS Graviton) та **POWER** модель пам'яті є слабою (*Weakly-Ordered*): процесор і компілятор мають право агресивно переставляти операції читання та запису заради оптимізації конвеєра.

У версії на C++ використання `std::atomic<bool>` гарантує коректну видимість змін між потоками. За замовчуванням операції виконуються з семантикою `std::memory_order_seq_cst` (строга послідовна узгодженість), що на процесорах ARM транслюється в асемблерні бар'єри `DMB ISH` (*Data Memory Barrier*).

Для оптимізації гарячого шляху в C++ можна перейти на семантику захоплення-вивільнення (*Acquire-Release semantics*):
- публікація повідомлення завершується записом прапорця з `std::memory_order_release` (інструкція `STLR` на ARM), що гарантує: усі дані структури `Message` зафіксовані в пам'яті до того, як прапорець стане видимим іншим ядрам;
- воркер вичитує прапорець із `std::memory_order_acquire` (інструкція `LDAR` на ARM), гарантуючи, що жодне наступне читання полів повідомлення не буде виконано раніше за успішну перевірку готовності.

### 5. Відкладена повторна доставка та експоненційний відкат (Exponential Backoff with Jitter)

У базовій реалізації відхилена задача (`NACK`) повертається в чергу негайно. Проте якщо збій викликаний тимчасовою недоступністю зовнішньої бази даних або платіжного шлюзу, миттєва повторна спроба гарантовано зазнає невдачі й лише спалить лічильник `delivery_count`.

У промислових системах черга підтримує **відкладену повторну доставку** (*Delayed Redelivery*):
- при отриманні `NACK` брокер не робить повідомлення доступним негайно, а переміщує його в чергу відкладених повідомлень із дедлайном;
- час затримки розраховується за формулою експоненційного відкату з випадковим джитером:
  ```
  Delay = min(MaxDelay, BaseDelay · 2^(attempt) + Random(0, Jitter))
  ```
- якщо `BaseDelay = 1 с`, то перша повторна спроба відбудеться через ~2 с, друга — через ~4 с, третя — через ~8 с. Це дає зовнішній системі час на самовідновлення без перевантаження лавиною повторних запитів.

## Інженерні пастки реалізації

1. **Гонка передчасного завершення оренди (Visibility Timeout Race):**
   Якщо задача виконується довше за таймаут видимості без фонового поновлення лізи (*Heartbeat*), брокер вважає воркера загиблим і повторно видає те саме повідомлення іншому воркеру. Коли перший воркер нарешті завершує роботу й надсилає `ACK`, другий воркер уже виконує ту саму дію повторно. Це руйнує узгодженість даних, якщо операція не є суворо ідемпотентною.

2. **Зациклення на отруйних повідомленнях (Poison Pill Storm):**
   Повідомлення з некоректним форматом або невалідною схемою викликає необроблене виключення чи аварійне завершення воркера. Без лічильника `delivery_count` та мертвої черги (DLQ) це повідомлення повертатиметься в чергу знову і знову, послідовно виводячи з ладу всі доступні інстанси воркерів у пулі.

3. **Коректне вимкнення (Graceful Shutdown) з незавершеними задачами:**
   Отримавши сигнал `SIGTERM`, воркер не повинен негайно обривати процес. Він зобов'язаний:
   - припинити вибірку нових повідомлень із черги (`stopToken.request_stop()`);
   - дочекатися завершення поточної ітерації активної задачі й відправити фінальний `ACK`;
   - якщо час очікування вичерпано (загальний deadline на зупинку), надіслати `NACK`, щоб брокер миттєво повернув задачу доступним вузлам, не чекаючи вичерпання таймауту видимості.

4. **Дрейф системного годинника при перевірці ліз:**
   У C версії використання функції `time(NULL)` або `CLOCK_REALTIME` піддається ризику стрибків системного часу при синхронізації через NTP. Якщо годинник раптово переведеться на 10 секунд назад, брокер не помітить закінчення оренди вчасно. У виробничих системах слід використовувати монотонні таймери (`clock_gettime(CLOCK_MONOTONIC)` або `std::chrono::steady_clock`), які гарантують безперервний і строгий поступ часу.

5. **Тестування відмовостійкості через хаос-інжиніринг (Chaos Engineering):**
   Перед розгортанням у промислове середовище пул споживачів має пройти тестування на стійкість до раптових зупинок. Штучне впорскування сигналів `SIGKILL` у випадкові моменти часу дозволяє переконатися, що брокер коректно повертає прострочені лізи за таймаутом, а воркери не створюють дублікатів даних завдяки перевірці унікальних ключів ідемпотентності.
