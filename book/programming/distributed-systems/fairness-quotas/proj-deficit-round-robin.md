# ⚙️ Реалізація планувальника Deficit Round Robin для RPC-запитів

У високопродуктивних мережевих проксі (Envoy, Nginx), брокерах повідомлень та шлюзах мікросервісів обробка тисяч одночасних клієнтів вимагає надійної ізоляції потоків трафіку. Головний виклик полягає у запобіганні блокуванню голови черги (Head-of-Line Blocking), коли один орендар генерує лавину важких запитів і монополізує пул обчислювальних потоків.

Класичний алгоритм Weighted Fair Queuing (WFQ) вимагає підтримки глобального віртуального часу та сортування запитів у пріоритетній купі зі складністю `O(log N)`. За інтенсивності в сотні тисяч операцій на секунду накладні витрати на синхронізацію та перебудову дерева стають вузьким місцем процесора. Планувальник **Deficit Round Robin (DRR)** усуває цю проблему, зводячи обчислювальну складність вибірки до константного часу `O(1)` за рахунок локальних лічильників дефіциту.

Нижче наведено повнофункціональну потокобезпечну реалізацію багатопотокового планувальника DRR, адаптованого для диспетчеризації RPC-викликів зі змінною вартістю обчислень (байтами або умовними одиницями процесорного часу).

## Архітектура та внутрішні структури даних

Диспетчер складається з трьох ключових структур:
1. **Дескриптор черги орендаря (`FlowQueue`):** кожна черга представляє окремого клієнта або клас обслуговування. Вона утримує конфігурований базовий квант (`quantum`), поточний накопичений баланс дефіциту (`deficit_counter`), кільцевий буфер очікуваних завдань та покажчик для зв'язування в динамічний список.
2. **Кільцевий список активних черг (`ActiveList`):** черга додається до активного списку планування лише в момент переходу зі стану порожнечі (коли надходить перший запит). Порожні черги негайно вилучаються з кільця, що запобігає марним холостим ітераціям циклу планувальника.
3. **Потокобезпечний арбітр:** синхронізація доступу між потоками прийому мережевих пакетів (Ingress Threads) та пулом потоків-виконавців бізнес-логіки (Worker Pool) за допомогою м'ютексів та умовних змінних.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <string.h>

#define MAX_FLOWS 128
#define QUEUE_CAPACITY 1024

// Опис RPC-запиту
typedef struct Request {
    uint64_t req_id;
    uint32_t tenant_id;
    uint32_t cost_units; // Вага запиту (байти або мікросекунди CPU)
    void* payload;
} Request;

// Черга окремого орендаря
typedef struct FlowQueue {
    uint32_t tenant_id;
    uint32_t quantum;          // Квант, що додається за кожен раунд
    int32_t  deficit_counter;  // Накопичений баланс дефіциту
    Request  buffer[QUEUE_CAPACITY];
    size_t   head;
    size_t   tail;
    size_t   count;
    bool     is_active;        // Чи присутня черга в активному кільці
    struct FlowQueue* next_active;
} FlowQueue;

// Стан планувальника DRR
typedef struct DRRScheduler {
    FlowQueue flows[MAX_FLOWS];
    size_t    flow_count;

    FlowQueue* active_head;
    FlowQueue* active_tail;
    FlowQueue* current_flow;   // Поточний потік на обслуговуванні

    pthread_mutex_t lock;
    pthread_cond_t  has_work;
    bool            shutdown;
} DRRScheduler;

// Ініціалізація планувальника
void drr_init(DRRScheduler* sched) {
    memset(sched, 0, sizeof(DRRScheduler));
    pthread_mutex_init(&sched->lock, NULL);
    pthread_cond_init(&sched->has_work, NULL);
}

// Реєстрація нового орендаря з базовим квантом
bool drr_register_tenant(DRRScheduler* sched, uint32_t tenant_id, uint32_t quantum) {
    pthread_mutex_lock(&sched->lock);
    if (sched->flow_count >= MAX_FLOWS) {
        pthread_mutex_unlock(&sched->lock);
        return false;
    }

    FlowQueue* q = &sched->flows[sched->flow_count++];
    q->tenant_id = tenant_id;
    q->quantum = quantum;
    q->deficit_counter = 0;
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->is_active = false;
    q->next_active = NULL;

    pthread_mutex_unlock(&sched->lock);
    return true;
}

