/* Файл: billing/payment_processor.c */
#define STATUS_AUTHORIZED  1
#define STATUS_CAPTURED    2
#define STATUS_REFUNDED    3
#define STATUS_CHARGEBACK  4  /* Новий статус, доданий під час релізу */

void process_status(int status) {
    if (status == STATUS_CHARGEBACK) {
        /* спеціальна логіка блокування */
    }
}
