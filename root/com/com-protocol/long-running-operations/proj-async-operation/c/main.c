#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_OPERATIONS 128
#define LEASE_DURATION_SEC 2
#define HEARTBEAT_INTERVAL_SEC 1

typedef enum {
    OP_STATE_PENDING = 0,
    OP_STATE_RUNNING,
    OP_STATE_SUCCEEDED,
    OP_STATE_FAILED,
    OP_STATE_CANCELLED
} op_state_t;

typedef struct {
    char id[37];
    char owner_id[32];
    char idempotency_key[64];
    uint32_t payload_hash;
    op_state_t state;
    float progress;
    char stage[32];
    uint32_t attempt;
    uint64_t lease_token;
    time_t lease_until;
    bool cancel_requested;
    char result_url[128];
    time_t created_at;
    time_t updated_at;
    time_t expires_at;
} operation_record_t;

typedef struct {
    operation_record_t table[MAX_OPERATIONS];
    size_t count;
    pthread_mutex_t mutex;
    pthread_cond_t cv_task_available;
    bool shutdown_requested;
} database_engine_t;

static database_engine_t g_db;

void db_init(database_engine_t *db) {
    memset(db, 0, sizeof(*db));
    pthread_mutex_init(&db->mutex, NULL);
    pthread_cond_init(&db->cv_task_available, NULL);
    db->shutdown_requested = false;
}

void db_destroy(database_engine_t *db) {
    pthread_mutex_destroy(&db->mutex);
    pthread_cond_destroy(&db->cv_task_available);
}

/* Ініціалізація та прийом операції з перевіркою ідемпотентності */
bool db_submit_operation(database_engine_t *db, const char *id, const char *owner, 
                         const char *idem_key, uint32_t hash, operation_record_t *out_op) {
    pthread_mutex_lock(&db->mutex);
    time_t now = time(NULL);

    /* 1. Перевірка існуючого ключа ідемпотентності */
    if (idem_key && strlen(idem_key) > 0) {
        for (size_t i = 0; i < db->count; ++i) {
            if (strcmp(db->table[i].owner_id, owner) == 0 && 
                strcmp(db->table[i].idempotency_key, idem_key) == 0) {
                if (db->table[i].payload_hash != hash) {
                    pthread_mutex_unlock(&db->mutex);
                    return false; /* 422 Conflict: підміна корисного навантаження */
                }
                memcpy(out_op, &db->table[i], sizeof(operation_record_t));
                pthread_mutex_unlock(&db->mutex);
                return true; /* Повернення існуючої операції */
            }
        }
    }

    if (db->count >= MAX_OPERATIONS) {
        pthread_mutex_unlock(&db->mutex);
        return false;
    }

    /* 2. Вставка нового запису */
    operation_record_t *rec = &db->table[db->count++];
    memset(rec, 0, sizeof(*rec));
    strncpy(rec->id, id, sizeof(rec->id) - 1);
    strncpy(rec->owner_id, owner, sizeof(rec->owner_id) - 1);
    if (idem_key) strncpy(rec->idempotency_key, idem_key, sizeof(rec->idempotency_key) - 1);
    rec->payload_hash = hash;
    rec->state = OP_STATE_PENDING;
    rec->progress = 0.0f;
    strncpy(rec->stage, "queued", sizeof(rec->stage) - 1);
    rec->created_at = now;
    rec->updated_at = now;
    rec->expires_at = now + 86400;

    memcpy(out_op, rec, sizeof(operation_record_t));
    pthread_cond_signal(&db->cv_task_available);
    pthread_mutex_unlock(&db->mutex);
    return true;
}

