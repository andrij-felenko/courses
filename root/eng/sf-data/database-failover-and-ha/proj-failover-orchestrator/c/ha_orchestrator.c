/* ha_orchestrator.c — Демон координатора відмовостійкості баз даних */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>

#define CLUSTER_NAME     "batman_cluster"
#define LEASE_TTL_MS     10000
#define HEARTBEAT_INT_MS 2000
#define RETRY_TIMEOUT_MS 5000

typedef uint64_t lsn_t;

typedef enum {
    STATE_STANDBY_FOLLOWER,
    STATE_LEADER_ACTIVE,
    STATE_LEADER_DEMOTING,
    STATE_FAILOVER_ELECTING,
    STATE_FENCED_ISOLATED
} node_state_t;

typedef struct {
    char node_id[64];
    node_state_t state;
    lsn_t current_lsn;
    uint64_t lease_expiry_mono_ms;
    bool is_healthy;
    pthread_mutex_t lock;
    pthread_cond_t cond;
    bool running;
} orchestrator_ctx_t;

/* Отримання поточного монотонного часу в мілісекундах */
static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Імітація виклику до Distributed Consensus Store (etcd / Consul) */
static bool dcs_try_acquire_or_renew_lease(const char* node_id, uint32_t ttl_ms, uint64_t* new_expiry_ms) {
    /* Симуляція мережевого запису в DCS: атомарна транзакція CAS (Compare-And-Swap) */
    uint64_t now = get_monotonic_ms();
    *new_expiry_ms = now + ttl_ms;
    return true;
}

/* Імітація безпечної ізоляції (Fencing / STONITH) */
static bool execute_node_fencing(const char* target_node_id) {
    /* У реальній системі: виклик IPMI / AWS StopInstances / анулювання сесії */
    fprintf(stdout, "[FENCING] Успішно ізольовано вузол: %s (живлення вимкнено)\n", target_node_id);
    return true;
}

/* Промоушен локальної СКБД (перехід у Read-Write) */
static bool pg_promote_local_db(orchestrator_ctx_t* ctx) {
    fprintf(stdout, "[PROMOTION] Виконання pg_promote() для вузла %s (LSN: 0x%lX)\n",
            ctx->node_id, ctx->current_lsn);
    /* Імітація успішного перемикання таймлайну */
    return true;
}

/* Примусовий перевід у Read-Only / зупинка для уникнення Split-Brain */
static void pg_demote_local_db(orchestrator_ctx_t* ctx) {
    fprintf(stderr, "[DEMOTION] Втрата лізу! Примусова ізоляція лідера %s (Read-Only mode)\n",
            ctx->node_id);
}

/* Потік утримання оренди лідером (Heartbeat Loop) */
static void* leader_heartbeat_thread(void* arg) {
    orchestrator_ctx_t* ctx = (orchestrator_ctx_t*)arg;

    while (ctx->running) {
        pthread_mutex_lock(&ctx->lock);
        if (ctx->state != STATE_LEADER_ACTIVE) {
            pthread_mutex_unlock(&ctx->lock);
            break;
        }

        uint64_t new_exp = 0;
        bool ok = dcs_try_acquire_or_renew_lease(ctx->node_id, LEASE_TTL_MS, &new_exp);
        if (ok) {
            ctx->lease_expiry_mono_ms = new_exp;
            ctx->current_lsn += 0x1000; /* Імітація генерації WAL транзакціями */
            pthread_mutex_unlock(&ctx->lock);
        } else {
            /* Якщо не змогли продовжити ліз за час безпеки — аварійний Demote */
            ctx->state = STATE_LEADER_DEMOTING;
            pthread_mutex_unlock(&ctx->lock);
            pg_demote_local_db(ctx);
            break;
        }

        usleep(HEARTBEAT_INT_MS * 1000);
    }
    return NULL;
}

/* Виконання процедури виборів та Failover */
bool orchestrator_run_failover_cycle(orchestrator_ctx_t* ctx, const char* failed_leader_id, lsn_t max_known_lsn) {
    pthread_mutex_lock(&ctx->lock);
    
    if (ctx->state != STATE_STANDBY_FOLLOWER) {
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    ctx->state = STATE_FAILOVER_ELECTING;
    fprintf(stdout, "[ELECTION] Початок виборів. Локальний LSN: 0x%lX, Максимальний у кластері: 0x%lX\n",
            ctx->current_lsn, max_known_lsn);

    /* Кандидат має право обиратися лише якщо його LSN не відстає від найсвіжішого */
    if (ctx->current_lsn < max_known_lsn) {
        fprintf(stderr, "[ELECTION] Відхилено: локальний вузол відстає за LSN від найсвіжішої репліки\n");
        ctx->state = STATE_STANDBY_FOLLOWER;
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    /* 1. Обов'язкова ізоляція старого лідера перед промоушеном */
    if (!execute_node_fencing(failed_leader_id)) {
        fprintf(stderr, "[ELECTION] Помилка fencing старого лідера. Промоушен скасовано для безпеки\n");
        ctx->state = STATE_STANDBY_FOLLOWER;
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    /* 2. Захоплення лізу в DCS */
    uint64_t expiry = 0;
    if (!dcs_try_acquire_or_renew_lease(ctx->node_id, LEASE_TTL_MS, &expiry)) {
        fprintf(stderr, "[ELECTION] Не вдалося захопити ключ лідера в DCS (конфлікт CAS)\n");
        ctx->state = STATE_STANDBY_FOLLOWER;
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    /* 3. Промоушен бази даних */
    if (!pg_promote_local_db(ctx)) {
        fprintf(stderr, "[FATAL] Помилка команди pg_promote()!\n");
        ctx->state = STATE_FENCED_ISOLATED;
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    ctx->state = STATE_LEADER_ACTIVE;
    ctx->lease_expiry_mono_ms = expiry;
    pthread_mutex_unlock(&ctx->lock);

    /* Запуск потоку оновлення оренди для нового лідера */
    pthread_t hb_tid;
    pthread_create(&hb_tid, NULL, leader_heartbeat_thread, ctx);
    pthread_detach(hb_tid);

    fprintf(stdout, "[SUCCESS] Вузол %s успішно підвищено до Primary лідера кластера!\n", ctx->node_id);
    return true;
}

int main(void) {
    orchestrator_ctx_t ctx;
    memset(&ctx, 0, sizeof(ctx));
    strncpy(ctx.node_id, "pg-node-02.prod", sizeof(ctx.node_id) - 1);
    ctx.state = STATE_STANDBY_FOLLOWER;
    ctx.current_lsn = 0x1A004F00;
    ctx.running = true;
    pthread_mutex_init(&ctx.lock, NULL);
    pthread_cond_init(&ctx.cond, NULL);

    fprintf(stdout, "Запуск HA оркестратора для вузла %s...\n", ctx.node_id);
    
    /* Імітація виявлення аварії лідера pg-node-01 */
    lsn_t cluster_max_lsn = 0x1A004F00;
    bool promoted = orchestrator_run_failover_cycle(&ctx, "pg-node-01.prod", cluster_max_lsn);

    if (promoted) {
        /* Імітація роботи лідера протягом 4 секунд */
        sleep(4);
    }

    ctx.running = false;
    pthread_mutex_destroy(&ctx.lock);
    pthread_cond_destroy(&ctx.cond);
    return 0;
}
