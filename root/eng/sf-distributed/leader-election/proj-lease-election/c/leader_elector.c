/* leader_elector.c - Промислова реалізація виборів лідера мовою C (POSIX) */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <errno.h>

/* --- Імітатор розподіленого координатора консенсусу (etcd / Consul) --- */

typedef struct {
    pthread_mutex_t lock;
    char leader_id[64];
    uint64_t fencing_token;    /* Монотонний лічильник епох (ревізія) */
    struct timespec expiry_ts; /* Момент закінчення лізи на монотонному годиннику */
    bool is_allocated;
} mock_coordinator_t;

static mock_coordinator_t g_coordinator = {
    .lock = PTHREAD_MUTEX_INITIALIZER,
    .leader_id = {0},
    .fencing_token = 0,
    .is_allocated = false
};

/* Отримати поточний час монотонного годинника в мілісекундах */
static int64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + (ts.tv_nsec / 1000000);
}

/* Спроба атомарного захоплення лізи (Compare-And-Swap) */
static bool coordinator_try_acquire(const char* candidate_id, uint32_t ttl_ms, uint64_t* out_token) {
    pthread_mutex_lock(&g_coordinator.lock);
    int64_t now = get_monotonic_ms();
    int64_t expiry = (int64_t)g_coordinator.expiry_ts.tv_sec * 1000 + (g_coordinator.expiry_ts.tv_nsec / 1000000);

    bool can_acquire = false;
    if (!g_coordinator.is_allocated || now >= expiry) {
        /* Ліза вільна або прострочена -> захоплюємо */
        can_acquire = true;
    } else if (strcmp(g_coordinator.leader_id, candidate_id) == 0) {
        /* Вже є лідером -> поновлюємо */
        can_acquire = true;
    }

    if (can_acquire) {
        strncpy(g_coordinator.leader_id, candidate_id, sizeof(g_coordinator.leader_id) - 1);
        g_coordinator.fencing_token++;
        *out_token = g_coordinator.fencing_token;
        g_coordinator.is_allocated = true;

        int64_t new_expiry = now + ttl_ms;
        g_coordinator.expiry_ts.tv_sec = new_expiry / 1000;
        g_coordinator.expiry_ts.tv_nsec = (new_expiry % 1000) * 1000000;
    }

    pthread_mutex_unlock(&g_coordinator.lock);
    return can_acquire;
}

/* Поновлення наявної лізи (Keep-Alive) */
static bool coordinator_renew_lease(const char* leader_id, uint64_t token, uint32_t ttl_ms) {
    pthread_mutex_lock(&g_coordinator.lock);
    int64_t now = get_monotonic_ms();
    int64_t expiry = (int64_t)g_coordinator.expiry_ts.tv_sec * 1000 + (g_coordinator.expiry_ts.tv_nsec / 1000000);

    bool ok = false;
    if (g_coordinator.is_allocated &&
        now < expiry &&
        strcmp(g_coordinator.leader_id, leader_id) == 0 &&
        g_coordinator.fencing_token == token) {
        
        int64_t new_expiry = now + ttl_ms;
        g_coordinator.expiry_ts.tv_sec = new_expiry / 1000;
        g_coordinator.expiry_ts.tv_nsec = (new_expiry % 1000) * 1000000;
        ok = true;
    }
    pthread_mutex_unlock(&g_coordinator.lock);
    return ok;
}

/* Явне звільнення лізи (Graceful Resign) */
static void coordinator_resign(const char* leader_id, uint64_t token) {
    pthread_mutex_lock(&g_coordinator.lock);
    if (g_coordinator.is_allocated &&
        strcmp(g_coordinator.leader_id, leader_id) == 0 &&
        g_coordinator.fencing_token == token) {
        g_coordinator.is_allocated = false;
        memset(g_coordinator.leader_id, 0, sizeof(g_coordinator.leader_id));
    }
    pthread_mutex_unlock(&g_coordinator.lock);
}

/* --- Захищене сховище з перевіркою фенсингового токена --- */

typedef struct {
    pthread_mutex_t lock;
    uint64_t last_seen_token;
    int balance;
} mock_storage_t;

static mock_storage_t g_storage = {
    .lock = PTHREAD_MUTEX_INITIALIZER,
    .last_seen_token = 0,
    .balance = 1000
};

static bool storage_mutate(uint64_t token, int delta, const char* caller_id) {
    pthread_mutex_lock(&g_storage.lock);
    if (token < g_storage.last_seen_token) {
        printf("[%s] ВІДХИЛЕНО: Токен %lu застарілий! Останній прийнятий: %lu\n",
               caller_id, (unsigned long)token, (unsigned long)g_storage.last_seen_token);
        pthread_mutex_unlock(&g_storage.lock);
        return false;
    }
    g_storage.last_seen_token = token;
    g_storage.balance += delta;
    printf("[%s] УСПІХ: Мутація з токеном %lu прийнята. Баланс = %d\n",
           caller_id, (unsigned long)token, g_storage.balance);
    pthread_mutex_unlock(&g_storage.lock);
    return true;
}