/* Захоплення оренди воркером (аналог SKIP LOCKED) */
bool db_claim_next_task(database_engine_t *db, uint64_t worker_token, operation_record_t *out_task) {
    pthread_mutex_lock(&db->mutex);
    time_t now = time(NULL);

    while (!db->shutdown_requested) {
        for (size_t i = 0; i < db->count; ++i) {
            operation_record_t *rec = &db->table[i];
            bool is_pending = (rec->state == OP_STATE_PENDING);
            bool is_expired = (rec->state == OP_STATE_RUNNING && rec->lease_until < now);

            if (is_pending || is_expired) {
                rec->state = OP_STATE_RUNNING;
                rec->attempt++;
                rec->lease_token = worker_token;
                rec->lease_until = now + LEASE_DURATION_SEC;
                rec->updated_at = now;
                strncpy(rec->stage, "processing", sizeof(rec->stage) - 1);

                memcpy(out_task, rec, sizeof(operation_record_t));
                pthread_mutex_unlock(&db->mutex);
                return true;
            }
        }
        pthread_cond_wait(&db->cv_task_available, &db->mutex);
    }

    pthread_mutex_unlock(&db->mutex);
    return false;
}

/* Серцебиття для подовження оренди та фіксації прогресу */
bool db_heartbeat(database_engine_t *db, const char *op_id, uint64_t token, float prog, const char *stage, bool *out_cancel) {
    pthread_mutex_lock(&db->mutex);
    time_t now = time(NULL);

    for (size_t i = 0; i < db->count; ++i) {
        operation_record_t *rec = &db->table[i];
        if (strcmp(rec->id, op_id) == 0) {
            if (rec->state != OP_STATE_RUNNING || rec->lease_token != token || rec->lease_until < now) {
                pthread_mutex_unlock(&db->mutex);
                return false; /* Оренду втрачено або перехоплено */
            }

            rec->lease_until = now + LEASE_DURATION_SEC;
            rec->progress = prog;
            if (stage) strncpy(rec->stage, stage, sizeof(rec->stage) - 1);
            rec->updated_at = now;
            if (out_cancel) *out_cancel = rec->cancel_requested;

            pthread_mutex_unlock(&db->mutex);
            return true;
        }
    }

    pthread_mutex_unlock(&db->mutex);
    return false;
}

/* Фіксація результату з перевіркою токена оренди */
bool db_commit_success(database_engine_t *db, const char *op_id, uint64_t token, const char *res_url) {
    pthread_mutex_lock(&db->mutex);
    time_t now = time(NULL);

    for (size_t i = 0; i < db->count; ++i) {
        operation_record_t *rec = &db->table[i];
        if (strcmp(rec->id, op_id) == 0) {
            if (rec->state != OP_STATE_RUNNING || rec->lease_token != token || rec->lease_until < now) {
                pthread_mutex_unlock(&db->mutex);
                return false; /* Спроба запису зомбі-виконавця відхилена */
            }

            rec->state = OP_STATE_SUCCEEDED;
            rec->progress = 1.0f;
            strncpy(rec->stage, "completed", sizeof(rec->stage) - 1);
            strncpy(rec->result_url, res_url, sizeof(rec->result_url) - 1);
            rec->updated_at = now;

            pthread_mutex_unlock(&db->mutex);
            return true;
        }
    }

    pthread_mutex_unlock(&db->mutex);
    return false;
}

/* Життєвий цикл потоку-воркера */
void *worker_thread_func(void *arg) {
    uint64_t worker_id = (uint64_t)(uintptr_t)arg;
    operation_record_t task;

    while (db_claim_next_task(&g_db, worker_id, &task)) {
        printf("[Worker %lu] Захоплено задачу %s (спроба %u)\n", worker_id, task.id, task.attempt);

        bool aborted = false;
        for (int step = 1; step <= 3; ++step) {
            sleep(1);
            float current_prog = (float)step / 3.0f;
            bool cancel_sig = false;

            if (!db_heartbeat(&g_db, task.id, worker_id, current_prog, "computing", &cancel_sig)) {
                printf("[Worker %lu] Помилка: втрачено оренду для %s!\n", worker_id, task.id);
                aborted = true;
                break;
            }

            if (cancel_sig) {
                printf("[Worker %lu] Виявлено запит на скасування для %s\n", worker_id, task.id);
                aborted = true;
                break;
            }
        }

        if (!aborted) {
            char final_url[128];
            snprintf(final_url, sizeof(final_url), "/reports/%s.pdf", task.id);
            if (db_commit_success(&g_db, task.id, worker_id, final_url)) {
                printf("[Worker %lu] Успішно завершено задачу %s -> %s\n", worker_id, task.id, final_url);
            }
        }
    }
    return NULL;
}
