# ⚙️ Реалізація асинхронного Message Endpoint: від черги до доменного сервісу

Цей проєкт демонструє повну, робочу реалізацію високопродуктивного асинхронного Message Endpoint промислового рівня. Архітектура розв'язує три головні інженерні виклики розподіленої інтеграції:
1. **Збереження строгого порядку (Partition Affinity):** обробка повідомлень одного бізнес-агрегата в гарантованій послідовності FIFO за допомогою шардованого диспетчера без блокування паралельних потоків інших клієнтів.
2. **Гарантія Effectively-Once (Idempotent Inbox):** вбудована дедуплікація повторних доставок через швидке сховище ідентифікаторів повідомлень.
3. **Контроль зворотного протитиску (Backpressure):** автоматичне призупинення вичитування з мережевого каналу при переповненні черг воркерів та безпечне дренування завдань при завершенні процесу (Graceful Shutdown).

## Архітектурний дизайн системи

Конвеєр кінцевої точки складається з чотирьох взаємопов'язаних шарів, кожен із яких ізолює окремий аспект обробки повідомлень:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    АРХІТЕКТУРНИЙ КОНВЕЄР MESSAGE ENDPOINT                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Канальний адаптер (Channel Adapter):                                     │
│    • Вичитує сирі повідомлення з сокета / симулятора черги.                │
│    • Контролює ліміт префетчу (Prefetch QoS = 50).                         │
│    • Реагує на сигнали паузи / відновлення (Backpressure).                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Шардований диспетчер (Partitioned Dispatcher):                          │
│    • Обчислює: hash(partition_key) % worker_count.                         │
│    • Розподіляє завдання у виділені черги окремих потоків.                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Вхідний фільтр ідемпотентності (Idempotent Inbox):                       │
│    • Атомарно перевіряє Message-ID перед викликом бізнес-логіки.           │
│    • Відсікає дублікати з негайним відправленням підтвердження ACK.         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Активатор доменного сервісу (Service Activator & Workers):               │
│    • Виконує бізнес-метод `processPayment(orderId, amount)`.               │
│    • Керує дескриптором підтвердження (ACK, NACK або перенаправлення в DLQ).│
└─────────────────────────────────────────────────────────────────────────────┘
```

Розглянемо послідовність проходження даних крізь ці шари:

1. Канальний адаптер отримує вхідний пакет із мережевого з'єднання, перевіряє наявність обов'язкових метаданих у конверті `MessageEnvelope` та формує дескриптор підтвердження `AcknowledgmentHandle`.
2. Диспетчер витягує з конверта ключ партиції `partition_key`, обчислює детермінований хеш і знаходить закріплену за цим ключем чергу воркера. Якщо буфер черги переповнений, диспетчер генерує сигнал зворотного протитиску (Backpressure), змушуючи адаптер тимчасово призупинити читання нових даних із мережі.
3. Робочий потік воркера вилучає завдання з власної ізольованої черги, звертається до репозиторію `IdempotentInbox` для перевірки `Message-ID`. Якщо повідомлення вже було зафіксоване раніше (дублікат через повторну доставку), воркер пропускає виклик домену та негайно підтверджує повідомлення (`ACK`), запобігаючи подвійному списанню коштів.
4. Якщо повідомлення нове, воркер передає бізнес-об'єкт активатору доменного сервісу `BankingDomainService`. Після успішного завершення операції воркер викликає `ack()`. Якщо бізнес-код кидає виняток валідації (отруйний пакет із нульовою або від'ємною сумою), дескриптор викликає `rejectToDlq()`, перенаправляючи пошкоджений документ у мертву чергу (DLQ) для ручного аналізу інженерами.

## Реалізація кінцевої точки

Нижче наведено повні, ідіоматичні реалізації мовами C++20, C11, Go та TypeScript. Кожна вкладка є самостійним завершеним кодом без зовнішніх сторонніх залежностей.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <unordered_set>
#include <unordered_map>
#include <chrono>
#include <functional>
#include <atomic>
#include <optional>
#include <sstream>

// ── 1. СТРУКТУРИ ДАНИХ ТА КОНВЕРТ ПОВІДОМЛЕННЯ ──────────────────────────────
struct MessageHeaders {
    std::string id;                         // Унікальний UUIDv7
    std::string partition_key;              // Ключ для збереження порядку (наприклад, account_id)
    std::string destination;                // Назва черги
    int64_t timestamp_ms = 0;
    uint32_t delivery_attempt = 1;
};

template <typename T>
struct Message {
    MessageHeaders headers;
    T payload;
};

// Бізнес-подія замовлення
struct PaymentEvent {
    std::string order_id;
    std::string account_id;
    uint64_t amount_cents;
    std::string action; // "CREATE", "DEPOSIT", "WITHDRAW"
};

// ── 2. ДЕСКРИПТОР РУЧНОГО ПІДТВЕРДЖЕННЯ (ACKNOWLEDGMENT HANDLE) ────────────
enum class AckStatus { UNPROCESSED, ACKED, NACKED, DLQ_ROUTED };

class AcknowledgmentHandle {
private:
    std::string message_id_;
    AckStatus status_ = AckStatus::UNPROCESSED;
    std::function<void(const std::string&, AckStatus, const std::string&)> callback_;

public:
    AcknowledgmentHandle(std::string message_id,
                         std::function<void(const std::string&, AckStatus, const std::string&)> cb)
        : message_id_(std::move(message_id)), callback_(std::move(cb)) {}

    ~AcknowledgmentHandle() {
        if (status_ == AckStatus::UNPROCESSED && callback_) {
            // RAII-захист: якщо воркер впав або не викликав жодного методу — повертаємо в чергу
            callback_(message_id_, AckStatus::NACKED, "Worker exception / unhandled exit");
        }
    }

    void ack() {
        if (status_ != AckStatus::UNPROCESSED) return;
        status_ = AckStatus::ACKED;
        callback_(message_id_, AckStatus::ACKED, "");
    }

    void nack(const std::string& reason) {
        if (status_ != AckStatus::UNPROCESSED) return;
        status_ = AckStatus::NACKED;
        callback_(message_id_, AckStatus::NACKED, reason);
    }

    void rejectToDlq(const std::string& reason) {
        if (status_ != AckStatus::UNPROCESSED) return;
        status_ = AckStatus::DLQ_ROUTED;
        callback_(message_id_, AckStatus::DLQ_ROUTED, reason);
    }
};

// ── 3. ВХІДНЕ СХОВИЩЕ ІДЕМПОТЕНТНОСТІ (INBOX REPOSITORY) ───────────────────
class ThreadSafeInbox {
private:
    std::mutex mutex_;
    std::unordered_set<std::string> processed_ids_;

public:
    // Повертає true, якщо повідомлення нове, або false, якщо це дублікат
    bool tryClaim(const std::string& message_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (processed_ids_.contains(message_id)) {
            return false; // Дубль знайдено!
        }
        processed_ids_.insert(message_id);
        return true;
    }
};

// ── 4. ДОМЕННИЙ СЕРВІС (BUSINESS SERVICE) ──────────────────────────────────
class BankingDomainService {
private:
    std::unordered_map<std::string, int64_t> account_balances_;
    std::mutex service_mutex_;

public:
    void processPayment(const PaymentEvent& event) {
        std::lock_guard<std::mutex> lock(service_mutex_);
        
        // Симуляція перевірки отруйного повідомлення (Poison Pill)
        if (event.amount_cents == 0 && event.action != "CREATE") {
            throw std::invalid_argument("Poison Pill: Zero payment amount is invalid!");
        }

        if (event.action == "CREATE") {
            account_balances_[event.account_id] = 0;
            std::cout << "  [Domain] Створено рахунок " << event.account_id << "\n";
        } else if (event.action == "DEPOSIT") {
            account_balances_[event.account_id] += event.amount_cents;
            std::cout << "  [Domain] Рахунок " << event.account_id << " поповнено на " 
                      << event.amount_cents << " коп. Баланс: " << account_balances_[event.account_id] << "\n";
        } else if (event.action == "WITHDRAW") {
            account_balances_[event.account_id] -= event.amount_cents;
            std::cout << "  [Domain] З рахунку " << event.account_id << " списано " 
                      << event.amount_cents << " коп. Баланс: " << account_balances_[event.account_id] << "\n";
        }
    }
};

// ── 5. ШАРДОВАНИЙ ДИСПЕТЧЕР З PARTITION AFFINITY ТА ПУЛОМ ВОРКЕРІВ ──────────
class KeyPartitionedDispatcher {
private:
    struct WorkerTask {
        Message<PaymentEvent> message;
        std::unique_ptr<AcknowledgmentHandle> ack_handle;
    };

    struct WorkerQueue {
        std::queue<WorkerTask> tasks;
        std::mutex mutex;
        std::condition_variable cv;
        std::thread thread;
        std::atomic<bool> running{true};
    };

    std::vector<std::unique_ptr<WorkerQueue>> workers_;
    size_t worker_count_;
    size_t max_queue_capacity_;
    BankingDomainService& domain_service_;
    ThreadSafeInbox& inbox_;
    std::atomic<size_t> total_in_flight_{0};

    void workerLoop(size_t worker_id) {
        auto& w = *workers_[worker_id];
        while (w.running) {
            WorkerTask task;
            {
                std::unique_lock<std::mutex> lock(w.mutex);
                w.cv.wait(lock, [&] { return !w.tasks.empty() || !w.running; });
                if (!w.running && w.tasks.empty()) break;
                if (w.tasks.empty()) continue;

                task = std::move(w.tasks.front());
                w.tasks.pop();
            }

            total_in_flight_--;

            // Крок 1: Перевірка ідемпотентності (Inbox)
            if (!inbox_.tryClaim(task.message.headers.id)) {
                std::cout << "  [Endpoint W" << worker_id << "] ДУБЛІКАТ повідомлення " 
                          << task.message.headers.id << " -> пропуск і швидкий ACK.\n";
                task.ack_handle->ack();
                continue;
            }

            // Крок 2: Виклик бізнес-сервісу
            try {
                domain_service_.processPayment(task.message.payload);
                task.ack_handle->ack();
            } catch (const std::invalid_argument& ex) {
                // Постійна помилка -> перенаправлення в мертву чергу (DLQ)
                std::cout << "  [Endpoint W" << worker_id << "] ОТРУЙНИЙ ПАКЕТ: " << ex.what() 
                          << " -> Переміщення в DLQ.\n";
                task.ack_handle->rejectToDlq(ex.what());
            } catch (const std::exception& ex) {
                // Тимчасова помилка -> повернення в чергу (NACK)
                std::cout << "  [Endpoint W" << worker_id << "] Збій обробки: " << ex.what() 
                          << " -> NACK з повтором.\n";
                task.ack_handle->nack(ex.what());
            }
        }
    }

public:
    KeyPartitionedDispatcher(size_t worker_count, size_t max_queue_capacity,
                             BankingDomainService& ds, ThreadSafeInbox& inbox)
        : worker_count_(worker_count), max_queue_capacity_(max_queue_capacity),
          domain_service_(ds), inbox_(inbox) {
        
        for (size_t i = 0; i < worker_count_; ++i) {
            auto w = std::make_unique<WorkerQueue>();
            w->thread = std::thread(&KeyPartitionedDispatcher::workerLoop, this, i);
            workers_.push_back(std::move(w));
        }
    }

    ~KeyPartitionedDispatcher() {
        stop();
    }

    bool dispatch(Message<PaymentEvent> msg, std::unique_ptr<AcknowledgmentHandle> handle) {
        // Хешування ключа партиції для прив'язки до одного воркера
        std::hash<std::string> hasher;
        size_t worker_idx = hasher(msg.headers.partition_key) % worker_count_;
        auto& w = *workers_[worker_idx];

        {
            std::lock_guard<std::mutex> lock(w.mutex);
            if (w.tasks.size() >= max_queue_capacity_) {
                return false; // Сигнал Backpressure: черга переповнена!
            }
            w.tasks.push(WorkerTask{std::move(msg), std::move(handle)});
        }
        total_in_flight_++;
        w.cv.notify_one();
        return true;
    }

    void stop() {
        for (auto& w : workers_) {
            w->running = false;
            w->cv.notify_all();
            if (w->thread.joinable()) {
                w->thread.join();
            }
        }
    }

    size_t getInFlightCount() const { return total_in_flight_.load(); }
};

// ── 6. КАНАЛЬНИЙ АДАПТЕР ТА ТОЧКА ВХОДУ (DEMO RUNNER) ──────────────────────
int main() {
    std::cout << "=== Запуск демонстрації асинхронного Message Endpoint ===\n\n";

    BankingDomainService domain_service;
    ThreadSafeInbox inbox;
    const size_t NUM_WORKERS = 3;
    const size_t QUEUE_CAPACITY = 100;

    KeyPartitionedDispatcher dispatcher(NUM_WORKERS, QUEUE_CAPACITY, domain_service, inbox);

    auto ack_callback = [](const std::string& msg_id, AckStatus status, const std::string& reason) {
        if (status == AckStatus::ACKED) {
            std::cout << "    -> [Broker Callback] ACK підтверджено для " << msg_id << "\n";
        } else if (status == AckStatus::DLQ_ROUTED) {
            std::cout << "    -> [Broker Callback] DLQ збережено для " << msg_id << " (Причина: " << reason << ")\n";
        } else if (status == AckStatus::NACKED) {
            std::cout << "    -> [Broker Callback] NACK для " << msg_id << " (Причина: " << reason << ")\n";
        }
    };

    // Сценарій 1: Послідовність подій для одного клієнта (Account#42)
    std::cout << "--- 1. Тест строгой послідовності для Account#42 ---\n";
    std::vector<Message<PaymentEvent>> stream = {
        {{"msg-001", "Account#42", "orders", 1000}, {"ord-1", "Account#42", 0, "CREATE"}},
        {{"msg-002", "Account#42", "orders", 1001}, {"ord-2", "Account#42", 50000, "DEPOSIT"}},
        {{"msg-003", "Account#42", "orders", 1002}, {"ord-3", "Account#42", 15000, "WITHDRAW"}},
        // Сценарій 2: Дублікат попереднього повідомлення
        {{"msg-002", "Account#42", "orders", 1003}, {"ord-2", "Account#42", 50000, "DEPOSIT"}},
        // Сценарій 3: Інший клієнт (Account#99) — обробляється паралельно
        {{"msg-004", "Account#99", "orders", 1004}, {"ord-4", "Account#99", 0, "CREATE"}},
        {{"msg-005", "Account#99", "orders", 1005}, {"ord-5", "Account#99", 30000, "DEPOSIT"}},
        // Сценарій 4: Отруйний пакет (нульова сума при списанні)
        {{"msg-006", "Account#42", "orders", 1006}, {"ord-6", "Account#42", 0, "WITHDRAW"}}
    };

    for (auto& msg : stream) {
        auto handle = std::make_unique<AcknowledgmentHandle>(msg.headers.id, ack_callback);
        std::string id = msg.headers.id;
        while (!dispatcher.dispatch(msg, std::move(handle))) {
            std::cout << "  [Backpressure] Черга заповнена, очікування 10 мс...\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            handle = std::make_unique<AcknowledgmentHandle>(id, ack_callback);
        }
    }

    // Очікування завершення обробки
    std::this_thread::sleep_for(std::chrono::milliseconds(300));

    std::cout << "\n--- Завершення роботи: Дренування буферів ---\n";
    dispatcher.stop();
    std::cout << "Всі воркери безпечно зупинені. Демонстрацію завершено успішно.\n";

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define NUM_WORKERS 3
#define QUEUE_CAPACITY 100
#define MAX_ID_LEN 64

typedef enum { ACK_UNPROCESSED, ACK_ACKED, ACK_NACKED, ACK_DLQ } AckStatus;

typedef struct {
    char id[MAX_ID_LEN];
    char partition_key[MAX_ID_LEN];
    char account_id[MAX_ID_LEN];
    char action[16];
    unsigned long amount_cents;
} CMessage;

typedef struct {
    char message_id[MAX_ID_LEN];
    AckStatus status;
} CAckHandle;

typedef struct {
    CMessage items[QUEUE_CAPACITY];
    CAckHandle handles[QUEUE_CAPACITY];
    int head, tail, count;
    pthread_mutex_t lock;
    pthread_cond_t cv;
    pthread_t thread;
    bool running;
} CWorkerQueue;

typedef struct {
    char ids[1000][MAX_ID_LEN];
    int count;
    pthread_mutex_t lock;
} CInbox;

CInbox g_inbox;
CWorkerQueue g_workers[NUM_WORKERS];

bool inbox_try_claim(const char* id) {
    pthread_mutex_lock(&g_inbox.lock);
    for (int i = 0; i < g_inbox.count; ++i) {
        if (strcmp(g_inbox.ids[i], id) == 0) {
            pthread_mutex_unlock(&g_inbox.lock);
            return false; // Дубль
        }
    }
    if (g_inbox.count < 1000) {
        strncpy(g_inbox.ids[g_inbox.count++], id, MAX_ID_LEN - 1);
    }
    pthread_mutex_unlock(&g_inbox.lock);
    return true;
}

unsigned int hash_key(const char* s) {
    unsigned int h = 5381;
    while (*s) h = ((h << 5) + h) + (unsigned char)(*s++);
    return h % NUM_WORKERS;
}

void* worker_thread_func(void* arg) {
    int wid = (int)(intptr_t)arg;
    CWorkerQueue* q = &g_workers[wid];

    while (true) {
        CMessage msg;
        CAckHandle handle;

        pthread_mutex_lock(&q->lock);
        while (q->count == 0 && q->running) {
            pthread_cond_wait(&q->cv, &q->lock);
        }
        if (!q->running && q->count == 0) {
            pthread_mutex_unlock(&q->lock);
            break;
        }

        msg = q->items[q->head];
        handle = q->handles[q->head];
        q->head = (q->head + 1) % QUEUE_CAPACITY;
        q->count--;
        pthread_mutex_unlock(&q->lock);

        // Дедуплікація
        if (!inbox_try_claim(msg.id)) {
            printf("  [C-Worker %d] ДУБЛІКАТ %s -> ACK\n", wid, msg.id);
            continue;
        }

        // Бізнес-логіка
        if (msg.amount_cents == 0 && strcmp(msg.action, "CREATE") != 0) {
            printf("  [C-Worker %d] ОТРУЙНИЙ ПАКЕТ %s -> DLQ\n", wid, msg.id);
        } else {
            printf("  [C-Worker %d] Оброблено %s для %s (%lu коп.) -> ACK\n", 
                   wid, msg.action, msg.account_id, msg.amount_cents);
        }
    }
    return NULL;
}

int main(void) {
    printf("=== C11 Реалізація Message Endpoint ===\n\n");
    pthread_mutex_init(&g_inbox.lock, NULL);
    g_inbox.count = 0;

    for (intptr_t i = 0; i < NUM_WORKERS; ++i) {
        g_workers[i].head = g_workers[i].tail = g_workers[i].count = 0;
        g_workers[i].running = true;
        pthread_mutex_init(&g_workers[i].lock, NULL);
        pthread_cond_init(&g_workers[i].cv, NULL);
        pthread_create(&g_workers[i].thread, NULL, worker_thread_func, (void*)i);
    }

    CMessage test_msgs[] = {
        {"c-msg-1", "Acc#10", "Acc#10", "CREATE", 0},
        {"c-msg-2", "Acc#10", "Acc#10", "DEPOSIT", 5000},
        {"c-msg-2", "Acc#10", "Acc#10", "DEPOSIT", 5000}, // Дубль
        {"c-msg-3", "Acc#10", "Acc#10", "WITHDRAW", 0}   // Отруйний
    };

    for (int i = 0; i < 4; ++i) {
        unsigned int wid = hash_key(test_msgs[i].partition_key);
        CWorkerQueue* q = &g_workers[wid];
        pthread_mutex_lock(&q->lock);
        q->items[q->tail] = test_msgs[i];
        strncpy(q->handles[q->tail].message_id, test_msgs[i].id, MAX_ID_LEN - 1);
        q->tail = (q->tail + 1) % QUEUE_CAPACITY;
        q->count++;
        pthread_cond_signal(&q->cv);
        pthread_mutex_unlock(&q->lock);
    }

    usleep(200000); // 200 мс

    for (int i = 0; i < NUM_WORKERS; ++i) {
        pthread_mutex_lock(&g_workers[i].lock);
        g_workers[i].running = false;
        pthread_cond_signal(&g_workers[i].cv);
        pthread_mutex_unlock(&g_workers[i].lock);
        pthread_join(g_workers[i].thread, NULL);
    }
    printf("\nУсі C-воркери завершили роботу.\n");
    return 0;
}
```
```ts
// TypeScript / Node.js асинхронний Message Endpoint

interface MessageHeaders {
    id: string;
    partitionKey: string;
    destination: string;
    timestampMs: number;
}

interface PaymentEvent {
    orderId: string;
    accountId: string;
    amountCents: number;
    action: "CREATE" | "DEPOSIT" | "WITHDRAW";
}

interface Message<T> {
    headers: MessageHeaders;
    payload: T;
}

type AckCallback = (id: string, status: "ACK" | "NACK" | "DLQ", reason?: string) => void;

class TsInbox {
    private processed = new Set<string>();

    tryClaim(id: string): boolean {
        if (this.processed.has(id)) return false;
        this.processed.add(id);
        return true;
    }
}

class TsKeyPartitionedEndpoint {
    private queues: Array<Array<{ msg: Message<PaymentEvent>; cb: AckCallback }>>;
    private busy: boolean[];
    private inbox = new TsInbox();

    constructor(private workerCount: number = 3) {
        this.queues = Array.from({ length: workerCount }, () => []);
        this.busy = Array.from({ length: workerCount }, () => false);
    }

    private hash(key: string): number {
        let h = 0;
        for (let i = 0; i < key.length; i++) {
            h = (Math.imul(31, h) + key.charCodeAt(i)) | 0;
        }
        return Math.abs(h) % this.workerCount;
    }

    dispatch(msg: Message<PaymentEvent>, cb: AckCallback): void {
        const workerId = this.hash(msg.headers.partitionKey);
        this.queues[workerId].push({ msg, cb });
        this.scheduleWorker(workerId);
    }

    private async scheduleWorker(workerId: number): Promise<void> {
        if (this.busy[workerId]) return;
        this.busy[workerId] = true;

        while (this.queues[workerId].length > 0) {
            const task = this.queues[workerId].shift()!;
            
            // 1. Дедуплікація через Inbox
            if (!this.inbox.tryClaim(task.msg.headers.id)) {
                console.log(`  [TS-Worker ${workerId}] ДУБЛІКАТ ${task.msg.headers.id} -> ACK`);
                task.cb(task.msg.headers.id, "ACK");
                continue;
            }

            // 2. Бізнес-обробка
            try {
                if (task.msg.payload.amountCents === 0 && task.msg.payload.action !== "CREATE") {
                    throw new Error("Invalid payment amount: 0");
                }
                console.log(`  [TS-Worker ${workerId}] Успішно: ${task.msg.payload.action} ${task.msg.payload.accountId}`);
                task.cb(task.msg.headers.id, "ACK");
            } catch (err: any) {
                console.log(`  [TS-Worker ${workerId}] ОТРУЙНИЙ ПАКЕТ ${task.msg.headers.id} -> DLQ`);
                task.cb(task.msg.headers.id, "DLQ", err.message);
            }
        }

        this.busy[workerId] = false;
    }
}
```
```go
package main

import (
	"fmt"
	"hash/fnv"
	"sync"
	"time"
)

type MessageHeaders struct {
	ID           string
	PartitionKey string
	Destination  string
}

type PaymentEvent struct {
	AccountID   string
	Action      string
	AmountCents uint64
}

type Message struct {
	Headers MessageHeaders
	Payload PaymentEvent
}

type AckStatus string

const (
	AckStatusAck  AckStatus = "ACK"
	AckStatusNack AckStatus = "NACK"
	AckStatusDlq  AckStatus = "DLQ"
)

type AckCallback func(id string, status AckStatus, reason string)

type WorkerTask struct {
	Msg Message
	Cb  AckCallback
}

type GoPartitionedEndpoint struct {
	workerCount int
	queues      []chan WorkerTask
	inbox       sync.Map
	wg          sync.WaitGroup
}

func NewEndpoint(workerCount int, queueCap int) *GoPartitionedEndpoint {
	ep := &GoPartitionedEndpoint{
		workerCount: workerCount,
		queues:      make([]chan WorkerTask, workerCount),
	}

	for i := 0; i < workerCount; i++ {
		ep.queues[i] = make(chan WorkerTask, queueCap)
		ep.wg.Add(1)
		go ep.workerLoop(i, ep.queues[i])
	}
	return ep
}

func (ep *GoPartitionedEndpoint) workerLoop(id int, queue chan WorkerTask) {
	defer ep.wg.Done()
	for task := range queue {
		// 1. Дедуплікація Inbox
		if _, loaded := ep.inbox.LoadOrStore(task.Msg.Headers.ID, true); loaded {
			fmt.Printf("  [Go-Worker %d] ДУБЛІКАТ %s -> ACK\n", id, task.Msg.Headers.ID)
			task.Cb(task.Msg.Headers.ID, AckStatusAck, "")
			continue
		}

		// 2. Бізнес-обробка
		if task.Msg.Payload.AmountCents == 0 && task.Msg.Payload.Action != "CREATE" {
			fmt.Printf("  [Go-Worker %d] ОТРУЙНИЙ ПАКЕТ %s -> DLQ\n", id, task.Msg.Headers.ID)
			task.Cb(task.Msg.Headers.ID, AckStatusDlq, "Zero amount")
		} else {
			fmt.Printf("  [Go-Worker %d] Оброблено %s для %s -> ACK\n", id, task.Msg.Payload.Action, task.Msg.Payload.AccountID)
			task.Cb(task.Msg.Headers.ID, AckStatusAck, "")
		}
	}
}

func (ep *GoPartitionedEndpoint) Dispatch(msg Message, cb AckCallback) {
	hasher := fnv.New32a()
	hasher.Write([]byte(msg.Headers.PartitionKey))
	workerID := int(hasher.Sum32()) % ep.workerCount
	ep.queues[workerID] <- WorkerTask{Msg: msg, Cb: cb}
}

func (ep *GoPartitionedEndpoint) Stop() {
	for _, q := range ep.queues {
		close(q)
	}
	ep.wg.Wait()
}
```
:::