// Додавання черги до активного списку
static void activate_flow_locked(DRRScheduler* sched, FlowQueue* q) {
    if (q->is_active) return;

    q->is_active = true;
    q->next_active = NULL;

    if (sched->active_tail == NULL) {
        sched->active_head = q;
        sched->active_tail = q;
        sched->current_flow = q;
    } else {
        sched->active_tail->next_active = q;
        sched->active_tail = q;
    }
}

// Постановка RPC-запиту в чергу відповідного орендаря
bool drr_enqueue(DRRScheduler* sched, Request req) {
    pthread_mutex_lock(&sched->lock);

    FlowQueue* target = NULL;
    for (size_t i = 0; i < sched->flow_count; ++i) {
        if (sched->flows[i].tenant_id == req.tenant_id) {
            target = &sched->flows[i];
            break;
        }
    }

    if (!target || target->count >= QUEUE_CAPACITY) {
        pthread_mutex_unlock(&sched->lock);
        return false; // Відмова: невідомий орендар або буфер переповнено
    }

    target->buffer[target->tail] = req;
    target->tail = (target->tail + 1) % QUEUE_CAPACITY;
    target->count++;

    if (!target->is_active) {
        // Перший пакет після простою: скидаємо старий дефіцит
        target->deficit_counter = 0;
        activate_flow_locked(sched, target);
    }

    pthread_cond_signal(&sched->has_work);
    pthread_mutex_unlock(&sched->lock);
    return true;
}

// Вибірка наступного запиту за алгоритмом Deficit Round Robin
bool drr_dequeue(DRRScheduler* sched, Request* out_req) {
    pthread_mutex_lock(&sched->lock);

    while (sched->active_head == NULL && !sched->shutdown) {
        pthread_cond_wait(&sched->has_work, &sched->lock);
    }

    if (sched->shutdown && sched->active_head == NULL) {
        pthread_mutex_unlock(&sched->lock);
        return false;
    }

    FlowQueue* prev_flow = NULL;
    FlowQueue* q = sched->current_flow ? sched->current_flow : sched->active_head;

    while (q != NULL) {
        // Початок раунду для потоку: додаємо квант
        q->deficit_counter += q->quantum;

        while (q->count > 0) {
            Request* head_req = &q->buffer[q->head];

            // Якщо накопиченого дефіциту достатньо для покриття вартості
            if ((int32_t)head_req->cost_units <= q->deficit_counter) {
                q->deficit_counter -= head_req->cost_units;
                *out_req = *head_req;

                q->head = (q->head + 1) % QUEUE_CAPACITY;
                q->count--;

                // Якщо черга спустошилася — обнуляємо дефіцит і вилучаємо зі списку
                if (q->count == 0) {
                    q->deficit_counter = 0;
                    q->is_active = false;

                    if (prev_flow) {
                        prev_flow->next_active = q->next_active;
                    } else {
                        sched->active_head = q->next_active;
                    }
                    if (sched->active_tail == q) {
                        sched->active_tail = prev_flow;
                    }
                    sched->current_flow = q->next_active ? q->next_active : sched->active_head;
                } else {
                    sched->current_flow = q;
                }

                pthread_mutex_unlock(&sched->lock);
                return true;
            } else {
                // Дефіциту замало: зберігаємо залишок і переходимо до наступного
                break;
            }
        }

        // Перехід до наступної черги в раунді
        prev_flow = q;
        q = q->next_active;
        if (q == NULL) {
            // Кільце замикається
            prev_flow = NULL;
            q = sched->active_head;
        }
    }

    pthread_mutex_unlock(&sched->lock);
    return false;
}
```
```cpp
#include <iostream>
#include <vector>
#include <deque>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <unordered_map>
#include <cstdint>

// Опис RPC-запиту
struct Request {
    uint64_t req_id{0};
    uint32_t tenant_id{0};
    uint32_t cost_units{1}; // Вартість у байтах або мікросекундах CPU
    std::string payload;
};

// Черга орендаря
class FlowQueue {
public:
    uint32_t tenant_id;
    uint32_t quantum;
    int32_t  deficit_counter{0};
    std::deque<Request> buffer;
    size_t   max_capacity{1024};

