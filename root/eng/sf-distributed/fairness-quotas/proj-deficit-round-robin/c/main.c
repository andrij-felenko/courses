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
