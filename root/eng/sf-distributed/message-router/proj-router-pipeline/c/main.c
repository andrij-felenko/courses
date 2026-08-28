#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_HEADERS 16
#define MAX_KEY_LEN 32
#define MAX_VAL_LEN 64
#define MAX_PAYLOAD 512
#define MAX_SLIP_HOPS 8
#define MAX_DESTINATIONS 8
#define MAX_RULES 16

typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
} HeaderPair;

typedef struct {
    char id[32];
    char topic[32];
    HeaderPair headers[MAX_HEADERS];
    size_t header_count;
    char payload[MAX_PAYLOAD];
    size_t payload_len;
    char routing_slip[MAX_SLIP_HOPS][32];
    size_t slip_count;
} MessageEnvelope;

typedef struct MessageSink {
    char name[32];
    bool (*deliver)(struct MessageSink* self, const MessageEnvelope* msg);
    size_t delivered_count;
} MessageSink;

static bool queue_deliver(MessageSink* self, const MessageEnvelope* msg) {
    printf("  [Черга %s] Отримано msg_id=%s payload: %s\n", self->name, msg->id, msg->payload);
    self->delivered_count++;
    return true;
}

static bool dlq_deliver(MessageSink* self, const MessageEnvelope* msg) {
    fprintf(stderr, "  ⚠️ [МЕРТВА ЧЕРГА %s] Ізольовано непридатне msg_id=%s\n", self->name, msg->id);
    self->delivered_count++;
    return true;
}

static const char* get_header(const MessageEnvelope* msg, const char* key) {
    for (size_t i = 0; i < msg->header_count; i++) {
        if (strcmp(msg->headers[i].key, key) == 0) {
            return msg->headers[i].value;
        }
    }
    return NULL;
}

typedef bool (*PredicateFn)(const MessageEnvelope* msg);

typedef struct {
    char rule_name[32];
    PredicateFn predicate;
    MessageSink* destinations[MAX_DESTINATIONS];
    size_t dest_count;
} RoutingRule;

typedef struct {
    RoutingRule rules[MAX_RULES];
    size_t rule_count;
    MessageSink* named_sinks[MAX_RULES];
    size_t named_sink_count;
    MessageSink* wire_tap;
    MessageSink* dlq;
} MessageRouter;

void router_init(MessageRouter* router, MessageSink* dlq) {
    memset(router, 0, sizeof(MessageRouter));
    router->dlq = dlq;
}

void router_set_wire_tap(MessageRouter* router, MessageSink* tap) {
    router->wire_tap = tap;
}

void router_register_sink(MessageRouter* router, MessageSink* sink) {
    if (router->named_sink_count < MAX_RULES) {
        router->named_sinks[router->named_sink_count++] = sink;
    }
}

void router_add_rule(MessageRouter* router, const char* name, PredicateFn pred, MessageSink** dests, size_t dest_count) {
    if (router->rule_count >= MAX_RULES) return;
    RoutingRule* r = &router->rules[router->rule_count++];
    strncpy(r->rule_name, name, sizeof(r->rule_name) - 1);
    r->predicate = pred;
    r->dest_count = dest_count < MAX_DESTINATIONS ? dest_count : MAX_DESTINATIONS;
    for (size_t i = 0; i < r->dest_count; i++) {
        r->destinations[i] = dests[i];
    }
}

void router_route(MessageRouter* router, MessageEnvelope* msg) {
    // 1. Wire Tap
    if (router->wire_tap) {
        router->wire_tap->deliver(router->wire_tap, msg);
    }

    // 2. Routing Slip
    if (msg->slip_count > 0) {
        char next_hop[32];
        strncpy(next_hop, msg->routing_slip[0], sizeof(next_hop) - 1);
        next_hop[sizeof(next_hop) - 1] = '\0';

        // Зсув списку (pop)
        for (size_t i = 0; i < msg->slip_count - 1; i++) {
            strcpy(msg->routing_slip[i], msg->routing_slip[i + 1]);
        }
        msg->slip_count--;

        // Пошук цільового каналу
        for (size_t i = 0; i < router->named_sink_count; i++) {
            if (strcmp(router->named_sinks[i]->name, next_hop) == 0) {
                printf("-> [Routing Slip] Передача на вузол '%s'\n", next_hop);
                router->named_sinks[i]->deliver(router->named_sinks[i], msg);
                return;
            }
        }

        fprintf(stderr, "-> [Routing Slip Помилка] Вузол '%s' не знайдено!\n", next_hop);
        if (router->dlq) router->dlq->deliver(router->dlq, msg);
        return;
    }

    // 3. Перевірка правил (Content-Based / Filter / Recipient List)
    bool routed = false;
    for (size_t i = 0; i < router->rule_count; i++) {
        RoutingRule* r = &router->rules[i];
        if (r->predicate(msg)) {
            for (size_t j = 0; j < r->dest_count; j++) {
                r->destinations[j]->deliver(r->destinations[j], msg);
                routed = true;
            }
        }
    }

    // 4. Dead Letter Queue
    if (!routed && router->dlq) {
        router->dlq->deliver(router->dlq, msg);
    }
}