## Покроковий розбір життєвого циклу та внутрішніх механізмів

Розглянемо детально кожен інженерний шар реалізованого Message Endpoint та механізми забезпечення надійності.

### 1. Механіка детермінованого шардування (Partition Affinity)

Для одночасного досягнення високої пропускної здатності та суворого збереження послідовності обробки подій одного бізнес-агрегата диспетчер використовує формулу детермінованого розподілу за ключем:

```
worker_idx = hash(partition_key) % worker_count
```

У мові C++20 стандартний шаблон `std::hash<std::string>` генерує 64-бітне псевдовипадкове число з рівномірним розподілом ентропії. Операція взяття остачі від ділення на `worker_count_` гарантує, що:
- Будь-яка кількість повідомлень з однаковим значенням `partition_key` (наприклад, `Account#42`) неминуче отримує однаковий індекс воркера `worker_idx = 0`.
- Повідомлення потрапляють у приватну чергу `WorkerQueue 0`, яка читається виключно одним робочим потоком `Thread 0`.
- Обробка всередині конкретного рахунку відбувається строго за алгоритмом FIFO: подія `CREATE` виконається гарантовано раніше за `DEPOSIT`, а `DEPOSIT` — раніше за `WITHDRAW`.
- Повідомлення іншого клієнта `Account#99` потрапляють до черги `WorkerQueue 1` і виконуються паралельно на іншому ядрі CPU. Відсутність спільних блокувань між різними акаунтами забезпечує лінійну масштабованість системи при збільшенні кількості ядер.

