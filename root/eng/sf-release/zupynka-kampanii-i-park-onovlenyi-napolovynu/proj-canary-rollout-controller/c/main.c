#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define MAX_SAMPLES_CAPACITY 1024
#define MAX_TARGET_NODES 64
#define MAX_ERROR_LOGS 128

typedef enum {
    STAGE_IDLE = 0,
    STAGE_INITIALIZING = 1,
    STAGE_PROMOTING_COHORT = 2,
    STAGE_SOAKING = 3,
    STAGE_EVALUATING_ACA = 4,
    STAGE_EMERGENCY_KILL_SWITCH = 5,
    STAGE_QUARANTINE_DRAINING = 6,
    STAGE_ROLLED_BACK = 7,
    STAGE_PROMOTED_FULL = 8
} rollout_state_t;

typedef struct {
    double latency_samples[MAX_SAMPLES_CAPACITY];
    size_t head;
    size_t count;
    pthread_mutex_t lock;
} telemetry_ring_buffer_t;

typedef struct {
    uint32_t node_id;
    uint32_t major_version;
    bool is_canary;
    bool is_healthy;
    bool is_draining;
    uint32_t active_connections;
} cluster_node_t;

typedef struct {
    rollout_state_t current_state;
    double current_weight_percent;
    uint64_t active_epoch_token;
    time_t state_entered_timestamp;
    
    cluster_node_t nodes[MAX_TARGET_NODES];
    size_t node_count;
    
    telemetry_ring_buffer_t baseline_telemetry;
    telemetry_ring_buffer_t canary_telemetry;
    
    pthread_rwlock_t state_rwlock;
    double alpha_threshold;
    double critical_z_score;
} canary_rollout_controller_t;

/* Допоміжна структура для статистичного ранжування */
typedef struct {
    double value;
    int is_canary;
    double assigned_rank;
} ranked_sample_t;

/* Ініціалізація кільцевого буфера телеметрії */
void ring_buffer_init(telemetry_ring_buffer_t *rb) {
    if (!rb) return;
    rb->head = 0;
    rb->count = 0;
    pthread_mutex_init(&rb->lock, NULL);
}

void ring_buffer_destroy(telemetry_ring_buffer_t *rb) {
    if (rb) {
        pthread_mutex_destroy(&rb->lock);
    }
}

/* Додавання вимірювання затримки у буфер */
void ring_buffer_push(telemetry_ring_buffer_t *rb, double latency_ms) {
    if (!rb) return;
    pthread_mutex_lock(&rb->lock);
    rb->latency_samples[rb->head] = latency_ms;
    rb->head = (rb->head + 1) % MAX_SAMPLES_CAPACITY;
    if (rb->count < MAX_SAMPLES_CAPACITY) {
        rb->count++;
    }
    pthread_mutex_unlock(&rb->lock);
}

/* Очищення накопичених зразків буфера */
void ring_buffer_clear(telemetry_ring_buffer_t *rb) {
    if (!rb) return;
    pthread_mutex_lock(&rb->lock);
    rb->head = 0;
    rb->count = 0;
    pthread_mutex_unlock(&rb->lock);
}

/* Копіювання зразків для безпечного статистичного аналізу */
size_t ring_buffer_snapshot(telemetry_ring_buffer_t *rb, double *dst, size_t max_out) {
    if (!rb || !dst || max_out == 0) return 0;
    pthread_mutex_lock(&rb->lock);
    size_t to_copy = (rb->count < max_out) ? rb->count : max_out;
    for (size_t i = 0; i < to_copy; ++i) {
        size_t idx = (rb->head + MAX_SAMPLES_CAPACITY - rb->count + i) % MAX_SAMPLES_CAPACITY;
        dst[i] = rb->latency_samples[idx];
    }
    pthread_mutex_unlock(&rb->lock);
    return to_copy;
}

