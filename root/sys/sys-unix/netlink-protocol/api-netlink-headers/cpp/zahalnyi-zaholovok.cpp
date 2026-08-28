#include <linux/netlink.h>
#include <cstdint>

// Ідіоматична ініціалізація заголовка nlmsghdr у C++20
constexpr uint32_t req_seq = 1001;
nlmsghdr nlh{
    .nlmsg_len = NLMSG_LENGTH(0),
    .nlmsg_type = RTM_GETLINK,
    .nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP,
    .nlmsg_seq = req_seq,
    .nlmsg_pid = 0
};
