#include <linux/netlink.h>
#include <cstdint>

// Ідіоматичне створення та заповнення заголовка Netlink у C++20
constexpr uint32_t payload_size = 1024;
nlmsghdr header{
    .nlmsg_len = NLMSG_LENGTH(payload_size),
    .nlmsg_type = RTM_GETLINK,
    .nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP,
    .nlmsg_seq = 1,
    .nlmsg_pid = 0
};
