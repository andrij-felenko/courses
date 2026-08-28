#include <cstdint>

// Запис fib_alias у C++ з підтримкою зв'язку з FibInfo
namespace net::kernel_sim {
    struct FibInfo; // Випереджувальне оголошення

    struct FibAlias {
        const FibInfo* info{nullptr}; /* Незмінні дані про next-hop */
        std::uint8_t   tos{0};        /* Type of Service */
        std::uint8_t   type{0};       /* Тип маршруту (RTN_UNICAST тощо) */
        std::uint8_t   state{0};      /* Внутрішній стан */
        std::uint8_t   slen{0};       /* Довжина маски префіксу (32 - prefix_length) */
    };
}