    FlowQueue(uint32_t id, uint32_t q, size_t cap = 1024)
        : tenant_id(id), quantum(q), max_capacity(cap) {}

    [[nodiscard]] bool is_empty() const noexcept {
        return buffer.empty();
    }

    [[nodiscard]] bool is_full() const noexcept {
        return buffer.size() >= max_capacity;
    }
};

// Потокобезпечний планувальник Deficit Round Robin
class DeficitRoundRobinScheduler {
public:
    DeficitRoundRobinScheduler() = default;

    void register_tenant(uint32_t tenant_id, uint32_t quantum) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (flows_.find(tenant_id) == flows_.end()) {
            flows_.emplace(tenant_id, std::make_shared<FlowQueue>(tenant_id, quantum));
        }
    }

    // Постановка запиту з контролем переповнення
    bool enqueue(Request req) {
        std::lock_guard<std::mutex> lock(mutex_);

        auto it = flows_.find(req.tenant_id);
        if (it == flows_.end() || it->second->is_full()) {
            return false; // Відхилення через невідомого клієнта або переповнення
        }

        auto& queue = it->second;
        bool was_empty = queue->is_empty();

        queue->buffer.push_back(std::move(req));

        if (was_empty) {
            // Потік повернувся з простою: скидаємо старий дефіцит і активуємо
            queue->deficit_counter = 0;
            active_flows_.push_back(queue);
            has_work_cv_.notify_one();
        }

        return true;
    }

    // Вибірка запиту за O(1)
    std::optional<Request> dequeue() {
        std::unique_lock<std::mutex> lock(mutex_);

        has_work_cv_.wait(lock, [this]() {
            return !active_flows_.empty() || shutdown_;
        });

        if (shutdown_ && active_flows_.empty()) {
            return std::nullopt;
        }

        while (!active_flows_.empty()) {
            auto current_queue = active_flows_.front();
            active_flows_.pop_front();

            // На початку раунду поповнюємо дефіцит на розмір кванта
            current_queue->deficit_counter += static_cast<int32_t>(current_queue->quantum);

            while (!current_queue->is_empty()) {
                const auto& head_req = current_queue->buffer.front();

                if (static_cast<int32_t>(head_req.cost_units) <= current_queue->deficit_counter) {
                    current_queue->deficit_counter -= static_cast<int32_t>(head_req.cost_units);
                    Request result = std::move(current_queue->buffer.front());
                    current_queue->buffer.pop_front();

                    // Якщо в черзі залишилися пакети — повертаємо її в активний список
                    if (!current_queue->is_empty()) {
                        active_flows_.push_front(current_queue);
                    } else {
                        // Черга порожня: обнуляємо дефіцит (Deficit Reset Rule)
                        current_queue->deficit_counter = 0;
                    }

                    return result;
                } else {
                    // Кванта недостатньо: зберігаємо дефіцит і відправляємо чергу в кінець кільця
                    break;
                }
            }

            if (!current_queue->is_empty()) {
                active_flows_.push_back(current_queue);
            } else {
                current_queue->deficit_counter = 0;
            }
        }

        return std::nullopt;
    }

    void shutdown() {
        std::lock_guard<std::mutex> lock(mutex_);
        shutdown_ = true;
        has_work_cv_.notify_all();
    }

