#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ENTRIES 64
#define MAX_KEY_LEN 32
#define MAX_VAL_LEN 64

/* Коди результатів виконання операцій */
typedef enum {
    STORAGE_OK = 0,
    STORAGE_ERR_STALE_EPOCH = -1,
    STORAGE_ERR_FULL = -2,
    STORAGE_ERR_NOT_FOUND = -3
} storage_status_t;

/* Запис у сховищі ключ-значення */
typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    uint64_t last_modified_epoch;
    bool active;
} storage_entry_t;

/* Стан сервера сховища даних */
typedef struct {
    uint64_t max_accepted_epoch;
    storage_entry_t entries[MAX_ENTRIES];
    size_t count;
} storage_server_t;

/* Запит на запис від клієнта-лідера */
typedef struct {
    uint64_t epoch;
    const char *key;
    const char *value;
} write_request_t;

/* Відповідь сервера сховища */
typedef struct {
    storage_status_t status;
    uint64_t current_storage_epoch;
    const char *message;
} write_response_t;

/* Ініціалізація сервера сховища */
void storage_init(storage_server_t *server) {
    server->max_accepted_epoch = 0;
    server->count = 0;
    for (size_t i = 0; i < MAX_ENTRIES; i++) {
        server->entries[i].active = false;
    }
}

/* Атомарна обробка запиту на запис із перевіркою токена фенсингу */
write_response_t storage_write(storage_server_t *server, const write_request_t *req) {
    write_response_t res;
    
    /* Головна перевірка фенсингу: відхиляємо старі епохи */
    if (req->epoch < server->max_accepted_epoch) {
        res.status = STORAGE_ERR_STALE_EPOCH;
        res.current_storage_epoch = server->max_accepted_epoch;
        res.message = "REJECTED: Stale fencing token (epoch expired)";
        return res;
    }

    /* Оновлюємо найбільшу бачену епоху сховища */
    server->max_accepted_epoch = req->epoch;

    /* Пошук наявного ключа */
    for (size_t i = 0; i < MAX_ENTRIES; i++) {
        if (server->entries[i].active && strcmp(server->entries[i].key, req->key) == 0) {
            strncpy(server->entries[i].value, req->value, MAX_VAL_LEN - 1);
            server->entries[i].value[MAX_VAL_LEN - 1] = '\0';
            server->entries[i].last_modified_epoch = req->epoch;

            res.status = STORAGE_OK;
            res.current_storage_epoch = server->max_accepted_epoch;
            res.message = "SUCCESS: Key updated";
            return res;
        }
    }

    /* Додавання нового запису */
    for (size_t i = 0; i < MAX_ENTRIES; i++) {
        if (!server->entries[i].active) {
            strncpy(server->entries[i].key, req->key, MAX_KEY_LEN - 1);
            server->entries[i].key[MAX_KEY_LEN - 1] = '\0';
            strncpy(server->entries[i].value, req->value, MAX_VAL_LEN - 1);
            server->entries[i].value[MAX_VAL_LEN - 1] = '\0';
            server->entries[i].last_modified_epoch = req->epoch;
            server->entries[i].active = true;
            server->count++;

            res.status = STORAGE_OK;
            res.current_storage_epoch = server->max_accepted_epoch;
            res.message = "SUCCESS: Key inserted";
            return res;
        }
    }

    res.status = STORAGE_ERR_FULL;
    res.current_storage_epoch = server->max_accepted_epoch;
    res.message = "ERROR: Storage table full";
    return res;
}

/* Читання поточного значення зі сховища */
storage_status_t storage_read(const storage_server_t *server, const char *key, char *out_val, size_t max_len) {
    for (size_t i = 0; i < MAX_ENTRIES; i++) {
        if (server->entries[i].active && strcmp(server->entries[i].key, key) == 0) {
            strncpy(out_val, server->entries[i].value, max_len - 1);
            out_val[max_len - 1] = '\0';
            return STORAGE_OK;
        }
    }
    return STORAGE_ERR_NOT_FOUND;
}

/* Координатор кластера (емуляція Raft / etcd) */
typedef struct {
    uint64_t current_epoch;
    const char *current_leader_name;
} cluster_coordinator_t;

