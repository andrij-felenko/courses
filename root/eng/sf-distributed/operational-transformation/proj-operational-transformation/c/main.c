#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>

#define MAX_DOC_LEN 256
#define MAX_LOG_LEN 128

typedef enum {
    OP_INSERT,
    OP_DELETE,
    OP_NOOP
} OpType;

typedef struct {
    OpType type;
    int pos;
    char ch;
    int client_id;
} Operation;

/* Створення операцій */
Operation op_insert(int pos, char ch, int client_id) {
    Operation op;
    op.type = OP_INSERT;
    op.pos = pos;
    op.ch = ch;
    op.client_id = client_id;
    return op;
}

Operation op_delete(int pos, int client_id) {
    Operation op;
    op.type = OP_DELETE;
    op.pos = pos;
    op.ch = '\0';
    op.client_id = client_id;
    return op;
}

Operation op_noop(void) {
    Operation op;
    op.type = OP_NOOP;
    op.pos = 0;
    op.ch = '\0';
    op.client_id = 0;
    return op;
}

/* Застосування операції до рядкового буфера */
void doc_apply(char *doc, const Operation *op) {
    int len = (int)strlen(doc);
    if (op->type == OP_NOOP) {
        return;
    }
    if (op->type == OP_INSERT) {
        if (op->pos < 0 || op->pos > len || len + 1 >= MAX_DOC_LEN) return;
        memmove(doc + op->pos + 1, doc + op->pos, len - op->pos + 1);
        doc[op->pos] = op->ch;
    } else if (op->type == OP_DELETE) {
        if (op->pos < 0 || op->pos >= len) return;
        memmove(doc + op->pos, doc + op->pos + 1, len - op->pos);
    }
}

/* Попарна трансформація: Inclusion Transformation T(op1, op2) */
void transform_pair(const Operation *op1, const Operation *op2,
                    Operation *out1, Operation *out2) {
    *out1 = *op1;
    *out2 = *op2;

    if (op1->type == OP_NOOP || op2->type == OP_NOOP) {
        return;
    }

    if (op1->type == OP_INSERT && op2->type == OP_INSERT) {
        if (op1->pos < op2->pos || (op1->pos == op2->pos && op1->client_id < op2->client_id)) {
            out2->pos += 1;
        } else {
            out1->pos += 1;
        }
    } else if (op1->type == OP_INSERT && op2->type == OP_DELETE) {
        if (op1->pos <= op2->pos) {
            out2->pos += 1;
        } else {
            out1->pos -= 1;
        }
    } else if (op1->type == OP_DELETE && op2->type == OP_INSERT) {
        if (op1->pos < op2->pos) {
            out2->pos -= 1;
        } else {
            out1->pos += 1;
        }
    } else if (op1->type == OP_DELETE && op2->type == OP_DELETE) {
        if (op1->pos < op2->pos) {
            out2->pos -= 1;
        } else if (op1->pos > op2->pos) {
            out1->pos -= 1;
        } else {
            /* Обидва клієнти видалили один і той самий символ */
            *out1 = op_noop();
            *out2 = op_noop();
        }
    }
}

/* Трансформація одного op відносно іншого: T(op1, op2) */
Operation transform_single(const Operation *op1, const Operation *op2) {
    Operation o1, o2;
    transform_pair(op1, op2, &o1, &o2);
    return o1;
}

/* ── СЕРВЕР JUPITER ────────────────────────────────────────────────────────── */
typedef struct {
    char doc[MAX_DOC_LEN];
    Operation history[MAX_LOG_LEN];
    int revision;
} Server;

void server_init(Server *srv, const char *initial_text) {
    strncpy(srv->doc, initial_text, MAX_DOC_LEN - 1);
    srv->doc[MAX_DOC_LEN - 1] = '\0';
    srv->revision = 0;
}

/* Сервер приймає операцію від клієнта з його базовою ревізією */
Operation server_receive_op(Server *srv, Operation client_op, int client_rev) {
    Operation current_op = client_op;

    /* Трансформація проти всіх операцій, що лягли на сервері після client_rev */
    for (int r = client_rev; r < srv->revision; ++r) {
        current_op = transform_single(&current_op, &srv->history[r]);
    }

    /* Застосування до стану сервера */
    doc_apply(srv->doc, &current_op);

    /* Запис у лог ревізій */
    srv->history[srv->revision] = current_op;
    srv->revision++;

    return current_op;
}

/* ── КЛІЄНТ JUPITER ────────────────────────────────────────────────────────── */
typedef enum {
    STATE_SYNCHRONIZED,
    STATE_AWAITING_CONFIRM,
    STATE_AWAITING_CONFIRM_WITH_BUFFER
} ClientState;

typedef struct {
    int client_id;
    char doc[MAX_DOC_LEN];
    int server_revision;
    ClientState state;
    Operation in_flight;
    Operation buffer;
} Client;

void client_init(Client *cli, int client_id, const char *initial_text) {
    cli->client_id = client_id;
    strncpy(cli->doc, initial_text, MAX_DOC_LEN - 1);
    cli->doc[MAX_DOC_LEN - 1] = '\0';
    cli->server_revision = 0;
    cli->state = STATE_SYNCHRONIZED;
    cli->in_flight = op_noop();
    cli->buffer = op_noop();
}

