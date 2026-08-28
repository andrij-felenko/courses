/* Файл: include/contracts/payment_types.h */
#ifndef PAYMENT_TYPES_H
#define PAYMENT_TYPES_H

typedef enum {
    PAYMENT_STATUS_AUTHORIZED = 1,
    PAYMENT_STATUS_CAPTURED   = 2,
    PAYMENT_STATUS_REFUNDED   = 3,
    PAYMENT_STATUS_CHARGEBACK = 4
} PaymentStatus;

typedef struct {
    unsigned long transaction_id;
    PaymentStatus status;
    long amount_cents;
    char currency[4];
} PaymentRecord;

#endif
