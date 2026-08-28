#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_POSTINGS_PER_TX 16
#define MAX_TRANSACTIONS 1024
#define MAX_POSTINGS 4096
#define MAX_ACCOUNTS 256
#define KEY_LEN 64

typedef enum {
    ACCOUNT_ASSET,
    ACCOUNT_LIABILITY,
    ACCOUNT_EQUITY,
    ACCOUNT_REVENUE,
    ACCOUNT_EXPENSE
} AccountType;

typedef struct {
    uint32_t id;
    char name[64];
    AccountType type;
} Account;

typedef struct {
    uint32_t id;
    uint32_t transaction_id;
    uint32_t account_id;
    int64_t amount; // Додатне: дебет/зарахування, від'ємне: кредит/списання
    uint64_t sequence;
} Posting;

typedef struct {
    uint32_t id;
    char idempotency_key[KEY_LEN];
    char description[128];
    uint32_t posting_count;
    Posting postings[MAX_POSTINGS_PER_TX];
} Transaction;

typedef struct {
    uint32_t account_id;
    uint64_t at_sequence;
    int64_t balance;
} BalanceSnapshot;

typedef struct {
    Account accounts[MAX_ACCOUNTS];
    uint32_t account_count;

    Posting postings[MAX_POSTINGS];
    uint32_t posting_count;

    Transaction transactions[MAX_TRANSACTIONS];
    uint32_t transaction_count;

    BalanceSnapshot snapshots[MAX_ACCOUNTS];
    uint32_t snapshot_count;

    uint64_t global_sequence;
} Ledger;

void ledger_init(Ledger *ledger) {
    memset(ledger, 0, sizeof(Ledger));
}

int ledger_add_account(Ledger *ledger, uint32_t id, const char *name, AccountType type) {
    if (ledger->account_count >= MAX_ACCOUNTS) return -1;
    for (uint32_t i = 0; i < ledger->account_count; i++) {
        if (ledger->accounts[i].id == id) return -2; // Дублікат ID
    }
    Account *acc = &ledger->accounts[ledger->account_count++];
    acc->id = id;
    strncpy(acc->name, name, sizeof(acc->name) - 1);
    acc->type = type;
    return 0;
}

// Пошук транзакції за ключем ідемпотентності
Transaction* ledger_find_by_key(Ledger *ledger, const char *key) {
    if (!key || strlen(key) == 0) return NULL;
    for (uint32_t i = 0; i < ledger->transaction_count; i++) {
        if (strncmp(ledger->transactions[i].idempotency_key, key, KEY_LEN) == 0) {
            return &ledger->transactions[i];
        }
    }
    return NULL;
}

// Запис транзакції з перевіркою нульової суми
int ledger_post_transaction(Ledger *ledger, const char *idempotency_key, 
                            const char *desc, const Posting *entries, uint32_t count) {
    if (count < 2 || count > MAX_POSTINGS_PER_TX) return -1;

    // 1. Перевірка ідемпотентності
    if (idempotency_key && strlen(idempotency_key) > 0) {
        if (ledger_find_by_key(ledger, idempotency_key) != NULL) {
            return 1; // Транзакцію вже проведено раніше (ідемпотентний пропуск)
        }
    }

    // 2. Перевірка інваріанта нульової суми: сума всіх amount повинна дорівнювати 0
    int64_t sum = 0;
    for (uint32_t i = 0; i < count; i++) {
        sum += entries[i].amount;
    }
    if (sum != 0) {
        return -2; // Порушення балансу: сума не нуль
    }

    // 3. Перевірка існування всіх зазначених рахунків
    for (uint32_t i = 0; i < count; i++) {
        bool found = false;
        for (uint32_t a = 0; a < ledger->account_count; a++) {
            if (ledger->accounts[a].id == entries[i].account_id) {
                found = true;
                break;
            }
        }
        if (!found) return -3; // Рахунок не знайдено в плані рахунків
    }

    if (ledger->transaction_count >= MAX_TRANSACTIONS) return -4;
    if (ledger->posting_count + count > MAX_POSTINGS) return -5;

    // 4. Атомарний запис у незмінний журнал проводок
    uint32_t tx_id = ledger->transaction_count + 1;
    Transaction *tx = &ledger->transactions[ledger->transaction_count++];
    tx->id = tx_id;
    if (idempotency_key) strncpy(tx->idempotency_key, idempotency_key, KEY_LEN - 1);
    strncpy(tx->description, desc, sizeof(tx->description) - 1);
    tx->posting_count = count;

    for (uint32_t i = 0; i < count; i++) {
        ledger->global_sequence++;
        Posting *p = &ledger->postings[ledger->posting_count++];
        p->id = ledger->posting_count;
        p->transaction_id = tx_id;
        p->account_id = entries[i].account_id;
        p->amount = entries[i].amount;
        p->sequence = ledger->global_sequence;

        tx->postings[i] = *p;
    }

    return 0;
}

