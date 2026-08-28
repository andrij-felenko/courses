#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
static void sleep_ms(int ms) { Sleep(ms); }
#else
#include <unistd.h>
static void sleep_ms(int ms) { usleep(ms * 1000); }
#endif

typedef enum {
    TX_SUCCESS = 0,
    TX_SERIALIZATION_FAILURE = 1, // SQLSTATE 40001
    TX_DEADLOCK_DETECTED = 2,     // SQLSTATE 40P01
    TX_FATAL_ERROR = 3
} TxStatus;

typedef struct {
    int account_balance;
    bool doctor_alice_on_call;
    bool doctor_bob_on_call;
    uint64_t current_version;
} DatabaseState;

typedef struct {
    DatabaseState* db;
    uint64_t tx_id;
    uint64_t snapshot_version;
} TransactionContext;

typedef struct {
    int max_retries;
    int initial_backoff_ms;
    int max_backoff_ms;
} RetryPolicy;

static uint64_t g_next_tx_id = 1;

void tx_init_context(TransactionContext* ctx, DatabaseState* db) {
    ctx->db = db;
    ctx->tx_id = g_next_tx_id++;
    ctx->snapshot_version = db->current_version;
}

int tx_read_balance(const TransactionContext* ctx) {
    return ctx->db->account_balance;
}

TxStatus tx_update_balance(TransactionContext* ctx, int new_balance, bool simulate_conflict) {
    if (simulate_conflict) {
        return TX_SERIALIZATION_FAILURE;
    }
    ctx->db->account_balance = new_balance;
    return TX_SUCCESS;
}

typedef TxStatus (*TxOperationFunc)(TransactionContext* ctx, void* user_data);

TxStatus tx_runner_execute(DatabaseState* db, const RetryPolicy* policy, 
                          TxOperationFunc operation, void* user_data) {
    int current_backoff = policy->initial_backoff_ms;

    for (int attempt = 1; attempt <= policy->max_retries; ++attempt) {
        TransactionContext ctx;
        tx_init_context(&ctx, db);

        TxStatus status = operation(&ctx, user_data);

        if (status == TX_SUCCESS) {
            return TX_SUCCESS;
        }

        if (status == TX_SERIALIZATION_FAILURE || status == TX_DEADLOCK_DETECTED) {
            if (attempt == policy->max_retries) {
                return status;
            }

            // Обчислення рандомізованого джитеру
            int sleep_time = rand() % (current_backoff + 1);
            sleep_ms(sleep_time);

            // Подвоєння затримки
            current_backoff *= 2;
            if (current_backoff > policy->max_backoff_ms) {
                current_backoff = policy->max_backoff_ms;
            }
            continue;
        }

        return status;
    }

    return TX_SERIALIZATION_FAILURE;
}

static int g_attempt_counter = 0;

TxStatus sample_operation(TransactionContext* ctx, void* user_data) {
    (void)user_data;
    int current = tx_read_balance(ctx);
    bool conflict = (++g_attempt_counter % 2 == 1);

    printf("  -> [C] Транзакція #%llu: зчитано баланс = %d (конфлікт: %s)\n",
           (unsigned long long)ctx->tx_id, current, conflict ? "ТАК" : "НІ");

    return tx_update_balance(ctx, current + 100, conflict);
}

int main(void) {
    srand((unsigned int)time(NULL));

    DatabaseState db;
    db.account_balance = 1000;
    db.doctor_alice_on_call = true;
    db.doctor_bob_on_call = true;
    db.current_version = 1;

    RetryPolicy policy = {
        .max_retries = 5,
        .initial_backoff_ms = 20,
        .max_backoff_ms = 500
    };

    printf("[INFO C] Початковий баланс: %d грн\n", db.account_balance);

    TxStatus status = tx_runner_execute(&db, &policy, sample_operation, NULL);

    if (status == TX_SUCCESS) {
        printf("[SUCCESS C] Фіксація успішна! Залишок: %d грн\n", db.account_balance);
    } else {
        printf("[ERROR C] Транзакцію відхилено після вичерпання спроб (код %d)\n", status);
    }

    return 0;
}