/* Користувач натиснув клавішу (локальна дія) */
bool client_apply_local(Client *cli, Operation op, Operation *to_send) {
    doc_apply(cli->doc, &op);

    if (cli->state == STATE_SYNCHRONIZED) {
        cli->in_flight = op;
        cli->state = STATE_AWAITING_CONFIRM;
        *to_send = op;
        return true; /* Треба надіслати to_send на сервер */
    } else if (cli->state == STATE_AWAITING_CONFIRM) {
        cli->buffer = op;
        cli->state = STATE_AWAITING_CONFIRM_WITH_BUFFER;
        return false; /* Операція пішла в буфер */
    } else {
        /* Оновлення буфера (у навчальній моделі зберігаємо останню дію) */
        cli->buffer = op;
        return false;
    }
}

/* Клієнт отримав підтвердження своєї операції (ACK) від сервера */
bool client_receive_ack(Client *cli, Operation *to_send) {
    cli->server_revision++;

    if (cli->state == STATE_AWAITING_CONFIRM) {
        cli->state = STATE_SYNCHRONIZED;
        cli->in_flight = op_noop();
        return false;
    } else if (cli->state == STATE_AWAITING_CONFIRM_WITH_BUFFER) {
        cli->in_flight = cli->buffer;
        cli->buffer = op_noop();
        cli->state = STATE_AWAITING_CONFIRM;
        *to_send = cli->in_flight;
        return true; /* Відправляємо буферизовану правку */
    }
    return false;
}

/* Клієнт отримав правку іншого користувача від сервера */
void client_receive_remote_op(Client *cli, Operation srv_op) {
    cli->server_revision++;

    if (cli->state == STATE_SYNCHRONIZED) {
        doc_apply(cli->doc, &srv_op);
    } else if (cli->state == STATE_AWAITING_CONFIRM) {
        Operation srv_prime, in_flight_prime;
        transform_pair(&srv_op, &cli->in_flight, &srv_prime, &in_flight_prime);

        doc_apply(cli->doc, &srv_prime);
        cli->in_flight = in_flight_prime;
    } else if (cli->state == STATE_AWAITING_CONFIRM_WITH_BUFFER) {
        Operation srv_prime, in_flight_prime;
        transform_pair(&srv_op, &cli->in_flight, &srv_prime, &in_flight_prime);
        cli->in_flight = in_flight_prime;

        Operation srv_double_prime, buffer_prime;
        transform_pair(&srv_prime, &cli->buffer, &srv_double_prime, &buffer_prime);
        cli->buffer = buffer_prime;

        doc_apply(cli->doc, &srv_double_prime);
    }
}

/* Тестовий сценарій */
int main(void) {
    Server srv;
    Client cli_a, cli_b;

    server_init(&srv, "CAT");
    client_init(&cli_a, 1, "CAT");
    client_init(&cli_b, 2, "CAT");

    printf("Початковий стан документа: «%s»\n", srv.doc);

    /* 1. Клієнт A локально видаляє 'A' (позиція 1) */
    Operation send_a;
    client_apply_local(&cli_a, op_delete(1, 1), &send_a);
    int rev_a = cli_a.server_revision;

    /* 2. Клієнт B одночасно вставляє 'H' (позиція 0) */
    Operation send_b;
    client_apply_local(&cli_b, op_insert(0, 'H', 2), &send_b);
    int rev_b = cli_b.server_revision;

    printf("Після локальних правок: A = «%s», B = «%s»\n", cli_a.doc, cli_b.doc);

    /* 3. Сервер отримує операцію від A першим */
    Operation srv_a = server_receive_op(&srv, send_a, rev_a);
    printf("Сервер прийняв правку A -> ревізія %d, текст: «%s»\n", srv.revision, srv.doc);

    /* 4. Сервер отримує операцію від B з лагом (rev 0 при поточному rev 1) */
    Operation srv_b = server_receive_op(&srv, send_b, rev_b);
    printf("Сервер прийняв правку B -> ревізія %d, текст: «%s»\n", srv.revision, srv.doc);

    /* 5. Клієнт A отримує ACK для власної правки та трансляцію правки B */
    Operation next_op;
    client_receive_ack(&cli_a, &next_op);
    client_receive_remote_op(&cli_a, srv_b);

    /* 6. Клієнт B отримує трансляцію правки A (до свого ACK) і потім ACK */
    client_receive_remote_op(&cli_b, srv_a);
    client_receive_ack(&cli_b, &next_op);

    printf("\nФінальний результат синхронізації:\n");
    printf("  Сервер:   «%s»\n", srv.doc);
    printf("  Клієнт A: «%s»\n", cli_a.doc);
    printf("  Клієнт B: «%s»\n", cli_b.doc);

    assert(strcmp(srv.doc, "HCT") == 0);
    assert(strcmp(cli_a.doc, "HCT") == 0);
    assert(strcmp(cli_b.doc, "HCT") == 0);

    printf("\nУспіх: усі репліки збіглися до ідентичного тексту «HCT»!\n");
    return 0;
}