// Створення знімка для конкретного рахунку
int ledger_create_snapshot(Ledger *ledger, uint32_t account_id) {
    int64_t bal = 0;
    uint64_t max_seq = 0;
    for (uint32_t i = 0; i < ledger->posting_count; i++) {
        if (ledger->postings[i].account_id == account_id) {
            bal += ledger->postings[i].amount;
            if (ledger->postings[i].sequence > max_seq) {
                max_seq = ledger->postings[i].sequence;
            }
        }
    }
    // Оновлюємо наявний знімок або створюємо новий
    for (uint32_t i = 0; i < ledger->snapshot_count; i++) {
        if (ledger->snapshots[i].account_id == account_id) {
            ledger->snapshots[i].at_sequence = max_seq;
            ledger->snapshots[i].balance = bal;
            return 0;
        }
    }
    if (ledger->snapshot_count >= MAX_ACCOUNTS) return -1;
    BalanceSnapshot *s = &ledger->snapshots[ledger->snapshot_count++];
    s->account_id = account_id;
    s->at_sequence = max_seq;
    s->balance = bal;
    return 0;
}

// Отримання поточного балансу: Snapshot + Delta
int64_t ledger_get_balance(const Ledger *ledger, uint32_t account_id) {
    int64_t base_balance = 0;
    uint64_t after_seq = 0;

    // Перевіряємо наявність збереженого знімка
    for (uint32_t i = 0; i < ledger->snapshot_count; i++) {
        if (ledger->snapshots[i].account_id == account_id) {
            base_balance = ledger->snapshots[i].balance;
            after_seq = ledger->snapshots[i].at_sequence;
            break;
        }
    }

    // Підсумовуємо тільки нові проводки, що з'явилися після знімка
    int64_t delta = 0;
    for (uint32_t i = 0; i < ledger->posting_count; i++) {
        if (ledger->postings[i].account_id == account_id && 
            ledger->postings[i].sequence > after_seq) {
            delta += ledger->postings[i].amount;
        }
    }

    return base_balance + delta;
}

int main(void) {
    Ledger ledger;
    ledger_init(&ledger);

    // Створення плану рахунків
    ledger_add_account(&ledger, 101, "Bank_Account_UAH", ACCOUNT_ASSET);
    ledger_add_account(&ledger, 201, "Customer_Deposits", ACCOUNT_LIABILITY);
    ledger_add_account(&ledger, 401, "Processing_Fee_Income", ACCOUNT_REVENUE);

    printf("Ініціалізація рахунків завершена.\n");

    // Транзакція 1: Клієнт поповнює гаманець на 1000.00 грн (100000 копійок)
    // Банк отримує актив (+100000), у банку виникає зобов'язання перед клієнтом (-100000)
    Posting tx1_postings[2] = {
        { .account_id = 101, .amount = 100000 },
        { .account_id = 201, .amount = -100000 }
    };
    int res = ledger_post_transaction(&ledger, "DEP-001", "Поповнення гаманця", tx1_postings, 2);
    printf("Tx 1 статус: %d (0 = OK)\n", res);

    // Спроба повторного запису з тим самим ключем ідемпотентності
    int res_dup = ledger_post_transaction(&ledger, "DEP-001", "Повтор", tx1_postings, 2);
    printf("Tx 1 повторний виклик: %d (1 = Idempotent Skip)\n", res_dup);

    // Створюємо знімок для рахунку банку
    ledger_create_snapshot(&ledger, 101);

    // Транзакція 2: Списання комісії 20.00 грн
    Posting tx2_postings[2] = {
        { .account_id = 201, .amount = 2000 },
        { .account_id = 401, .amount = -2000 }
    };
    ledger_post_transaction(&ledger, "FEE-001", "Комісія за обслуговування", tx2_postings, 2);

    printf("Баланс банку (101): %ld коп.\n", (long)ledger_get_balance(&ledger, 101));
    printf("Баланс депозитів клієнтів (201): %ld коп.\n", (long)ledger_get_balance(&ledger, 201));
    printf("Баланс доходу з комісій (401): %ld коп.\n", (long)ledger_get_balance(&ledger, 401));

    return 0;
}
