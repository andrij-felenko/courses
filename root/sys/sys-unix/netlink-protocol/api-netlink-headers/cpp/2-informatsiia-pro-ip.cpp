#include <linux/rtnetlink.h>
#include <sys/socket.h>

// Ініціалізація ifaddrmsg у C++20
ifaddrmsg ifa{
    .ifa_family = AF_INET6,
    .ifa_prefixlen = 64,
    .ifa_flags = IFA_F_PERMANENT,
    .ifa_scope = RT_SCOPE_UNIVERSE,
    .ifa_index = 3
};
