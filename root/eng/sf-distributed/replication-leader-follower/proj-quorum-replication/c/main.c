#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define CLUSTER_SIZE 5
#define MAX_KEY_LEN 32
#define MAX_VAL_LEN 64

typedef enum {
    STATUS_OK = 0,
    STATUS_TIMEOUT = 1,
    STATUS_QUORUM_FAILED = 2,
    STATUS_NOT_FOUND = 3
} StatusCode;

/* Структура запису з версією */
typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    uint64_t version;
    bool exists;
} Record;

/* Вузол сховища */
typedef struct {
    int node_id;
    Record data;
    double failure_rate; /* Імовірність відмови вузла [0.0 .. 1.0] */
} StorageNode;

/* Результат операції читання з одного вузла */
typedef struct {
    int node_id;
    Record record;
    StatusCode status;
} NodeResponse;

/* Ініціалізація кластера */
void cluster_init(StorageNode cluster[CLUSTER_SIZE]) {
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        cluster[i].node_id = i;
        cluster[i].data.exists = false;
        cluster[i].data.version = 0;
        cluster[i].failure_rate = (i == 3) ? 0.40 : 0.05; /* Вузол 3 має вищий рівень збоїв */
    }
}

/* Симуляція прямого запису на один вузол */
StatusCode node_write(StorageNode* node, const char* key, const char* value, uint64_t version) {
    double r = (double)rand() / RAND_MAX;
    if (r < node->failure_rate) {
        return STATUS_TIMEOUT; /* Імітація збою мережі або таймауту */
    }
    
    /* Запис приймається, якщо нова версія суворо більша або рівна */
    if (!node->data.exists || version >= node->data.version) {
        strncpy(node->data.key, key, MAX_KEY_LEN - 1);
        strncpy(node->data.value, value, MAX_VAL_LEN - 1);
        node->data.key[MAX_KEY_LEN - 1] = '\0';
        node->data.value[MAX_VAL_LEN - 1] = '\0';
        node->data.version = version;
        node->data.exists = true;
        return STATUS_OK;
    }
    return STATUS_OK;
}

/* Симуляція прямого читання з одного вузла */
NodeResponse node_read(StorageNode* node, const char* key) {
    NodeResponse resp;
    resp.node_id = node->node_id;
    resp.status = STATUS_OK;
    
    double r = (double)rand() / RAND_MAX;
    if (r < node->failure_rate) {
        resp.status = STATUS_TIMEOUT;
        return resp;
    }
    
    if (!node->data.exists || strcmp(node->data.key, key) != 0) {
        resp.status = STATUS_NOT_FOUND;
        return resp;
    }
    
    resp.record = node->data;
    return resp;
}

/* Координатор: виконання запису з кворумом W */
StatusCode coordinator_write(StorageNode cluster[CLUSTER_SIZE], const char* key, 
                              const char* value, uint64_t version, int w_quorum) {
    int successful_acks = 0;
    
    printf("[Coordinator] Початок запису key='%s', val='%s', ver=%llu (потрібно W=%d acks)...\n",
           key, value, (unsigned long long)version, w_quorum);
    
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        StatusCode res = node_write(&cluster[i], key, value, version);
        if (res == STATUS_OK) {
            successful_acks++;
            printf("  -> Вузол %d: Запис OK\n", i);
        } else {
            printf("  -> Вузол %d: Помилка/Таймаут\n", i);
        }
    }
    
    if (successful_acks >= w_quorum) {
        printf("[Coordinator] Запис успішний: зібрано %d acks з W=%d\n\n", successful_acks, w_quorum);
        return STATUS_OK;
    }
    
    printf("[Coordinator] ПОМИЛКА КВОРУМУ: зібрано лише %d acks з W=%d\n\n", successful_acks, w_quorum);
    return STATUS_QUORUM_FAILED;
}

/* Координатор: виконання читання з кворумом R та запуском Read Repair */
StatusCode coordinator_read(StorageNode cluster[CLUSTER_SIZE], const char* key, 
                             int r_quorum, Record* out_record) {
    NodeResponse responses[CLUSTER_SIZE];
    int successful_reads = 0;
    
    printf("[Coordinator] Початок читання key='%s' (потрібно R=%d відповідей)...\n", key, r_quorum);
    
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        responses[i] = node_read(&cluster[i], key);
        if (responses[i].status == STATUS_OK) {
            successful_reads++;
            printf("  <- Вузол %d відповів: val='%s', ver=%llu\n", 
                   i, responses[i].record.value, (unsigned long long)responses[i].record.version);
        } else {
            printf("  <- Вузол %d: недоступний або не знайдено\n", i);
        }
    }
    
    if (successful_reads < r_quorum) {
        printf("[Coordinator] ПОМИЛКА КВОРУМУ ЧИТАННЯ: зібрано лише %d відповідей з R=%d\n\n",
               successful_reads, r_quorum);
        return STATUS_QUORUM_FAILED;
    }
    
    /* Знаходимо найновішу версію серед опитаних вузлів */
    uint64_t max_version = 0;
    int latest_idx = -1;
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        if (responses[i].status == STATUS_OK) {
            if (responses[i].record.version >= max_version) {
                max_version = responses[i].record.version;
                latest_idx = i;
            }
        }
    }
    
    if (latest_idx == -1) {
        return STATUS_NOT_FOUND;
    }
    
    *out_record = responses[latest_idx].record;
    printf("[Coordinator] Обрано свіжу версію: val='%s' (ver=%llu)\n", 
           out_record->value, (unsigned long long)out_record->version);
    
    /* Асинхронний Read Repair: виявляємо застарілі вузли та оновлюємо їх */
    printf("[Coordinator] Перевірка необхідності Read Repair:\n");
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        if (responses[i].status == STATUS_OK) {
            if (responses[i].record.version < max_version) {
                printf("  -> [Read Repair] Вузол %d має застарілу версію %llu! Оновлюємо до %llu...\n",
                       i, (unsigned long long)responses[i].record.version, (unsigned long long)max_version);
                node_write(&cluster[i], out_record->key, out_record->value, out_record->version);
            }
        }
    }
    printf("[Coordinator] Читання завершено успішно.\n\n");
    return STATUS_OK;
}

int main(void) {
    srand((unsigned int)time(NULL));
    StorageNode cluster[CLUSTER_SIZE];
    cluster_init(cluster);
    
    /* Крок 1: Запис з кворумом W=3 на N=5 */
    coordinator_write(cluster, "account:42", "balance:100", 1, 3);
    
    /* Крок 2: Штучно застаріваємо Вузол 1 (імітація пропущеного оновлення) */
    cluster[1].data.version = 0;
    strcpy(cluster[1].data.value, "balance:0");
    
    /* Крок 3: Читання з кворумом R=3 — виявлення розходження та Read Repair */
    Record result;
    StatusCode status = coordinator_read(cluster, "account:42", 3, &result);
    
    if (status == STATUS_OK) {
        printf("Клієнт отримав фінальний результат: %s (версія %llu)\n", 
               result.value, (unsigned long long)result.version);
    }
    return 0;
}