/* Функція порівняння для швидкого сортування qsort */
static int compare_ranked_samples(const void *a, const void *b) {
    const ranked_sample_t *sa = (const ranked_sample_t *)a;
    const ranked_sample_t *sb = (const ranked_sample_t *)b;
    if (sa->value < sb->value) return -1;
    if (sa->value > sb->value) return 1;
    return 0;
}

/* Обчислення U-критерію Манна-Вітні */
bool run_mann_whitney_analysis(const double *base, size_t n,
                               const double *canary, size_t m,
                               double *out_z, double *out_p) {
    if (!base || !canary || n == 0 || m == 0 || !out_z || !out_p) return false;

    size_t total = n + m;
    ranked_sample_t *arr = (ranked_sample_t *)malloc(total * sizeof(ranked_sample_t));
    if (!arr) return false;

    for (size_t i = 0; i < n; ++i) {
        arr[i].value = base[i];
        arr[i].is_canary = 0;
        arr[i].assigned_rank = 0.0;
    }
    for (size_t j = 0; j < m; ++j) {
        arr[n + j].value = canary[j];
        arr[n + j].is_canary = 1;
        arr[n + j].assigned_rank = 0.0;
    }

    qsort(arr, total, sizeof(ranked_sample_t), compare_ranked_samples);

    /* Обчислення рангів із корекцією зв'язок */
    size_t i = 0;
    while (i < total) {
        size_t j = i;
        while (j + 1 < total && arr[j + 1].value == arr[i].value) {
            j++;
        }
        double rank = 1.0 + (double)(i + j) / 2.0;
        for (size_t k = i; k <= j; ++k) {
            arr[k].assigned_rank = rank;
        }
        i = j + 1;
    }

    double r_base = 0.0;
    for (size_t k = 0; k < total; ++k) {
        if (arr[k].is_canary == 0) {
            r_base += arr[k].assigned_rank;
        }
    }

    double dn = (double)n;
    double dm = (double)m;
    double u1 = dn * dm + (dn * (dn + 1.0)) / 2.0 - r_base;
    double u2 = dn * dm - u1;
    double u_stat = (u1 < u2) ? u1 : u2;

    double mu_u = (dn * dm) / 2.0;
    double sigma_u = sqrt((dn * dm * (dn + dm + 1.0)) / 12.0);

    if (sigma_u > 1e-6) {
        *out_z = (u_stat - mu_u) / sigma_u;
    } else {
        *out_z = 0.0;
    }

    *out_p = erfc(fabs(*out_z) / sqrt(2.0));

    free(arr);
    return true;
}

/* Ініціалізація головного диспетчера канаркових релізів */
bool canary_controller_init(canary_rollout_controller_t *ctrl, double critical_z) {
    if (!ctrl) return false;
    memset(ctrl, 0, sizeof(*ctrl));
    ctrl->current_state = STAGE_IDLE;
    ctrl->current_weight_percent = 0.0;
    ctrl->active_epoch_token = 1000;
    ctrl->state_entered_timestamp = time(NULL);
    ctrl->alpha_threshold = 0.01;
    ctrl->critical_z_score = (critical_z < 0.0) ? -2.58 : -fabs(critical_z);

    ring_buffer_init(&ctrl->baseline_telemetry);
    ring_buffer_init(&ctrl->canary_telemetry);

    return (pthread_rwlock_init(&ctrl->state_rwlock, NULL) == 0);
}

void canary_controller_destroy(canary_rollout_controller_t *ctrl) {
    if (!ctrl) return;
    ring_buffer_destroy(&ctrl->baseline_telemetry);
    ring_buffer_destroy(&ctrl->canary_telemetry);
    pthread_rwlock_destroy(&ctrl->state_rwlock);
}

