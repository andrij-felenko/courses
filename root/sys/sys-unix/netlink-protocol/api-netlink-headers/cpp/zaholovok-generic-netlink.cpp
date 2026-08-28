#include <linux/genetlink.h>
#include <cstdint>

// Ініціалізація заголовка Generic Netlink genlmsghdr у C++20
constexpr uint8_t ctrl_ver = 2;
genlmsghdr gnl{
    .cmd = CTRL_CMD_GETFAMILY,
    .version = ctrl_ver,
    .reserved = 0
};
