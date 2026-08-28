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
