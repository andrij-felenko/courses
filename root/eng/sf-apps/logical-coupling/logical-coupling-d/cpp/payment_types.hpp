/* Файл: include/contracts/payment_types.hpp */
#pragma once
#include <cstdint>
#include <string_view>

enum class PaymentStatus : uint8_t {
    Authorized = 1,
    Captured   = 2,
    Refunded   = 3,
    Chargeback = 4
};

struct PaymentRecord {
    uint64_t transaction_id;
    PaymentStatus status;
    int64_t amount_cents;
    char currency[4];
};
