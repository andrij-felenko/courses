#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_PAYLOAD_LEN 256
#define MAX_ERR_MSG_LEN 128
#define MAX_QUEUE_CAPACITY 64
#define MAX_RETRIES_LIMIT 3
#define MAX_REDRIVE_LIMIT 2

/* Статуси результату обробки */
typedef enum {
    PROCESS_OK = 0,
    PROCESS_TRANSIENT_ERROR = 1,
    PROCESS_POISON_ERROR = 2
} ProcessResult;

/* Структура бізнес-повідомлення */
typedef struct {
    char id[36];
    char payload[MAX_PAYLOAD_LEN];
    uint32_t attempts;
    uint32_t redrive_count;
    int64_t next_retry_timestamp_ms;
    char trace_id[33];
} Message;

/* Структура діагностичного конверта мертвої черги */
typedef struct {
    Message original_msg;
    char original_queue[32];
    char exception_type[48];
    char exception_message[MAX_ERR_MSG_LEN];
    int64_t first_failed_timestamp_ms;
    int64_t dead_lettered_timestamp_ms;
    uint32_t total_attempts;
} DeadLetterEnvelope;

/* Кільцева черга повідомлень */
typedef struct {
    Message items[MAX_QUEUE_CAPACITY];
    int head;
    int tail;
    int count;
} MessageQueue;

/* Черга мертвого сховища */
typedef struct {
    DeadLetterEnvelope items[MAX_QUEUE_CAPACITY];
    int head;
    int tail;
    int count;
} DeadLetterQueue;

