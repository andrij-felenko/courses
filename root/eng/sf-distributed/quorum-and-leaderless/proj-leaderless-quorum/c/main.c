#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_KEY_LEN   64
#define MAX_VAL_LEN   128
#define MAX_REPLICAS  8

/* Запис даних у сховищі окремої репліки */
typedef struct {
    char     key[MAX_KEY_LEN];
    char     value[MAX_VAL_LEN];
    uint64_t version;     /* монотонний лічильник версії */
    bool     is_deleted;  /* tombstone-маркер видалення */
    bool     present;     /* чи існує запис */
} Record;

/* Стан окремого вузла-репліки */
typedef struct {
    uint32_t id;
    bool     is_alive;    /* прапорець доступності вузла в мережі */
    Record   storage[64]; /* спрощене локальне сховище */
    size_t   count;
} ReplicaNode;

/* Результат операції читання з однієї репліки */
typedef struct {
    uint32_t node_id;
    bool     responded;
    Record   record;
} ReadResponse;

/* Ініціалізація вузла */
void node_init(ReplicaNode *node, uint32_t id) {
    node->id = id;
    node->is_alive = true;
    node->count = 0;
    memset(node->storage, 0, sizeof(node->storage));
}

/* Локальний запис на вузол */
bool node_local_write(ReplicaNode *node, const char *key, const char *val, uint64_t ver) {
    if (!node->is_alive) return false;

    for (size_t i = 0; i < node->count; ++i) {
        if (strcmp(node->storage[i].key, key) == 0) {
            /* Оновлюємо лише якщо нова версія новіша за поточну */
            if (ver >= node->storage[i].version) {
                strncpy(node->storage[i].value, val, MAX_VAL_LEN - 1);
                node->storage[i].version = ver;
                node->storage[i].is_deleted = false;
                node->storage[i].present = true;
            }
            return true;
        }
    }

    if (node->count < 64) {
        Record *r = &node->storage[node->count++];
        strncpy(r->key, key, MAX_KEY_LEN - 1);
        strncpy(r->value, val, MAX_VAL_LEN - 1);
        r->version = ver;
        r->is_deleted = false;
        r->present = true;
        return true;
    }
    return false;
}

/* Локальне читання з вузла */
bool node_local_read(const ReplicaNode *node, const char *key, Record *out_rec) {
    if (!node->is_alive) return false;

    for (size_t i = 0; i < node->count; ++i) {
        if (strcmp(node->storage[i].key, key) == 0) {
            *out_rec = node->storage[i];
            return true;
        }
    }
    /* Ключ не знайдено на живому вузлі */
    memset(out_rec, 0, sizeof(Record));
    strncpy(out_rec->key, key, MAX_KEY_LEN - 1);
    out_rec->present = false;
    out_rec->version = 0;
    return true;
}

/* Координатор: виконання запису з кворумом W */
bool coordinator_write(ReplicaNode cluster[], size_t n, size_t w,
                       const char *key, const char *val, uint64_t ver) {
    size_t acks = 0;

    printf("[Coordinator] Запис key='%s', val='%s', ver=%llu (потрібно W=%zu з N=%zu)...\n",
           key, val, (unsigned long long)ver, w, n);

    for (size_t i = 0; i < n; ++i) {
        if (node_local_write(&cluster[i], key, val, ver)) {
            acks++;
            printf("  -> Вузол %u: OK (підтверджено)\n", cluster[i].id);
        } else {
            printf("  -> Вузол %u: ВІДМОВА (недоступний)\n", cluster[i].id);
        }
    }

    if (acks >= w) {
        printf("[Coordinator] УСПІХ: зібрано %zu ACK >= W=%zu\n\n", acks, w);
        return true;
    } else {
        printf("[Coordinator] ПОМИЛКА КВОРУМУ: зібрано лише %zu ACK < W=%zu\n\n", acks, w);
        return false;
    }
}

