#include <linux/genetlink.h>
#include <cstdint>

// Заповнення заголовка Generic Netlink у C++20
constexpr uint8_t genl_version = 1;
genlmsghdr gnl{
    .cmd = CTRL_CMD_GETFAMILY,
    .version = genl_version,
    .reserved = 0
};
