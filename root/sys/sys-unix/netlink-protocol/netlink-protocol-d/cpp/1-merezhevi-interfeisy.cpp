#include <linux/rtnetlink.h>
#include <net/if.h>

// Ініціалізація ifinfomsg для запиту стану інтерфейсу в C++20
ifinfomsg ifi{
    .ifi_family = AF_UNSPEC,
    .ifi_type = ARPHRD_ETHER,
    .ifi_index = 0, // 0 означає запит для всіх інтерфейсів
    .ifi_flags = IFF_UP,
    .ifi_change = 0xFFFFFFFF
};