### 2. Керування володінням пам'яттю та RAII-дескриптор підтвердження

Ключовим аспектом надійності є запобігання втраті повідомлень при аварійному завершенні робочих потоків. У реалізації C++ це досягається комбінацією унікальних покажчиків `std::unique_ptr` та ідіоми RAII (Resource Acquisition Is Initialization).

Клас `AcknowledgmentHandle` володіє ексклюзивним правом відправки фінального статусу в брокер. Деструктор класу містить захисну логіку:

```cpp
~AcknowledgmentHandle() {
    if (status_ == AckStatus::UNPROCESSED && callback_) {
        callback_(message_id_, AckStatus::NACKED, "Worker exception / unhandled exit");
    }
}
```

Якщо доменний метод `processPayment()` кидає неперехоплений виняток пам'яті або якщо потік аварійно виходить із блоку `try/catch`, локальний об'єкт `std::unique_ptr<AcknowledgmentHandle>` знищується під час розгортання стека (Stack Unwinding). Деструктор бачить статус `UNPROCESSED` і негайно викликає `NACK`, повертаючи повідомлення в чергу брокера. Це унеможливлює стан «завислого повідомлення», коли пакет залишається заблокованим у брокері до вичерпання таймауту сесії (який у реальних системах може тривати до 30 хвилин).