void coordinator_init(cluster_coordinator_t *coord) {
    coord->current_epoch = 0;
    coord->current_leader_name = "None";
}

/* Обрання нового лідера з монотонним збільшенням номера епохи */
uint64_t coordinator_elect_leader(cluster_coordinator_t *coord, const char *new_leader_name) {
    coord->current_epoch++;
    coord->current_leader_name = new_leader_name;
    printf("[COORDINATOR] Elected new leader '%s' with Fencing Token (Epoch) = %llu\n",
           coord->current_leader_name, (unsigned long long)coord->current_epoch);
    return coord->current_epoch;
}

int main(void) {
    printf("=== СИМУЛЯЦІЯ ЗАХИСТУ ВІД SPLIT-BRAIN ЧЕРЕЗ FENCING TOKENS ===\n\n");

    storage_server_t storage;
    storage_init(&storage);

    cluster_coordinator_t coordinator;
    coordinator_init(&coordinator);

    /* 1. Початкові вибори: Вузол 1 стає лідером */
    uint64_t leader1_token = coordinator_elect_leader(&coordinator, "Node-1");

    /* 2. Вузол 1 успішно записує дані на рахунок */
    write_request_t req1 = {
        .epoch = leader1_token,
        .key = "account:UA8842",
        .value = "balance:1000_UAH"
    };

    printf("[LEADER 1] Sending write: key='%s', val='%s', epoch=%llu\n",
           req1.key, req1.value, (unsigned long long)req1.epoch);
    write_response_t resp1 = storage_write(&storage, &req1);
    printf("[STORAGE] Status: %d, ServerEpoch: %llu, Msg: %s\n\n",
           resp1.status, (unsigned long long)resp1.current_storage_epoch, resp1.message);

    /* 3. Симуляція зависання Вузла 1 (GC Pause / мережевий обрив) */
    printf(">>> [ALARM] Node-1 frozen on GC pause (Stop-The-World)! Heartbeat lost.\n");

    /* 4. Координатор фіксує таймаут і обирає Вузол 2 новим лідером */
    uint64_t leader2_token = coordinator_elect_leader(&coordinator, "Node-2");

    /* 5. Вузол 2 записує нову транзакцію з новим токеном */
    write_request_t req2 = {
        .epoch = leader2_token,
        .key = "account:UA8842",
        .value = "balance:750_UAH"
    };

    printf("[LEADER 2] Sending write: key='%s', val='%s', epoch=%llu\n",
           req2.key, req2.value, (unsigned long long)req2.epoch);
    write_response_t resp2 = storage_write(&storage, &req2);
    printf("[STORAGE] Status: %d, ServerEpoch: %llu, Msg: %s\n\n",
           resp2.status, (unsigned long long)resp2.current_storage_epoch, resp2.message);

    /* 6. Вузол 1 прокидається після GC і намагається виконати старий запізнілий запис */
    printf(">>> [RESUME] Node-1 wakes up from GC! It still believes it is the leader.\n");
    write_request_t stale_req = {
        .epoch = leader1_token, /* Старий токен = 1 */
        .key = "account:UA8842",
        .value = "balance:500_UAH" /* Конфліктний запізнілий запис */
    };

    printf("[LEADER 1 (STALE)] Trying to write: key='%s', val='%s', epoch=%llu\n",
           stale_req.key, stale_req.value, (unsigned long long)stale_req.epoch);
    write_response_t stale_resp = storage_write(&storage, &stale_req);
    printf("[STORAGE] Status: %d, ServerEpoch: %llu, Msg: %s\n\n",
           stale_resp.status, (unsigned long long)stale_resp.current_storage_epoch, stale_resp.message);

    /* 7. Фінальна перевірка цілісності даних у сховищі */
    char final_val[MAX_VAL_LEN];
    storage_read(&storage, "account:UA8842", final_val, sizeof(final_val));
    printf("=== ПІДСУМОК: Фінальний стан у сховищі: '%s' ===\n", final_val);
    printf("Цілісність збережено: запізнілий запис відхилено завдяки фенсингу.\n");

    return 0;
}
