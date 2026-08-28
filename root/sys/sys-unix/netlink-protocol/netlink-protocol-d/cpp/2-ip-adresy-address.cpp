#include <linux/rtnetlink.h>
#include <sys/socket.h>

// Формування запиту ifaddrmsg для IPv4/IPv6 у C++20
ifaddrmsg ifa{
    .ifa_family = AF_INET,
    .ifa_prefixlen = 24,
    .ifa_flags = IFA_F_PERMANENT,
    .ifa_scope = RT_SCOPE_UNIVERSE,
    .ifa_index = 1
};