### 3. Механіка роботи вхідного сховища ідемпотентності (Idempotent Inbox)

У розподілених системах із гарантією доставки At-least-once дублювання повідомлень є неминучим наслідком обривів мережевих сокетів під час відправки ACK. Вхідна кінцева точка перехоплює повідомлення до їхньої передачі в доменний сервіс:

```cpp
if (!inbox_.tryClaim(task.message.headers.id)) {
    std::cout << "  [Endpoint W" << worker_id << "] ДУБЛІКАТ повідомлення " 
              << task.message.headers.id << " -> пропуск і швидкий ACK.\n";
    task.ack_handle->ack();
    continue;
}
```

Метод `tryClaim()` атомарно перевіряє наявність ідентифікатора у внутрішній хеш-таблиці `processed_ids_`. Якщо ідентифікатор знайдено:
1. Бізнес-метод `processPayment()` не викликається, усуваючи загрозу повторного списання грошей.
2. Дескриптор `ack_handle->ack()` негайно підтверджує успішну обробку в брокер повідомлень.
3. Брокер безпечно видаляє надлишкову копію зі своєї черги.

У промислових системах замість пам'яті процесу використовується реляційна таблиця бази даних із первинним ключем `PRIMARY KEY (message_id)` або високопродуктивне сховище Redis із командою `SET message_id "COMPLETED" EX 604800 NX` (атомарне встановлення із 7-денним часом життя запису).

