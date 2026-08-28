#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_HEADERS 16
#define KEY_LEN 32
#define VAL_LEN 64
#define PAYLOAD_MAX 512
#define MAX_STAGES 8

/* Статуси виконання стадії конвеєра */
typedef enum {
    STAGE_OK = 0,
    STAGE_FILTERED = 1,
    STAGE_ERROR = 2
} StageStatus;

/* Метадані заголовка */
typedef struct {
    char key[KEY_LEN];
    char value[VAL_LEN];
} Header;

/* Нормалізований конверт повідомлення */
typedef struct {
    char message_id[KEY_LEN];
    char correlation_id[KEY_LEN];
    Header headers[MAX_HEADERS];
    size_t header_count;
    char payload[PAYLOAD_MAX];
    size_t payload_len;
} NormalizedMessage;

/* Контекст обміну повідомленням (Exchange) */
typedef struct {
    NormalizedMessage in_msg;
    NormalizedMessage out_msg;
    char target_endpoint[VAL_LEN];
    char fault_reason[VAL_LEN];
    bool is_fault;
} Exchange;

/* Попереднє оголошення інтерфейсу стадії */
typedef struct PipelineStage PipelineStage;
typedef StageStatus (*StageFunc)(PipelineStage *self, Exchange *ex);

struct PipelineStage {
    const char *name;
    StageFunc process;
    void *context;
};

/* Допоміжні функції роботи з заголовками */
void set_header(NormalizedMessage *msg, const char *key, const char *val) {
    if (msg->header_count < MAX_HEADERS) {
        strncpy(msg->headers[msg->header_count].key, key, KEY_LEN - 1);
        msg->headers[msg->header_count].key[KEY_LEN - 1] = '\0';
        strncpy(msg->headers[msg->header_count].value, val, VAL_LEN - 1);
        msg->headers[msg->header_count].value[VAL_LEN - 1] = '\0';
        msg->header_count++;
    }
}

const char* get_header(const NormalizedMessage *msg, const char *key) {
    for (size_t i = 0; i < msg->header_count; i++) {
        if (strcmp(msg->headers[i].key, key) == 0) {
            return msg->headers[i].value;
        }
    }
    return NULL;
}

/* 1. Стадія перевірки автентифікації */
StageStatus auth_stage_process(PipelineStage *self, Exchange *ex) {
    (void)self;
    const char *token = get_header(&ex->in_msg, "X-Auth-Token");
    if (!token || strcmp(token, "secret-token-123") != 0) {
        strncpy(ex->fault_reason, "AUTH_REJECTED: Invalid or missing token", VAL_LEN - 1);
        ex->is_fault = true;
        return STAGE_ERROR;
    }
    return STAGE_OK;
}

/* 2. Стадія маршрутизації за змістом (CBR) */
StageStatus routing_stage_process(PipelineStage *self, Exchange *ex) {
    (void)self;
    const char *type = get_header(&ex->in_msg, "X-Message-Type");
    if (!type) {
        strncpy(ex->fault_reason, "ROUTING_FAILED: Missing message type", VAL_LEN - 1);
        ex->is_fault = true;
        return STAGE_ERROR;
    }

    if (strcmp(type, "ORDER_PAYMENT") == 0) {
        strncpy(ex->target_endpoint, "billing.service.v1", VAL_LEN - 1);
    } else if (strcmp(type, "INVENTORY_SYNC") == 0) {
        strncpy(ex->target_endpoint, "warehouse.service.v2", VAL_LEN - 1);
    } else {
        strncpy(ex->fault_reason, "ROUTING_FAILED: Unknown route", VAL_LEN - 1);
        ex->is_fault = true;
        return STAGE_ERROR;
    }
    return STAGE_OK;
}

/* 3. Стадія трансформації канонічного формату */
StageStatus transform_stage_process(PipelineStage *self, Exchange *ex) {
    (void)self;
    memcpy(&ex->out_msg, &ex->in_msg, sizeof(NormalizedMessage));
    
    char formatted_payload[PAYLOAD_MAX];
    snprintf(formatted_payload, sizeof(formatted_payload),
             "{\"target\":\"%s\",\"id\":\"%s\",\"data\":\"%s\"}",
             ex->target_endpoint, ex->in_msg.message_id, ex->in_msg.payload);

    strncpy(ex->out_msg.payload, formatted_payload, PAYLOAD_MAX - 1);
    ex->out_msg.payload[PAYLOAD_MAX - 1] = '\0';
    ex->out_msg.payload_len = strlen(ex->out_msg.payload);
    set_header(&ex->out_msg, "Content-Type", "application/json");
    return STAGE_OK;
}

/* Рушій конвеєра шини */
typedef struct {
    PipelineStage stages[MAX_STAGES];
    size_t stage_count;
} BusPipeline;

void bus_add_stage(BusPipeline *bus, const char *name, StageFunc func) {
    if (bus->stage_count < MAX_STAGES) {
        bus->stages[bus->stage_count].name = name;
        bus->stages[bus->stage_count].process = func;
        bus->stages[bus->stage_count].context = NULL;
        bus->stage_count++;
    }
}

void bus_execute(BusPipeline *bus, Exchange *ex) {
    printf("[BUS] Початок обробки повідомлення ID=%s\n", ex->in_msg.message_id);
    for (size_t i = 0; i < bus->stage_count; i++) {
        PipelineStage *stage = &bus->stages[i];
        StageStatus st = stage->process(stage, ex);
        if (st == STAGE_ERROR) {
            printf("[BUS] Збій на стадії '%s': %s -> Відправка в DLQ\n",
                   stage->name, ex->fault_reason);
            return;
        } else if (st == STAGE_FILTERED) {
            printf("[BUS] Повідомлення відфільтровано на стадії '%s'\n", stage->name);
            return;
        }
    }
    printf("[BUS] Успішна доставка до '%s': payload=%s\n",
           ex->target_endpoint, ex->out_msg.payload);
}

int main(void) {
    BusPipeline bus = {0};
    bus_add_stage(&bus, "AuthValidator", auth_stage_process);
    bus_add_stage(&bus, "ContentRouter", routing_stage_process);
    bus_add_stage(&bus, "JsonTransformer", transform_stage_process);

    /* Тест 1: Валідне платіжне повідомлення */
    Exchange ex1 = {0};
    strncpy(ex1.in_msg.message_id, "MSG-001", KEY_LEN - 1);
    set_header(&ex1.in_msg, "X-Auth-Token", "secret-token-123");
    set_header(&ex1.in_msg, "X-Message-Type", "ORDER_PAYMENT");
    strncpy(ex1.in_msg.payload, "amount=150.00;currency=USD", PAYLOAD_MAX - 1);
    ex1.in_msg.payload_len = strlen(ex1.in_msg.payload);
    bus_execute(&bus, &ex1);

    /* Тест 2: Повідомлення без валідного токена */
    Exchange ex2 = {0};
    strncpy(ex2.in_msg.message_id, "MSG-002", KEY_LEN - 1);
    set_header(&ex2.in_msg, "X-Auth-Token", "wrong-token");
    set_header(&ex2.in_msg, "X-Message-Type", "ORDER_PAYMENT");
    strncpy(ex2.in_msg.payload, "amount=500.00", PAYLOAD_MAX - 1);
    bus_execute(&bus, &ex2);

    return 0;
}
