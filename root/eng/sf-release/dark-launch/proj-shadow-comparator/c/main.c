#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <pthread.h>

#define QUEUE_CAPACITY 512
#define MAX_NAME_LEN 64
#define FLOAT_EPSILON 1e-6

/* Вхідні дані фінансового запиту */
typedef struct {
    uint64_t account_id;
    double amount;
    uint32_t currency_code;
    uint64_t client_timestamp_ms;
} TransactionRequest;

/* Результат обробки транзакції */
typedef struct {
    double base_fee;
    double tax_fee;
    double total_charged;
    uint32_t execution_node_id; /* Динамічне службове поле */
    bool is_successful;
} TransactionResult;

/* Сигнатура функції бізнес-логіки */
typedef TransactionResult (*ProcessingFn)(const TransactionRequest* req);

/* Опис окремого тіньового експерименту для черги */
typedef struct {
    char experiment_name[MAX_NAME_LEN];
    TransactionRequest request;
    TransactionResult control_result;
    uint64_t control_duration_us;
    ProcessingFn candidate_fn;
} ShadowTask;

/* Неблокуюча кільцева черга з м'ютексом та умовною змінною */
typedef struct {
    ShadowTask tasks[QUEUE_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    size_t total_dropped;
    bool is_terminating;
    pthread_mutex_t lock;
    pthread_cond_t has_items;
} ShadowQueue;

static ShadowQueue g_queue;
static pthread_t g_worker_thread;

/* Отримання поточного монотонного часу в мікросекундах */
static uint64_t get_monotonic_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)ts.tv_nsec / 1000ULL;
}

/* Нормалізований компаратор результатів */
static bool compare_transaction_results(const TransactionResult* ctrl,
                                        const TransactionResult* cand,
                                        char* diff_buffer,
                                        size_t diff_buf_size) {
    if (ctrl->is_successful != cand->is_successful) {
        snprintf(diff_buffer, diff_buf_size, "Статус успішності різниться: ctrl=%d, cand=%d",
                 ctrl->is_successful, cand->is_successful);
        return false;
    }

    if (fabs(ctrl->base_fee - cand->base_fee) > FLOAT_EPSILON) {
        snprintf(diff_buffer, diff_buf_size, "Розбіжність base_fee: ctrl=%.6f, cand=%.6f",
                 ctrl->base_fee, cand->base_fee);
        return false;
    }

    if (fabs(ctrl->tax_fee - cand->tax_fee) > FLOAT_EPSILON) {
        snprintf(diff_buffer, diff_buf_size, "Розбіжність tax_fee: ctrl=%.6f, cand=%.6f",
                 ctrl->tax_fee, cand->tax_fee);
        return false;
    }

    if (fabs(ctrl->total_charged - cand->total_charged) > FLOAT_EPSILON) {
        snprintf(diff_buffer, diff_buf_size, "Розбіжність total_charged: ctrl=%.6f, cand=%.6f",
                 ctrl->total_charged, cand->total_charged);
        return false;
    }

    /* execution_node_id є недетермінованим вузловим маршрутом і маскується */
    return true;
}

/* Цикл фонового потоку-обробника */
static void* shadow_worker_routine(void* arg) {
    (void)arg;
    char diff_msg[256];

    while (true) {
        ShadowTask task;

        pthread_mutex_lock(&g_queue.lock);
        while (g_queue.count == 0 && !g_queue.is_terminating) {
            pthread_cond_wait(&g_queue.has_items, &g_queue.lock);
        }

        if (g_queue.is_terminating && g_queue.count == 0) {
            pthread_mutex_unlock(&g_queue.lock);
            break;
        }

        task = g_queue.tasks[g_queue.head];
        g_queue.head = (g_queue.head + 1) % QUEUE_CAPACITY;
        g_queue.count--;
        pthread_mutex_unlock(&g_queue.lock);

        /* Виконання експериментальної функції із заміром затримки */
        uint64_t cand_start_us = get_monotonic_us();
        TransactionResult cand_res = task.candidate_fn(&task.request);
        uint64_t cand_duration_us = get_monotonic_us() - cand_start_us;

        /* Порівняння результатів */
        bool is_match = compare_transaction_results(&task.control_result, &cand_res,
                                                     diff_msg, sizeof(diff_msg));

        if (is_match) {
            printf("[МЕТРИКА ЗБІГУ] Експеримент '%s' (Акаунт: %lu) | Час: ctrl=%lu мкс, cand=%lu мкс\n",
                   task.experiment_name, task.request.account_id,
                   task.control_duration_us, cand_duration_us);
        } else {
            fprintf(stderr, "[РОЗБІЖНІСТЬ!] Експеримент '%s' (Акаунт: %lu) -> %s\n",
                    task.experiment_name, task.request.account_id, diff_msg);
        }
    }
    return NULL;
}

/* Ініціалізація інфраструктури */
void shadow_system_init(void) {
    g_queue.head = 0;
    g_queue.tail = 0;
    g_queue.count = 0;
    g_queue.total_dropped = 0;
    g_queue.is_terminating = false;
    pthread_mutex_init(&g_queue.lock, NULL);
    pthread_cond_init(&g_queue.has_items, NULL);
    pthread_create(&g_worker_thread, NULL, shadow_worker_routine, NULL);
}

/* Зупинка системи та коректне звільнення ресурсів */
void shadow_system_shutdown(void) {
    pthread_mutex_lock(&g_queue.lock);
    g_queue.is_terminating = true;
    pthread_cond_broadcast(&g_queue.has_items);
    pthread_mutex_unlock(&g_queue.lock);

    pthread_join(g_worker_thread, NULL);
    pthread_mutex_destroy(&g_queue.lock);
    pthread_cond_destroy(&g_queue.has_items);
}

/* Головна точка входу темного запуску */
TransactionResult run_with_dark_launch(const char* name,
                                       const TransactionRequest* req,
                                       ProcessingFn control_fn,
                                       ProcessingFn candidate_fn) {
    /* 1. Синхронний запуск контрольного рушія для клієнта */
    uint64_t ctrl_start_us = get_monotonic_us();
    TransactionResult ctrl_res = control_fn(req);
    uint64_t ctrl_duration_us = get_monotonic_us() - ctrl_start_us;

    /* 2. Неблокуюча спроба постановки в тіньову чергу */
    pthread_mutex_lock(&g_queue.lock);
    if (g_queue.count < QUEUE_CAPACITY) {
        ShadowTask* slot = &g_queue.tasks[g_queue.tail];
        strncpy(slot->experiment_name, name, MAX_NAME_LEN - 1);
        slot->experiment_name[MAX_NAME_LEN - 1] = '\0';
        slot->request = *req;
        slot->control_result = ctrl_res;
        slot->control_duration_us = ctrl_duration_us;
        slot->candidate_fn = candidate_fn;

        g_queue.tail = (g_queue.tail + 1) % QUEUE_CAPACITY;
        g_queue.count++;
        pthread_cond_signal(&g_queue.has_items);
    } else {
        g_queue.total_dropped++;
        /* Пропуск записується в лічильники без блокування виклику */
    }
    pthread_mutex_unlock(&g_queue.lock);

    /* 3. Клієнт негайно отримує перевірений результат */
    return ctrl_res;
}