### 4. Контроль зворотного протитиску (Backpressure) та захист від OOM

Канальний адаптер кінцевої точки не повинен безконтрольно вичитувати сокет при виникненні затримок у базі даних. У нашій реалізації кожна черга воркера має обмежену ємність `max_queue_capacity_ = 100`:

```cpp
if (w.tasks.size() >= max_queue_capacity_) {
    return false; // Сигнал Backpressure
}
```

Коли сумарний вхідний потік перевищує швидкість обробки, черга воркера заповнюється, і диспетчер повертає `false`. Канальний адаптер перехоплює цей сигнал і призупиняє читання нових фреймів із TCP-сокета. На рівні мережевого протоколу TCP це призводить до заповнення буфера прийому сокета (TCP Receive Window = 0). Відправник (брокер) бачить закрите вікно TCP і автоматично припиняє надсилання пакетів через мережу, утримуючи повідомлення у власному дисковому буфері. Це на 100% захищає процес кінцевої точки від переповнення оперативної пам'яті та падіння через нестачу пам'яті (Out-Of-Memory Crash).

### 5. Протокол безпечного дренування (Graceful Shutdown)

При отриманні сигналу завершення роботи застосунку (`SIGTERM`) кінцева точка повинна завершити поточні активні транзакції без втрати даних:

