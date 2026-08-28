#include <cstdint>

// Елемент ECMP next-hop у C++ з ініціалізацією членів
namespace net {
    struct RtNextHop {
        std::uint16_t len{0};     /* Довжина структури разом із під-атрибутами */
        std::uint8_t  flags{0};   /* Прапорці (RTNH_F_DEAD, RTNH_F_LINKDOWN) */
        std::uint8_t  hops{0};    /* Вага маршруту для балансування трафіку */
        std::int32_t  ifindex{0}; /* Індекс вихідного інтерфейсу */
    };
}