static bool is_region_eu(const MessageEnvelope* msg) {
    const char* reg = get_header(msg, "region");
    return reg && strcmp(reg, "EU") == 0;
}

static bool is_high_value(const MessageEnvelope* msg) {
    const char* amt = get_header(msg, "amount");
    if (!amt) return false;
    return atof(amt) >= 10000.0;
}

int main(void) {
    MessageSink dlq = {.name = "DLQ.PRIMARY", .deliver = dlq_deliver, .delivered_count = 0};
    MessageSink audit = {.name = "AUDIT.STREAM", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_eu = {.name = "ORDERS.EU", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_us = {.name = "ORDERS.US", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_fraud = {.name = "FRAUD.EVALUATION", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_kyc = {.name = "KYC.VALIDATION", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_billing = {.name = "BILLING.SETTLEMENT", .deliver = queue_deliver, .delivered_count = 0};

    MessageRouter router;
    router_init(&router, &dlq);
    router_set_wire_tap(&router, &audit);

    router_register_sink(&router, &q_kyc);
    router_register_sink(&router, &q_fraud);
    router_register_sink(&router, &q_billing);

    MessageSink* eu_dests[] = {&q_eu};
    router_add_rule(&router, "EU_Rule", is_region_eu, eu_dests, 1);

    MessageSink* vip_dests[] = {&q_us, &q_fraud};
    router_add_rule(&router, "VIP_Rule", is_high_value, vip_dests, 2);

    printf("=== 1. Звичайне замовлення з ЄС ===\n");
    MessageEnvelope m1 = {.header_count = 2, .payload_len = 15, .slip_count = 0};
    strcpy(m1.id, "msg_001");
    strcpy(m1.topic, "orders");
    strcpy(m1.headers[0].key, "region"); strcpy(m1.headers[0].value, "EU");
    strcpy(m1.headers[1].key, "amount"); strcpy(m1.headers[1].value, "250.0");
    strcpy(m1.payload, "{\"item\":\"Book\"}");
    router_route(&router, &m1);

    printf("\n=== 2. VIP замовлення великої суми (Мультивектор) ===\n");
    MessageEnvelope m2 = {.header_count = 2, .payload_len = 17, .slip_count = 0};
    strcpy(m2.id, "msg_002");
    strcpy(m2.topic, "orders");
    strcpy(m2.headers[0].key, "region"); strcpy(m2.headers[0].value, "US");
    strcpy(m2.headers[1].key, "amount"); strcpy(m2.headers[1].value, "50000.0");
    strcpy(m2.payload, "{\"item\":\"Server\"}");
    router_route(&router, &m2);

    printf("\n=== 3. Повідомлення з Routing Slip ===\n");
    MessageEnvelope m3 = {.header_count = 1, .payload_len = 19, .slip_count = 3};
    strcpy(m3.id, "msg_003");
    strcpy(m3.topic, "onboarding");
    strcpy(m3.headers[0].key, "user"); strcpy(m3.headers[0].value, "usr_99");
    strcpy(m3.routing_slip[0], "KYC.VALIDATION");
    strcpy(m3.routing_slip[1], "FRAUD.EVALUATION");
    strcpy(m3.routing_slip[2], "BILLING.SETTLEMENT");
    strcpy(m3.payload, "{\"action\":\"verify\"}");
    router_route(&router, &m3);

    printf("\n=== 4. Немаршрутизоване повідомлення (падає в DLQ) ===\n");
    MessageEnvelope m4 = {.header_count = 1, .payload_len = 4, .slip_count = 0};
    strcpy(m4.id, "msg_004");
    strcpy(m4.topic, "telemetry");
    strcpy(m4.headers[0].key, "sensor"); strcpy(m4.headers[0].value, "temp_01");
    strcpy(m4.payload, "24.5");
    router_route(&router, &m4);

    return 0;
}