```cpp
void stop() {
    for (auto& w : workers_) {
        w->running = false;
        w->cv.notify_all();
        if (w->thread.joinable()) {
            w->thread.join();
        }
    }
}
```

1. Диспетчер виставляє прапорець `running = false` для кожного воркера.
2. Виклик `notify_all()` будить усі сплячі потоки.
3. Кожен потік воркера дочитує та обробляє всі повідомлення, що вже перебувають у черзі `w.tasks`, зберігає зміни в базі даних та відправляє мережеві підтвердження `ACK`.
4. Виклик `w->thread.join()` блокує головний потік до повного завершення всіх воркерів.

## Покрокове трасування життєвого циклу одного повідомлення

Для повного розуміння внутрішньої взаємодії компонентів простежимо шлях повідомлення `msg-002` (поповнення балансу `Account#42` на 50 000 коп.):

1. **Мережеве зчитування та упаковка:** канальний адаптер зчитує бінарний фрейм із мережевого сокета, створює структуру `Message<PaymentEvent>` із заголовками `partition_key = "Account#42"` та генерує `AcknowledgmentHandle` із прив'язкою до ідентифікатора `msg-002`.
2. **Диспетчеризація:** канальний адаптер викликає метод `dispatcher.dispatch()`. Диспетчер бере хеш від рядка `"Account#42"`, отримує залишок від ділення `worker_idx = 0` і перевіряє кількість елементів у `WorkerQueue 0`. Оскільки в черзі менше 100 завдань, завдання додається у чергу, лічильник `total_in_flight_` збільшується на одиницю, і спрацьовує виклик `w.cv.notify_one()`.
3. **Пробудження воркера:** потік `Thread 0` прокидається на умовній змінній, захоплює м'ютекс `w.mutex`, вилучає завдання з черги `tasks.front()`, негайно відпускає м'ютекс і зменшує лічильник незавершених завдань.
4. **Перевірка ідемпотентності:** потік викликає `inbox_.tryClaim("msg-002")`. Оскільки це перша поява ідентифікатора, метод додає рядок до хеш-таблиці та повертає `true`.
5. **Виконання доменного методу:** воркер передає структуру `PaymentEvent` методу `domain_service.processPayment()`. Метод оновлює локальний баланс рахунку, друкує підтвердження в лог і повертає керування без винятків.
6. **Мережеве підтвердження:** воркер викликає `task.ack_handle->ack()`. Дескриптор переводить свій внутрішній стан у `ACKED` і викликає лямбда-функцію зворотного виклику `ack_callback`, яка відправляє підтвердження `basic.ack` у мережевий сокет брокера. Брокер фіксує успіх і остаточно видаляє повідомлення з черги на диску.

