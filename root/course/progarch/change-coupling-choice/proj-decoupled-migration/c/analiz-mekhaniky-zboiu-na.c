/* c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Структура DTO для синхронного REST-запиту (версія 1) */
typedef struct {
    char order_id[32];
    double amount;
} OrderPayloadV1;

/* Старий клієнт відправляє лише V1 */
int send_billing_request_v1(const OrderPayloadV1* payload) {
    printf("[REST Client C] Sending V1 request: Order=%s, Amount=%.2f\n", 
           payload->order_id, payload->amount);
    
    /* Емуляція сервера V2, який чекає обов'язкове поле tax_id */
    int server_has_tax_id_requirement = 1;
    if (server_has_tax_id_requirement) {
        printf("[REST Server V2] ERROR 400: Missing required field 'tax_identifier'\n");
        return -1; /* Збій виклику — релізи зчеплені! */
    }
    return 0;
}

int main(void) {
    OrderPayloadV1 order = {"ORD-9901", 149.99};
    int res = send_billing_request_v1(&order);
    if (res != 0) {
        printf("[System] Lockstep Failure: Cannot deploy OrderService without updating BillingService!\n");
    }
    return 0;
}