/* Додавання цільового серверного вузла у топологію контролера */
bool canary_controller_register_node(canary_rollout_controller_t *ctrl,
                                     uint32_t node_id,
                                     uint32_t major_version,
                                     bool is_canary) {
    if (!ctrl) return false;
    pthread_rwlock_wrlock(&ctrl->state_rwlock);
    if (ctrl->node_count >= MAX_TARGET_NODES) {
        pthread_rwlock_unlock(&ctrl->state_rwlock);
        return false;
    }
    cluster_node_t *n = &ctrl->nodes[ctrl->node_count++];
    n->node_id = node_id;
    n->major_version = major_version;
    n->is_canary = is_canary;
    n->is_healthy = true;
    n->is_draining = false;
    n->active_connections = 0;
    pthread_rwlock_unlock(&ctrl->state_rwlock);
    return true;
}

/* Маршрутизація вхідного запиту на основі хешу користувача */
int32_t canary_controller_route_request(canary_rollout_controller_t *ctrl, uint32_t user_hash) {
    if (!ctrl) return -1;
    pthread_rwlock_rdlock(&ctrl->state_rwlock);

    /* Швидка перевірка стану екстреної зупинки */
    if (ctrl->current_state == STAGE_EMERGENCY_KILL_SWITCH ||
        ctrl->current_state == STAGE_QUARANTINE_DRAINING ||
        ctrl->current_state == STAGE_ROLLED_BACK) {
        /* Трафік суворо на вузли v1 */
        for (size_t i = 0; i < ctrl->node_count; ++i) {
            if (!ctrl->nodes[i].is_canary && ctrl->nodes[i].is_healthy && !ctrl->nodes[i].is_draining) {
                int32_t id = (int32_t)ctrl->nodes[i].node_id;
                pthread_rwlock_unlock(&ctrl->state_rwlock);
                return id;
            }
        }
        pthread_rwlock_unlock(&ctrl->state_rwlock);
        return -1;
    }

    double bucket = (double)(user_hash % 10000) / 100.0;
    bool select_canary = (bucket < ctrl->current_weight_percent);

    int32_t selected_node = -1;
    for (size_t i = 0; i < ctrl->node_count; ++i) {
        if (ctrl->nodes[i].is_canary == select_canary &&
            ctrl->nodes[i].is_healthy &&
            !ctrl->nodes[i].is_draining) {
            selected_node = (int32_t)ctrl->nodes[i].node_id;
            break;
        }
    }

    pthread_rwlock_unlock(&ctrl->state_rwlock);
    return selected_node;
}

/* Активація аварійного Kill Switch за O(1) */
void canary_controller_trigger_kill_switch(canary_rollout_controller_t *ctrl, const char *reason) {
    if (!ctrl) return;
    pthread_rwlock_wrlock(&ctrl->state_rwlock);

    ctrl->current_state = STAGE_EMERGENCY_KILL_SWITCH;
    ctrl->current_weight_percent = 0.0;
    ctrl->active_epoch_token++;
    ctrl->state_entered_timestamp = time(NULL);

    /* Переведення всіх канаркових вузлів у режим дренажу */
    for (size_t i = 0; i < ctrl->node_count; ++i) {
        if (ctrl->nodes[i].is_canary) {
            ctrl->nodes[i].is_draining = true;
        }
    }

    printf("[KILL_SWITCH] Аварійна зупинка активована. Причина: %s. Нова епоха: %llu\n",
           reason ? reason : "Невідома аномалія",
           (unsigned long long)ctrl->active_epoch_token);

    pthread_rwlock_unlock(&ctrl->state_rwlock);
}

