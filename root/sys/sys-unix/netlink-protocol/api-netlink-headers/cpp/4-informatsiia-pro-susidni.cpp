#include <linux/rtnetlink.h>
#include <sys/socket.h>

// Ініціалізація структури ndmsg для запиту ARP/NDP у C++20
ndmsg ndm{
    .ndm_family = AF_INET,
    .ndm_ifindex = 1,
    .ndm_state = NUD_REACHABLE,
    .ndm_flags = NTF_PROXY,
    .ndm_type = RTN_UNICAST
};
