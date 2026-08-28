#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

typedef enum {
    CMD_DEPOSIT,
    CMD_WITHDRAW,
    CMD_FREEZE,
    CMD_UNFREEZE
} OrderCmd;

typedef struct {
    OrderCmd cmd;
    int amount;
    uint32_t reply_to;
} OrderMessage;

typedef struct AccountActor AccountActor;
typedef void (*AccountBehavior)(AccountActor* self, const OrderMessage* msg);

struct AccountActor {
    uint32_t id;
    int balance;
    AccountBehavior behavior;
};

void active_behavior(AccountActor* self, const OrderMessage* msg);
void frozen_behavior(AccountActor* self, const OrderMessage* msg);

void active_behavior(AccountActor* self, const OrderMessage* msg) {
    switch (msg->cmd) {
        case CMD_DEPOSIT:
            self->balance += msg->amount;
            printf("[Актор %u] Депозит +%d. Новий баланс: %d\n", self->id, msg->amount, self->balance);
            break;
        case CMD_WITHDRAW:
            if (self->balance >= msg->amount) {
                self->balance -= msg->amount;
                printf("[Актор %u] Зняття -%d. Залишок: %d\n", self->id, msg->amount, self->balance);
            } else {
                printf("[Актор %u] Відхилено: недостатньо коштів (%d < %d)\n", self->id, self->balance, msg->amount);
            }
            break;
        case CMD_FREEZE:
            printf("[Актор %u] Рахунок заморожено! Перемикання поведінки на frozen_behavior.\n", self->id);
            self->behavior = frozen_behavior;
            break;
        case CMD_UNFREEZE:
            printf("[Актор %u] Рахунок уже активний.\n", self->id);
            break;
    }
}

void frozen_behavior(AccountActor* self, const OrderMessage* msg) {
    if (msg->cmd == CMD_UNFREEZE) {
        printf("[Актор %u] Рахунок розморожено. Повернення до active_behavior.\n", self->id);
        self->behavior = active_behavior;
    } else {
        printf("[Актор %u] ВІДХИЛЕНО: рахунок заблоковано! Операція %d неможлива.\n", self->id, msg->cmd);
    }
}

int main(void) {
    AccountActor account = { .id = 101, .balance = 500, .behavior = active_behavior };

    OrderMessage m1 = { .cmd = CMD_WITHDRAW, .amount = 200, .reply_to = 0 };
    OrderMessage m2 = { .cmd = CMD_FREEZE, .amount = 0, .reply_to = 0 };
    OrderMessage m3 = { .cmd = CMD_WITHDRAW, .amount = 100, .reply_to = 0 };
    OrderMessage m4 = { .cmd = CMD_UNFREEZE, .amount = 0, .reply_to = 0 };
    OrderMessage m5 = { .cmd = CMD_WITHDRAW, .amount = 100, .reply_to = 0 };

    account.behavior(&account, &m1);
    account.behavior(&account, &m2);
    account.behavior(&account, &m3); // Має бути відхилено через заморозку
    account.behavior(&account, &m4);
    account.behavior(&account, &m5); // Має виконатися успішно

    return 0;
}
