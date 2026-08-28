#include <cstdint>

// Результат fib_lookup у C++ з явними типами та nullptr за замовчуванням
namespace net::kernel_sim {
    struct FibInfo;
    struct FibTable;

    struct FibResult {
        std::uint32_t   prefix{0};      /* Префікс адреси */
        std::uint8_t    prefixlen{0};   /* Довжина маски префіксу */
        std::uint8_t    nh_sel{0};      /* Обраний індекс next-hop у масиві ECMP */
        std::uint8_t    type{0};        /* Тип маршруту (RTN_UNICAST тощо) */
        std::uint8_t    scope{0};       /* Область видимості */
        std::uint32_t   tclassid{0};    /* Клас трафіку для QoS */
        const FibInfo*  fi{nullptr};    /* Знайдена структура FibInfo */
        const FibTable* table{nullptr}; /* Знайдена таблиця маршрутизації */
    };
}
