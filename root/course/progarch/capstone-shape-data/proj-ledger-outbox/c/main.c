/* C: Low-level Manual Transaction Handling & Outbox Pattern */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    char event_id[64];
    char aggregate_type[64];
    char aggregate_id[64];
    char event_type[64];
    char payload_json[512];
} outbox_event_t;

typedef struct {
    bool in_transaction;
} db_conn_t;

static bool db_execute(db_conn_t *conn, const char *sql) {
    printf("[C DB EXEC] %s\n", sql);
    return true;
}

int wallet_transfer_with_outbox(
    db_conn_t *conn,
    const char *sender_id,
    const char *receiver_id,
    long long amount_cents,
    const outbox_event_t *event
) {
    if (!conn) return -1;

    /* BEGIN TX */
    conn->in_transaction = true;
    printf("[C DB] BEGIN TRANSACTION;\n");

    /* 1. Deduct balance */
    char sql_buffer[1024];
    snprintf(sql_buffer, sizeof(sql_buffer),
             "UPDATE wallet_accounts SET balance_cents = balance_cents - %lld WHERE account_id = '%s'",
             amount_cents, sender_id);
    if (!db_execute(conn, sql_buffer)) {
        goto rollback;
    }

    /* 2. Credit balance */
    snprintf(sql_buffer, sizeof(sql_buffer),
             "UPDATE wallet_accounts SET balance_cents = balance_cents + %lld WHERE account_id = '%s'",
             amount_cents, receiver_id);
    if (!db_execute(conn, sql_buffer)) {
        goto rollback;
    }

    /* 3. Insert Outbox Event */
    snprintf(sql_buffer, sizeof(sql_buffer),
             "INSERT INTO outbox_events (event_id, aggregate_type, aggregate_id, event_type, payload_json) "
             "VALUES ('%s', '%s', '%s', '%s', '%s')",
             event->event_id, event->aggregate_type, event->aggregate_id,
             event->event_type, event->payload_json);
    if (!db_execute(conn, sql_buffer)) {
        goto rollback;
    }

    /* COMMIT */
    printf("[C DB] COMMIT;\n");
    conn->in_transaction = false;
    return 0;

rollback:
    printf("[C DB] ROLLBACK;\n");
    conn->in_transaction = false;
    return -1;
}
