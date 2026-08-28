/* c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Модель подійної структури з опціональними полями */
typedef struct {
    char event_id[64];
    char order_id[32];
    double amount;
    char tax_identifier[32]; /* Нове поле v2 (може бути порожнім) */
    int has_tax_identifier;
} OrderPlacedEvent;

/* Транзакційний запис у таблицю Outbox (Емуляція) */
int write_to_transactional_outbox(const char* order_id, double amount, const char* tax_id) {
    printf("[Database Transaction] BEGIN\n");
    printf("  [DB Table 'orders'] INSERT INTO orders VALUES ('%s', %.2f)\n", order_id, amount);
    
    printf("  [DB Table 'outbox'] INSERT INTO outbox_events (event_type, payload) VALUES ('OrderPlaced', ");
    if (tax_id && strlen(tax_id) > 0) {
        printf("'{\"order_id\":\"%s\",\"amount\":%.2f,\"tax_id\":\"%s\"}')\n", order_id, amount, tax_id);
    } else {
        printf("'{\"order_id\":\"%s\",\"amount\":%.2f}')\n", order_id, amount);
    }
    printf("[Database Transaction] COMMIT SUCCESSFUL\n");
    return 0;
}

/* Поблажливий читач на стороні BillingService */
void consume_event_tolerant(const OrderPlacedEvent* event) {
    printf("[Billing Consumer C] Processing Order=%s, Amount=%.2f\n", event->order_id, event->amount);
    
    if (event->has_tax_identifier) {
        printf("  -> Tax ID present: %s (Processing V2 logic)\n", event->tax_identifier);
    } else {
        printf("  -> Tax ID missing: Using default fallback (Processing V1 legacy compatibility)\n");
    }
    printf("[Billing Consumer C] Event %s processed successfully!\n", event->event_id);
}

int main(void) {
    printf("=== КРОК 1: Викатка OrderService V2 (додає Outbox) ===\n");
    write_to_transactional_outbox("ORD-9902", 299.50, NULL);
    
    printf("\n=== КРОК 2: Обробка старою/перехідною версією BillingService ===\n");
    OrderPlacedEvent ev1 = {
        .event_id = "EVT-1001",
        .order_id = "ORD-9902",
        .amount = 299.50,
        .has_tax_identifier = 0
    };
    consume_event_tolerant(&ev1);
    
    printf("\n=== КРОК 3: Викатка оновленого BillingService V2 ===\n");
    write_to_transactional_outbox("ORD-9903", 450.00, "UA12345678");
    OrderPlacedEvent ev2 = {
        .event_id = "EVT-1002",
        .order_id = "ORD-9903",
        .amount = 450.00,
        .tax_identifier = "UA12345678",
        .has_tax_identifier = 1
    };
    consume_event_tolerant(&ev2);
    
    return 0;
}
