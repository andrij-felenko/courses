#include <linux/netlink.h>
#include <sys/socket.h>
#include <cstdint>

// У C++20 структура sockaddr_nl ініціалізується через designated initializers
constexpr uint32_t multicast_groups = RTMGRP_LINK | RTMGRP_IPV4_IFADDR;
sockaddr_nl sa{
    .nl_family = AF_NETLINK,
    .nl_pad = 0,
    .nl_pid = 0, // 0 дозволяє ядру призначити Port ID
    .nl_groups = multicast_groups
};
