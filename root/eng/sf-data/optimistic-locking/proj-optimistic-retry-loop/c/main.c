#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>

/* Структура банківського рахунку */
typedef struct {
    uint64_t account_id;
    int64_t balance_cents;
    uint64_t version;
} AccountRecord;

/* Коди результатів транзакції */
typedef enum {
    TX_SUCCESS = 0,
    TX_INSUFFICIENT_FUNDS = 1,
    TX_CONCURRENCY_CONFLICT = 2,
    TX_MAX_RETRIES_EXCEEDED = 3,
    TX_DB_ERROR = 4
} TxResult;

/* Конфігурація політики повторних спроб */
typedef struct {
    uint32_t max_retries;
    uint64_t base_delay_ms;
    uint64_t max_delay_ms;
} RetryPolicy;

/* Імітація сховища бази даних */
typedef struct {
    AccountRecord record;
    uint64_t update_attempts;
} MockDatabase;

/* Ініціалізація тестової бази даних */
void db_init(MockDatabase *db, uint64_t id, int64_t initial_balance) {
    db->record.account_id = id;
    db->record.balance_cents = initial_balance;
    db->record.version = 1;
    db->update_attempts = 0;
}

/* Читання запису: SELECT balance, version FROM accounts WHERE id = ? */
bool db_read_account(MockDatabase *db, uint64_t id, AccountRecord *out_record) {
    if (db->record.account_id != id) return false;
    *out_record = db->record;
    return true;
}

/* Атомарний CAS UPDATE:
   UPDATE accounts SET balance = ?, version = version + 1
   WHERE id = ? AND version = ? */
bool db_update_account_cas(MockDatabase *db, uint64_t id, int64_t new_balance, uint64_t expected_version) {
    db->update_attempts++;
    if (db->record.account_id != id) return false;
    
    // Перевірка предикату версії
    if (db->record.version != expected_version) {
        return false; // affected_rows = 0 (Колізія!)
    }

    // Атомарна фіксація
    db->record.balance_cents = new_balance;
    db->record.version++;
    return true; // affected_rows = 1 (Успіх)
}

/* Пауза з мікросекундною точністю та обробкою переривань EINTR */
static void sleep_ms(uint64_t ms) {
    struct timespec req, rem;
    req.tv_sec = (time_t)(ms / 1000);
    req.tv_nsec = (long)((ms % 1000) * 1000000L);
    while (nanosleep(&req, &rem) == -1 && errno == EINTR) {
        req = rem; // Досипаємо залишок часу, якщо потік був перерваний сигналом
    }
}

/* Обчислення паузи за алгоритмом Full Jitter */
static uint64_t calculate_backoff_ms(const RetryPolicy *policy, uint32_t attempt) {
    uint64_t multiplier = 1ULL << (attempt > 30 ? 30 : attempt);
    uint64_t max_backoff = policy->base_delay_ms * multiplier;
    if (max_backoff > policy->max_delay_ms) {
        max_backoff = policy->max_delay_ms;
    }
    if (max_backoff == 0) return 0;
    return (uint64_t)(rand() % (max_backoff + 1));
}

/* Виконання бізнес-операції з оптимістичним retry-циклом */
TxResult withdraw_with_retry(MockDatabase *db, uint64_t account_id, int64_t amount_cents, const RetryPolicy *policy) {
    for (uint32_t attempt = 0; attempt <= policy->max_retries; ++attempt) {
        AccountRecord acc;
        if (!db_read_account(db, account_id, &acc)) {
            return TX_DB_ERROR;
        }

        // Перевірка інваріантів бізнес-логіки
        if (acc.balance_cents < amount_cents) {
            return TX_INSUFFICIENT_FUNDS; // Повторювати немає сенсу
        }

        int64_t new_balance = acc.balance_cents - amount_cents;
        uint64_t current_version = acc.version;

        // Спроба атомарної фіксації
        bool success = db_update_account_cas(db, account_id, new_balance, current_version);
        if (success) {
            return TX_SUCCESS;
        }

        // Колізія: якщо спроби не вичерпано — відступаємо з джитером
        if (attempt < policy->max_retries) {
            uint64_t delay_ms = calculate_backoff_ms(policy, attempt);
            sleep_ms(delay_ms);
        }
    }

    return TX_MAX_RETRIES_EXCEEDED;
}

int main(void) {
    srand((unsigned int)time(NULL));
    MockDatabase db;
    db_init(&db, 42, 100000); // Баланс 100000 центів, версія 1

    RetryPolicy policy = {
        .max_retries = 5,
        .base_delay_ms = 10,
        .max_delay_ms = 200
    };

    printf("Початковий баланс: %ld центів, версія: %lu\n", db.record.balance_cents, db.record.version);
    
    TxResult res = withdraw_with_retry(&db, 42, 25000, &policy);
    if (res == TX_SUCCESS) {
        printf("Списання успішне! Новий баланс: %ld центів, нова версія: %lu\n",
               db.record.balance_cents, db.record.version);
    } else {
        printf("Помилка виконання транзакції: код %d\n", res);
    }

    return 0;
}
