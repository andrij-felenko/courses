#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

// Приклад ідіоматичного керування транзакцією на мові C
typedef struct {
    int id;
    int64_t balance;
} Account;

typedef struct {
    bool in_transaction;
} DbConnection;

bool db_begin(DbConnection *conn) {
    conn->in_transaction = true;
    return true;
}

bool db_commit(DbConnection *conn) {
    conn->in_transaction = false;
    return true;
}

bool db_rollback(DbConnection *conn) {
    conn->in_transaction = false;
    return true;
}

bool transfer_money(DbConnection *conn, Account *from, Account *to, int64_t amount) {
    if (!db_begin(conn)) return false;

    if (from->balance < amount) {
        // Порушення бізнес-інваріанта: відкат і вихід
        db_rollback(conn);
        return false;
    }

    from->balance -= amount;
    to->balance += amount;

    if (!db_commit(conn)) {
        db_rollback(conn);
        return false;
    }

    return true;
}