/* Виконання регулярного кроку оцінки та просування когорт */
void canary_controller_tick(canary_rollout_controller_t *ctrl) {
    if (!ctrl) return;
    pthread_rwlock_wrlock(&ctrl->state_rwlock);
    time_t now = time(NULL);

    switch (ctrl->current_state) {
        case STAGE_IDLE:
            break;

        case STAGE_INITIALIZING:
            ctrl->current_state = STAGE_PROMOTING_COHORT;
            ctrl->current_weight_percent = 1.0; /* Перша канарка: 1% */
            ctrl->state_entered_timestamp = now;
            ring_buffer_clear(&ctrl->baseline_telemetry);
            ring_buffer_clear(&ctrl->canary_telemetry);
            printf("[ROLLOUT] Ініціалізація завершена. Встановлено канаркову вагу 1%%\n");
            break;

        case STAGE_PROMOTING_COHORT:
            ctrl->current_state = STAGE_SOAKING;
            ctrl->state_entered_timestamp = now;
            printf("[ROLLOUT] Перехід у режим вистоювання (Soaking). Вага: %.1f%%\n", ctrl->current_weight_percent);
            break;

        case STAGE_SOAKING:
            /* Період вистоювання: для тесту 5 секунд */
            if (difftime(now, ctrl->state_entered_timestamp) >= 5.0) {
                ctrl->current_state = STAGE_EVALUATING_ACA;
                ctrl->state_entered_timestamp = now;
            }
            break;

        case STAGE_EVALUATING_ACA: {
            double base_snap[MAX_SAMPLES_CAPACITY];
            double can_snap[MAX_SAMPLES_CAPACITY];
            size_t n = ring_buffer_snapshot(&ctrl->baseline_telemetry, base_snap, MAX_SAMPLES_CAPACITY);
            size_t m = ring_buffer_snapshot(&ctrl->canary_telemetry, can_snap, MAX_SAMPLES_CAPACITY);

            if (n >= 10 && m >= 10) {
                double z_stat = 0.0, p_val = 1.0;
                if (run_mann_whitney_analysis(base_snap, n, can_snap, m, &z_stat, &p_val)) {
                    printf("[ACA_EVAL] Вибірки: n=%zu, m=%zu. Z-score: %.3f, p-value: %.5f\n", n, m, z_stat, p_val);

                    if (z_stat < ctrl->critical_z_score && p_val < ctrl->alpha_threshold) {
                        /* Статистично значуща деградація затримки */
                        pthread_rwlock_unlock(&ctrl->state_rwlock);
                        canary_controller_trigger_kill_switch(ctrl, "Статистична деградація p99 затримки (ACA Mann-Whitney)");
                        return;
                    }
                }
            }

            /* Метрики в нормі: просування когорти */
            if (ctrl->current_weight_percent >= 50.0) {
                ctrl->current_weight_percent = 100.0;
                ctrl->current_state = STAGE_PROMOTED_FULL;
                printf("[ROLLOUT] Реліз успішно розгорнуто на 100%% парку!\n");
            } else if (ctrl->current_weight_percent >= 25.0) {
                ctrl->current_weight_percent = 50.0;
                ctrl->current_state = STAGE_PROMOTING_COHORT;
            } else if (ctrl->current_weight_percent >= 5.0) {
                ctrl->current_weight_percent = 25.0;
                ctrl->current_state = STAGE_PROMOTING_COHORT;
            } else {
                ctrl->current_weight_percent = 5.0;
                ctrl->current_state = STAGE_PROMOTING_COHORT;
            }
            ctrl->state_entered_timestamp = now;
            ring_buffer_clear(&ctrl->baseline_telemetry);
            ring_buffer_clear(&ctrl->canary_telemetry);
            break;
        }

        case STAGE_EMERGENCY_KILL_SWITCH:
            ctrl->current_state = STAGE_QUARANTINE_DRAINING;
            ctrl->state_entered_timestamp = now;
            printf("[DRAIN] Початок фази дренажу канаркових сокетів (GOAWAY кадр надіслано)\n");
            break;

        case STAGE_QUARANTINE_DRAINING:
            if (difftime(now, ctrl->state_entered_timestamp) >= 3.0) {
                ctrl->current_state = STAGE_ROLLED_BACK;
                ctrl->state_entered_timestamp = now;
                printf("[QUARANTINE] Дренаж завершено. Канаркові вузли ізольовано у карантинному контурі.\n");
            }
            break;

        case STAGE_ROLLED_BACK:
        case STAGE_PROMOTED_FULL:
            break;
    }

    pthread_rwlock_unlock(&ctrl->state_rwlock);
}