private:
    std::mutex mutex_;
    std::condition_variable has_work_cv_;
    std::unordered_map<uint32_t, std::shared_ptr<FlowQueue>> flows_;
    std::deque<std::shared_ptr<FlowQueue>> active_flows_;
    bool shutdown_{false};
};
```
:::

## Інженерний аналіз та механізми захисту

Реалізація планувальника DRR у виробничих системах вимагає врахування низки критичних нюансів продуктивності, безпеки та точності обліку ресурсів:

### 1. Правило скидання дефіциту під час простою (Deficit Reset Rule)

Найнебезпечніша помилка в наївних реалізаціях DRR полягає у збереженні лічильника дефіциту, коли черга стає порожньою. Якщо клієнт не надсилав запитів протягом години, а планувальник продовжував нараховувати йому кванти кожного раунду, накопичений баланс сягне мільйонів одиниць. Коли такий клієнт раптово надішле пачку з 10 000 запитів, він повністю монополізує чергу виконання на кілька хвилин, порушуючи SLA всіх інших клієнтів.

У наведеному коді реалізовано строге правило: як тільки черга спустошується (`count == 0`), її `deficit_counter` примусово скидається в `0`, а сама черга видаляється зі списку активних. Коли клієнт надсилає новий запит після паузи, його обслуговування починається «з чистого аркуша» з додаванням рівно одного базового кванта.

### 2. Вибір розміру кванта (Quantum Sizing) та амортизована складність

Для забезпечення константної складності `O(1)` розмір кванта `Quantum` для черги з найменшою вагою повинен бути не меншим за максимальний можливий розмір одного запиту:

```
Quantum_min ≥ MaxRequestCost
```

Якщо це правило порушується (наприклад, максимальний запит важить 10 000 байтів, а квант становить лише 100 байтів), планувальнику знадобиться 100 холостих раундів лише для того, щоб накопичити достатньо дефіциту для пропуску одного пакета. Це призводить до надмірного навантаження на процесор через холості перемикання контексту між чергами.

Якщо ж встановити квант надмірно великим (наприклад, 10 МБ при середньому розмірі запиту 1 КБ), алгоритм деградує до звичайного пачкового Round-Robin, що суттєво збільшує миттєву затримку (Jitter) для дрібних інтерактивних клієнтів.

### 3. Стратегії оцінки вартості запитів (Cost Estimation)

У розподілених сервісах вага RPC-запиту (`cost_units`) не завжди відома наперед:
* **Апріорна оцінка (A-priori Cost):** вимірюється розмір вхідного HTTP-тіла або кількість запитаних ключів у batch-запиті. Це швидкий метод, доступний на етапі `enqueue()`.
* **Апостеріорна корекція (A-posteriori Feedback):** якщо виконання запиту спричинило важкий скан бази даних (наприклад, 200 мс замість очікуваних 2 мс), різниця вартості віднімається з дефіциту черги клієнта заднім числом у момент завершення обробки. Якщо дефіцит стає від'ємним, наступні запити цього клієнта чекатимуть кілька раундів для компенсації перевитрат.

### 4. Покрокове простеження обробки (Execution Trace)

Розглянемо практичний сценарій з двома активними клієнтами:
* Клієнт 1 (вага 1, `Quantum = 500`): має в черзі важкий запит вагою 800 байтів.
* Клієнт 2 (вага 1, `Quantum = 500`): має в черзі два легкі запити по 250 байтів.

*Раунд 1:*
1. Черга 1 отримує `Deficit = 500`. Перший запит важить 800. Оскільки `800 > 500`, запит не відправляється. Залишок дефіциту 500 переноситься на наступний раунд.
2. Черга 2 отримує `Deficit = 500`. Перший запит важить 250. Планувальник виконує запит, `Deficit = 500 - 250 = 250`. Другий запит важить 250. Планувальник виконує і його, `Deficit = 250 - 250 = 0`. Черга 2 стає порожньою і вибуває з активного кільця.

*Раунд 2:*
1. Черга 1 поповнює дефіцит: `Deficit = 500 (старий) + 500 (квант) = 1000`. Оскільки `800 ≤ 1000`, важкий запит успішно відправляється, а залишок `Deficit = 1000 - 800 = 200` зберігається.

Цей ланцюжок наочно показує, що легкий клієнт отримав свої відповіді миттєво в першому ж раунді, тоді як важкий запит був затриманий рівно на час накопичення своєї справедливої квоти.

### 5. Багатопотокова синхронізація та мінімізація Lock Contention

У запропонованій реалізації доступ до стану синхронізується через `mutex` та `condition_variable`. За умов високого навантаження (понад 500 000 RPS) єдиний м'ютекс планувальника може стати точкою між'ядерної конкуренції (Cache Line Bouncing).

Для високопродуктивних L7-проксі застосовують архітектуру Shared-Nothing: кожен потік подій (Worker Event Loop) має власний незалежний екземпляр планувальника DRR, а вхідні TCP-з'єднання розподіляються між воркерами за допомогою механізму ядра Linux `SO_REUSEPORT` або eBPF-програми `sockops`. Це дозволяє здійснювати планування в пам'яті окремого ядра процесора без міжпотокових блокувань.
