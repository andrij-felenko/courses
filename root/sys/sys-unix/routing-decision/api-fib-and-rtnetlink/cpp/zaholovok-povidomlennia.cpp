#include <linux/rtnetlink.h>
#include <cstdint>

// Обгортка заголовка rtmsg з ініціалізацією полів у C++20
namespace net {
    struct RtMsg {
        std::uint8_t family{AF_INET};    /* Сімейство адрес (AF_INET або AF_INET6) */
        std::uint8_t dst_len{0};         /* Довжина маски префіксу призначення */
        std::uint8_t src_len{0};         /* Довжина маски префіксу джерела */
        std::uint8_t tos{0};             /* Type of Service (ToS) / DSCP */
        std::uint8_t table{RT_TABLE_MAIN};/* ID таблиці маршрутизації */
        std::uint8_t protocol{RTPROT_STATIC};/* Протокол джерела (BGP, Static) */
        std::uint8_t scope{RT_SCOPE_UNIVERSE};/* Область видимості */
        std::uint8_t type{RTN_UNICAST};  /* Тип маршруту (RTN_UNICAST тощо) */
        std::uint32_t flags{0};          /* Допоміжні прапорці */
    };
}
