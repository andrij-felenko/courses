#include <linux/rtnetlink.h>
#include <net/if.h>

// Створення ifinfomsg для модифікації стану каналу у C++20
ifinfomsg ifi{
    .ifi_family = AF_UNSPEC,
    .ifi_type = ARPHRD_ETHER,
    .ifi_index = 2,
    .ifi_flags = IFF_UP,
    .ifi_change = IFF_UP
};