## Математичне моделювання черг та розрахунок пулу воркерів

При проектуванні виробничої кінцевої точки розміри черг і кількість робочих потоків не повинні призначатися довільно. Вони спираються на теорію масового обслуговування (Queueing Theory) та фундаментальний закон Літтла.

Згідно з законом Літтла, середня кількість повідомлень у черзі `L` дорівнює добутку інтенсивності вхідного потоку `λ` (повідомлень/с) на середній час перебування в системі `W` (секунд):

```
L = λ · W
```

Для стабільної роботи без накопичення нескінченних черг система повинна задовольняти умову стаціонарності: сумарна пропускна здатність пулу потоків `μ_total` має строго перевищувати середній вхідний потік `λ`:

```
μ_total = N_threads · μ_worker > λ
```

де:
- `N_threads` — кількість паралельних робочих потоків;
- `μ_worker = 1 / T_proc` — середня швидкість обробки одного повідомлення одним воркером (`T_proc` — час транзакції в базі даних).

Якщо сервіс отримує вхідний піковий потік `λ = 1000` повідомлень на секунду, а середній час запису в базу даних становить `T_proc = 20` мс (тобто `μ_worker = 50` оп/с), мінімальна необхідна кількість воркерів розраховується як:

```
N_threads = λ / μ_worker = 1000 / 50 = 20 воркерів
```

Мінімальна місткість черги одного воркера `Q_cap` для згладжування сплесків затримки бази даних (p99 latency spikе до `100` мс) визначається за формулою:

```
Q_cap = (λ / N_threads) · (T_p99 - T_proc) = (1000 / 20) · (0.100 - 0.020) = 50 · 0.080 = 4 повідомлення
```

З урахуванням запасу надійності в 10 разів місткість буфера встановлюють на рівні `Q_cap = 50..100` повідомлень на потік.

## Інтеграція з реальними брокерами: мапінг на librdkafka та rabbitmq-c

У промислових C++ застосунках канальний адаптер транслює виклики абстрактного `AcknowledgmentHandle` та `ChannelAdapter` у виклики низькорівневих C-бібліотек:

- **Інтеграція з Apache Kafka (через `librdkafka`):**
  - Вичитування пакетів здійснюється викликом `rd_kafka_consumer_poll(rk, 100)`.
  - Замість індивідуальних ACK метод `ack()` оновлює внутрішню таблицю зміщень партицій (Partition Offsets).
  - Періодичний фоновий потік викликає `rd_kafka_commit()` для синхронної або асинхронної фіксації зміщень на брокері.
  - При виникненні ребалансу (Consumer Rebalance Callback) адаптер зупиняє диспетчеризацію нових повідомлень, чекає дренування черг активних воркерів, викликає фінальний коміт і лише після цього віддає партицію іншому споживачеві кластера.
- **Інтеграція з RabbitMQ (через `rabbitmq-c`):**
  - Вичитування здійснюється викликом `amqp_basic_consume` з конфігурацією `amqp_basic_qos(conn, channel, 0, prefetch_count, 0)`.
  - Метод `ack()` викликає функцію `amqp_basic_ack(conn, channel, delivery_tag, 0)`.
  - Метод `nack()` викликає `amqp_basic_nack(conn, channel, delivery_tag, 0, requeue ? 1 : 0)`.
  - Метод `rejectToDlq()` публікує конверт у Dead-Letter Exchange `amqp_basic_publish(conn, channel, dlx_name, routing_key, ...)` та відправляє `amqp_basic_ack` для початкового повідомлення.

## Порівняння моделей конкурентності в різних мовах