/* --- Клієнтський модуль виборів лідера --- */

typedef struct {
    char node_id[64];
    uint32_t lease_ttl_ms;
    uint32_t renew_interval_ms;
    uint32_t retry_interval_ms;

    volatile bool running;
    volatile bool is_leading;
    volatile bool cancel_payload;
    uint64_t current_token;

    pthread_t election_thread;
    pthread_t payload_thread;
    pthread_mutex_t state_lock;
} leader_elector_t;

/* Фонова корисна робота активного лідера */
static void* leader_payload_worker(void* arg) {
    leader_elector_t* elector = (leader_elector_t*)arg;
    printf("[%s] Лідер розпочав виконання монопольних бізнес-задач.\n", elector->node_id);

    while (elector->running && elector->is_leading && !elector->cancel_payload) {
        /* Виконуємо транзакцію білінгу раз на 800 мс */
        storage_mutate(elector->current_token, 50, elector->node_id);
        usleep(800000);
    }

    printf("[%s] Лідер зупинив виконання бізнес-задач (cancel=%d).\n",
           elector->node_id, elector->cancel_payload);
    return NULL;
}

/* Основний цикл управління лідерством */
static void* election_loop(void* arg) {
    leader_elector_t* elector = (leader_elector_t*)arg;

    while (elector->running) {
        if (!elector->is_leading) {
            /* Стан STANDBY: пробуємо захопити лізу */
            uint64_t token = 0;
            if (coordinator_try_acquire(elector->node_id, elector->lease_ttl_ms, &token)) {
                pthread_mutex_lock(&elector->state_lock);
                elector->is_leading = true;
                elector->cancel_payload = false;
                elector->current_token = token;
                printf(">>> [%s] СТАВ ЛІДЕРОМ! Отримано Fencing Token = %lu <<<\n",
                       elector->node_id, (unsigned long)token);
                
                pthread_create(&elector->payload_thread, NULL, leader_payload_worker, elector);
                pthread_mutex_unlock(&elector->state_lock);
            } else {
                usleep(elector->retry_interval_ms * 1000);
            }
        } else {
            /* Стан LEADER: оновлюємо лізу (Keep-Alive) */
            usleep(elector->renew_interval_ms * 1000);

            if (!elector->running) break;

            if (!coordinator_renew_lease(elector->node_id, elector->current_token, elector->lease_ttl_ms)) {
                /* Втрата лізи через таймаут або збій */
                printf("!!! [%s] ВТРАТА ЛІДЕРСТВА: Не вдалося поновити лізу! !!!\n", elector->node_id);

                pthread_mutex_lock(&elector->state_lock);
                elector->is_leading = false;
                elector->cancel_payload = true;
                pthread_mutex_unlock(&elector->state_lock);

                pthread_join(elector->payload_thread, NULL);
            }
        }
    }

    if (elector->is_leading) {
        coordinator_resign(elector->node_id, elector->current_token);
        elector->is_leading = false;
        elector->cancel_payload = true;
        pthread_join(elector->payload_thread, NULL);
    }
    return NULL;
}

void leader_elector_init(leader_elector_t* elector, const char* id, uint32_t ttl_ms) {
    strncpy(elector->node_id, id, sizeof(elector->node_id) - 1);
    elector->lease_ttl_ms = ttl_ms;
    elector->renew_interval_ms = ttl_ms / 3;     /* Серцебиття раз на 1/3 TTL */
    elector->retry_interval_ms = ttl_ms / 4;
    elector->running = true;
    elector->is_leading = false;
    elector->cancel_payload = false;
    elector->current_token = 0;
    pthread_mutex_init(&elector->state_lock, NULL);
    pthread_create(&elector->election_thread, NULL, election_loop, elector);
}

void leader_elector_stop(leader_elector_t* elector) {
    elector->running = false;
    pthread_join(elector->election_thread, NULL);
    pthread_mutex_destroy(&elector->state_lock);
}

/* Демонстрація відмови лідера та захисту токеном */
int main(void) {
    printf("=== Старт кластера виборів лідера ===\n");
    leader_elector_t node_a, node_b;

    leader_elector_init(&node_a, "Вузол-A", 1500); /* TTL = 1.5 секунди */
    usleep(200000);
    leader_elector_init(&node_b, "Вузол-B", 1500);

    /* Даємо Вузлу-A попрацювати лідером 2.5 секунди */
    sleep(2);

    printf("\n--- Імітація аварійної GC-паузи / зависання Вузла-A на 3 секунди ---\n");
    /* Примусово блокуємо роботу Вузла-A (імітація freeze) */
    pthread_mutex_lock(&node_a.state_lock);
    sleep(3); /* Вузол-B за цей час перехопить лідерство і виконає мутацію */
    pthread_mutex_unlock(&node_a.state_lock);

    sleep(2);

    leader_elector_stop(&node_a);
    leader_elector_stop(&node_b);
    printf("=== Роботу кластера завершено ===\n");
    return 0;
}