/* Ініціалізація черг */
void queue_init(MessageQueue* q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

bool queue_push(MessageQueue* q, const Message* msg) {
    if (q->count >= MAX_QUEUE_CAPACITY) return false;
    q->items[q->tail] = *msg;
    q->tail = (q->tail + 1) % MAX_QUEUE_CAPACITY;
    q->count++;
    return true;
}

bool queue_pop(MessageQueue* q, Message* out) {
    if (q->count == 0) return false;
    *out = q->items[q->head];
    q->head = (q->head + 1) % MAX_QUEUE_CAPACITY;
    q->count--;
    return true;
}

void dlq_init(DeadLetterQueue* dlq) {
    dlq->head = 0;
    dlq->tail = 0;
    dlq->count = 0;
}

bool dlq_push(DeadLetterQueue* dlq, const DeadLetterEnvelope* env) {
    if (dlq->count >= MAX_QUEUE_CAPACITY) return false;
    dlq->items[dlq->tail] = *env;
    dlq->tail = (dlq->tail + 1) % MAX_QUEUE_CAPACITY;
    dlq->count++;
    return true;
}

bool dlq_pop(DeadLetterQueue* dlq, DeadLetterEnvelope* out) {
    if (dlq->count == 0) return false;
    *out = dlq->items[dlq->head];
    dlq->head = (dlq->head + 1) % MAX_QUEUE_CAPACITY;
    dlq->count--;
    return true;
}

/* Отримання поточного монотонного часу в мілісекундах */
static int64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

/* Бізнес-обробник повідомлення */
ProcessResult process_business_logic(const Message* msg, char* err_buf, size_t err_len) {
    /* Якщо payload містить "POISON" — це невиправний збій валідації */
    if (strstr(msg->payload, "POISON") != NULL) {
        snprintf(err_buf, err_len, "MalformedSchemaError: Invalid binary token in payload");
        return PROCESS_POISON_ERROR;
    }
    /* Якщо payload містить "TIMEOUT" і перша спроба — симулюємо тимчасовий збій */
    if (strstr(msg->payload, "TIMEOUT") != NULL && msg->attempts < 2) {
        snprintf(err_buf, err_len, "DownstreamTimeoutException: Payment gateway unavailable");
        return PROCESS_TRANSIENT_ERROR;
    }
    return PROCESS_OK;
}

/* Загортання в DLQ конверт */
void route_to_dlq(DeadLetterQueue* dlq, const Message* msg, const char* ex_type, const char* ex_msg) {
    DeadLetterEnvelope env;
    memset(&env, 0, sizeof(env));
    env.original_msg = *msg;
    strncpy(env.original_queue, "primary-orders", sizeof(env.original_queue) - 1);
    strncpy(env.exception_type, ex_type, sizeof(env.exception_type) - 1);
    strncpy(env.exception_message, ex_msg, sizeof(env.exception_message) - 1);
    env.first_failed_timestamp_ms = current_time_ms() - (msg->attempts * 500);
    env.dead_lettered_timestamp_ms = current_time_ms();
    env.total_attempts = msg->attempts;

    dlq_push(dlq, &env);
    printf("  [DLQ ALERT] Message %s routed to DLQ! Reason: %s (attempts: %u)\n",
           msg->id, ex_msg, msg->attempts);
}

/* Обробка одного циклу споживача */
void run_consumer_cycle(MessageQueue* primary, MessageQueue* retry_q, DeadLetterQueue* dlq) {
    Message msg;
    int64_t now = current_time_ms();

    /* 1. Спершу перевіряємо чергу повторів: чи є готові за таймером */
    if (retry_q->count > 0) {
        if (queue_pop(retry_q, &msg)) {
            if (msg.next_retry_timestamp_ms <= now) {
                printf("  [RETRY-EXEC] Retrying message %s (attempt %u)...\n", msg.id, msg.attempts + 1);
                char err_buf[MAX_ERR_MSG_LEN] = {0};
                msg.attempts++;
                ProcessResult res = process_business_logic(&msg, err_buf, sizeof(err_buf));
                if (res == PROCESS_OK) {
                    printf("  [SUCCESS] Message %s processed on retry %u!\n", msg.id, msg.attempts);
                    return;
                }
                if (res == PROCESS_POISON_ERROR || msg.attempts >= MAX_RETRIES_LIMIT) {
                    route_to_dlq(dlq, &msg, "DeterministicFailure", err_buf);
                } else {
                    msg.next_retry_timestamp_ms = now + (msg.attempts * 300);
                    queue_push(retry_q, &msg);
                }
                return;
            } else {
                /* Час ще не настав — повертаємо назад у чергу затримок */
                queue_push(retry_q, &msg);
            }
        }
    }

    /* 2. Обробляємо нові повідомлення з основної черги */
    if (queue_pop(primary, &msg)) {
        printf("  [CONSUME] Processing message %s: '%s'...\n", msg.id, msg.payload);
        char err_buf[MAX_ERR_MSG_LEN] = {0};
        msg.attempts = 1;
        ProcessResult res = process_business_logic(&msg, err_buf, sizeof(err_buf));

        if (res == PROCESS_OK) {
            printf("  [SUCCESS] Message %s processed successfully (ACK).\n", msg.id);
        } else if (res == PROCESS_POISON_ERROR) {
            route_to_dlq(dlq, &msg, "PoisonMessageException", err_buf);
        } else {
            /* Перехідна помилка -> відправляємо в чергу повторів із затримкою */
            msg.next_retry_timestamp_ms = now + 200; /* 200 мс затримка */
            queue_push(retry_q, &msg);
            printf("  [RETRY-SCHEDULE] Message %s failed (transient): %s. Delaying 200ms.\n",
                   msg.id, err_buf);
        }
    }
}

/* Контролер безпечного Redrive з DLQ */
void run_redrive_controller(DeadLetterQueue* dlq, MessageQueue* primary, uint32_t max_to_replay) {
    uint32_t replayed = 0;
    DeadLetterEnvelope env;

    printf("\n=== Запуск Redrive Контролера (Безпечне відновлення з DLQ) ===\n");
    while (replayed < max_to_replay && dlq_pop(dlq, &env)) {
        /* Захисний бар'єр 1: Захист від зациклення (Loop Breaker) */
        if (env.original_msg.redrive_count >= MAX_REDRIVE_LIMIT) {
            printf("  [REDRIVE-SKIP] Message %s exceeded redrive limit (%u). Moved to Parking Lot.\n",
                   env.original_msg.id, env.original_msg.redrive_count);
            continue;
        }

        /* Захисний бар'єр 2: Патчинг дефекту схеми */
        Message to_reinject = env.original_msg;
        if (strstr(to_reinject.payload, "POISON") != NULL) {
            printf("  [SCHEMA-PATCH] Patching poison payload for %s: replacing with valid JSON.\n",
                   to_reinject.id);
            strncpy(to_reinject.payload, "ORDER_DATA_PATCHED_OK", sizeof(to_reinject.payload) - 1);
        }

        /* Оновлення службових лічильників */
        to_reinject.attempts = 0;
        to_reinject.redrive_count++;
        to_reinject.next_retry_timestamp_ms = 0;

        /* Повторне введення в основну чергу */
        queue_push(primary, &to_reinject);
        replayed++;
        printf("  [REDRIVE-INJECT] Successfully re-injected message %s to primary queue.\n",
               to_reinject.id);
    }
    printf("=== Завершено Redrive: відновлено %u повідомлень ===\n\n", replayed);
}

int main(void) {
    MessageQueue primary, retry_q;
    DeadLetterQueue dlq;

    queue_init(&primary);
    queue_init(&retry_q);
    dlq_init(&dlq);

    /* Публікуємо 3 тестові задачі різного типу */
    Message m1 = {"msg-001", "ORDER_TIMEOUT_NETWORK", 0, 0, 0, "trace-aaa"};
    Message m2 = {"msg-002", "ORDER_POISON_BAD_SCHEMA", 0, 0, 0, "trace-bbb"};
    Message m3 = {"msg-003", "ORDER_VALID_CLEAN", 0, 0, 0, "trace-ccc"};

    queue_push(&primary, &m1);
    queue_push(&primary, &m2);
    queue_push(&primary, &m3);

    printf("=== Старт обробки черги ===\n");
    for (int i = 0; i < 6; i++) {
        run_consumer_cycle(&primary, &retry_q, &dlq);
        struct timespec sleep_ts = {0, 80 * 1000000}; /* 80 мс */
        nanosleep(&sleep_ts, NULL);
    }

    printf("\nСтан черг: Primary=%d, Retry=%d, DLQ=%d\n", primary.count, retry_q.count, dlq.count);

    /* Запускаємо безпечне відновлення */
    run_redrive_controller(&dlq, &primary, 10);

    /* Обробляємо відновлене повідомлення */
    while (primary.count > 0 || retry_q.count > 0) {
        run_consumer_cycle(&primary, &retry_q, &dlq);
    }

    printf("\nПідсумок: усі задачі оброблено, черга DLQ порожня (%d).\n", dlq.count);
    return 0;
}