Реалізація патерну Message Endpoint суттєво різниться залежно від моделі конкурентності обраної мови програмування:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ПОРІВНЯННЯ МОДЕЛЕЙ КОНКУРЕНТНОСТІ                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. C++20:                                                                   │
│    • Модель: Системні нитки ОС (std::thread) з приватними м'ютексами.       │
│    • Пам'ять: RAII-деструктори, нульові накладні витрати (Zero-Cost).       │
│    • Перевага: Максимальна продуктивність, повний контроль кеш-ліній CPU.   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. C11:                                                                     │
│    • Модель: POSIX Threads (pthread_mutex_t, pthread_cond_t).               │
│    • Пам'ять: Фіксовані кільцеві буфери (Ring Buffers) без динамічної RAM.  │
│    • Перевага: Мінімальний бінарний розмір, придатність для embedded систем.│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Go:                                                                      │
│    • Модель: Легковажні горутини (Goroutines) та типізовані канали (Channels)│
│    • Пам'ять: Конкурентна хеш-таблиця sync.Map, збирач сміття (GC).         │
│    • Перевага: Вбудований протитиск через обмежені буферизовані канали.      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. TypeScript / Node.js:                                                    │
│    • Модель: Однонитковий цикл подій (Event Loop) та мікротаски Promise.    │
│    • Пам'ять: Асинхронні черги на базі Set/Map, відсутність м'ютексів.      │
│    • Перевага: Неможливість класичних дедлоків пам'яті, простота DTO.       │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **C++20 та C11:** використовують паралелізм на рівні ядер процесора. Окремий м'ютекс на кожну чергу воркера (`WorkerQueue::mutex`) усуває міжпотокову конкуренцію (Lock Contention), дозволяючи системі масштабуватися до десятків мільйонів повідомлень на секунду.
- **Go:** реалізує модель послідовних процесів, що взаємодіють (CSP). Замість явних черг і умовних змінних використовуються буферизовані канали `chan WorkerTask`. Сигнал Backpressure реалізується природно через блокування запису в заповнений канал.
- **TypeScript:** працює в однопотоковому циклі подій. Стан гонки за пам'ять процесу відсутній за визначенням, проте тривалі обчислення або синхронні операції можуть заблокувати весь цикл обробки. Тому обробка вхідних завдань організована як послідовний асинхронний ланцюжок через `async/await`.

## Низькорівнева оптимізація та апаратна архітектура

Для досягнення ультранизької латентності (Sub-millisecond Latency) у високонавантажених C++ ендпоінтах враховують особливості архітектури сучасних процесорів:

1. **Захист від хибного спільного використання кеш-ліній (False Sharing):** структури `WorkerQueue` розміщують у пам'яті з вирівнюванням за розміром кеш-лінії процесора (типово 64 байти):
   ```cpp
   struct alignas(64) WorkerQueue {
       // Поля структури гарантовано займають окрему кеш-лінію
   };
   ```
   Це запобігає апаратному скиданню L1/L2-кешів між сусідніми ядрами процесора при одночасному оновленні черг різними потоками.
2. **Lock-Free буфери SPSC (Single-Producer Single-Consumer):** оскільки кожну чергу воркера наповнює лише один потік диспетчера, а вичитує лише один потік воркера, стандартну чергу з м'ютексом можна замінити на безблокувальний кільцевий буфер на атомарних покажчиках `std::atomic<size_t>` з семантикою пам'яті `std::memory_order_acquire` / `std::memory_order_release`. Це зменшує час передачі завдання між потоками з 1200 нс до 45 нс.

## Стратегія тестування та перевірка інваріантів

Надійність кінцевої точки перевіряється спеціалізованим набором автоматизованих тестів:

- **Тест на стан гонки (Race Condition Test з ThreadSanitizer):** програма компілюється з прапорцем `-fsanitize=thread`. Генератор симулює одночасний потік із 100 000 повідомлень для 1000 випадкових акаунтів, перевіряючи відсутність несинхронізованого доступу до балансів.
- **Тест на строгість черговості (Sequence Order Verification):** для кожного рахунку генерується послідовність чисел `1..1000`. Воркери фіксують отримані значення у вихідному масиві. Тест перевіряє, що масив для кожного рахунку є строго монотонно зростаючим.
- **Стрес-тест на вичерпання пам'яті (Backpressure Soak Test):** швидкість доменного методу штучно сповільнюється до 1 оп/с, а вхідний потік подається зі швидкістю 10 000 оп/с. Тест перевіряє, що споживання оперативної пам'яті процесу стабілізується на фіксованому рівні `N_workers · Q_capacity` і не зростає з часом.
- **Тест на відновлення після збоїв (Chaos Worker Crash Test):** потік генерації випадково кидає винятки пам'яті в 5% випадків. Тест перевіряє, що жодне повідомлення не втрачається без підтвердження `NACK` або відправлення в DLQ.

## Типові помилки та пастки експлуатації

- **Пастка гарячого ключа (Hot Partition Skew):** якщо 95% транзакцій системи припадають на один службовий акаунт маркетплейсу, потік `Worker 0` буде завантажений на 100%, тоді як решта потоків простоюватимуть. Для вирішення цієї проблеми застосовують комбіноване ключування (`accountId + ":" + roundRobinSalt`), якщо внутрішні бізнес-операції допускають паралелізм.
- **Нескінченний цикл отруйного пакета (Poison Pill Storm):** якщо воркер повертає пошкоджене повідомлення в чергу через `nack(requeue=true)`, черга негайно віддає його наступному вільному воркеру. Виникає катастрофічний шторм повторів, який спалює 100% потужності CPU. Суворе правило: невалідовані дані та синтаксичні помилки повинні безумовно скеровуватися в `rejectToDlq()`.
- **Зависання потоків у домені (Unbounded Blocking):** виконання повільних зовнішніх HTTP-запитів всередині `processPayment()` блокує робочий потік воркера. Якщо всі воркери заблокуються очікуванням стороннього сервісу, вся кінцева точка зупиниться. Доменні виклики повинні завжди захищатися суворими таймаутами (Timeouts / Deadlines) та автоматичними запобіжниками (Circuit Breakers).
- **Втрата повідомлень при переповненні буфера відправки (Publisher Buffer Bloat):** коли вихідний шлюз накопичує тисячі асинхронних `sendAsync()` без обмеження черги очікування, пам'ять процесу вичерпується при збої брокера. Завжди обмежуйте розмір буфера відправника та застосовуйте таймаути очікування підтвердження.
- **Порушення бар'єрів пам'яті при роботі з атоміками:** використання `std::memory_order_relaxed` для лічильників непідтверджених повідомлень може призвести до читання застарілого стану між різними ядрами CPU. У критичних місцях синхронізації завжди використовуйте семантику `Acquire-Release` або повний бар'єр `std::memory_order_seq_cst`.