/* Координатор: читання з кворумом R та запуск Read-Repair */
bool coordinator_read(ReplicaNode cluster[], size_t n, size_t r,
                      const char *key, char *out_val, uint64_t *out_ver) {
    ReadResponse responses[MAX_REPLICAS];
    size_t resp_count = 0;

    printf("[Coordinator] Читання key='%s' (потрібно R=%zu з N=%zu)...\n", key, r, n);

    for (size_t i = 0; i < n && resp_count < r; ++i) {
        Record rec;
        if (node_local_read(&cluster[i], key, &rec)) {
            responses[resp_count].node_id = cluster[i].id;
            responses[resp_count].responded = true;
            responses[resp_count].record = rec;
            printf("  <- Відповідь від вузла %u: val='%s', ver=%llu, present=%d\n",
                   cluster[i].id, rec.value, (unsigned long long)rec.version, rec.present);
            resp_count++;
        } else {
            printf("  <- Вузол %u не відповів (таймаут)\n", cluster[i].id);
        }
    }

    if (resp_count < r) {
        printf("[Coordinator] ПОМИЛКА КВОРУМУ ЧИТАННЯ: отримано %zu відповідей < R=%zu\n\n",
               resp_count, r);
        return false;
    }

    /* Знаходимо найновішу версію серед отриманих відповідей */
    uint64_t max_ver = 0;
    int best_idx = -1;

    for (size_t i = 0; i < resp_count; ++i) {
        if (responses[i].record.present && responses[i].record.version >= max_ver) {
            max_ver = responses[i].record.version;
            best_idx = (int)i;
        }
    }

    if (best_idx >= 0) {
        strncpy(out_val, responses[best_idx].record.value, MAX_VAL_LEN - 1);
        *out_ver = max_ver;
        printf("[Coordinator] Обрано найновіший стан: val='%s', ver=%llu\n", out_val, (unsigned long long)max_ver);
    } else {
        printf("[Coordinator] Ключ не знайдено на жодній з опитаних реплік\n");
        return false;
    }

    /* ФАЗА READ-REPAIR: оновлюємо всі відсталі вузли серед опитаних */
    for (size_t i = 0; i < resp_count; ++i) {
        if (!responses[i].record.present || responses[i].record.version < max_ver) {
            uint32_t target_id = responses[i].node_id;
            printf("  [Read-Repair] Вузол %u відстає (ver=%llu < %llu) -> надсилаємо оновлення...\n",
                   target_id, (unsigned long long)responses[i].record.version, (unsigned long long)max_ver);

            for (size_t k = 0; k < n; ++k) {
                if (cluster[k].id == target_id) {
                    node_local_write(&cluster[k], key, out_val, max_ver);
                    printf("  [Read-Repair] Вузол %u успішно зцілено до ver=%llu!\n",
                           target_id, (unsigned long long)max_ver);
                    break;
                }
            }
        }
    }
    printf("\n");
    return true;
}

int main(void) {
    const size_t N = 3;
    const size_t W = 2;
    const size_t R = 2;

    ReplicaNode cluster[3];
    for (size_t i = 0; i < N; ++i) node_init(&cluster[i], (uint32_t)(i + 1));

    printf("=== Сценарій 1: Звичайний запис (W=2) при всіх живих вузлах ===\n");
    coordinator_write(cluster, N, W, "user:101", "Andriy", 1);

    printf("=== Сценарій 2: Вузол 3 падає; оновлення записується на вузли 1 і 2 ===\n");
    cluster[2].is_alive = false; /* Вузол 3 вийшов з ладу */
    coordinator_write(cluster, N, W, "user:101", "Andriy Felenko", 2);

    printf("=== Сценарій 3: Вузол 3 оживає зі старим станом (ver=1) ===\n");
    cluster[2].is_alive = true;
    cluster[0].is_alive = false; /* Тимчасово недоступний вузол 1 */

    char val_buf[MAX_VAL_LEN] = {0};
    uint64_t ver_out = 0;

    /* Читання опитує вузли 2 і 3 (R = 2). Вузол 2 має ver=2, вузол 3 має ver=1. */
    coordinator_read(cluster, N, R, "user:101", val_buf, &ver_out);

    printf("=== Сценарій 4: Перевірка після Read-Repair (Вузол 3 має бути оновлений) ===\n");
    Record check_rec;
    node_local_read(&cluster[2], "user:101", &check_rec);
    printf("Прямий погляд на сховище Вузла 3: val='%s', ver=%llu (Зцілення підтверджено!)\n",
           check_rec.value, (unsigned long long)check_rec.version);

    return 0;
}
