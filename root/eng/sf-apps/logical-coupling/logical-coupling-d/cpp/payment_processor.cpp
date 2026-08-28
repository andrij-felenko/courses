/* Файл: billing/payment_processor.cpp */
#include <cstdint>

enum class PaymentStatus : uint8_t {
    Authorized = 1,
    Captured   = 2,
    Refunded   = 3,
    Chargeback = 4  // Новий статус, доданий під час релізу
};

void process_status(PaymentStatus status) {
    if (status == PaymentStatus::Chargeback) {
        // спеціальна логіка блокування
    }
}
