#include <linux/rtnetlink.h>
#include <sys/socket.h>

// Формування запиту rtmsg для маршрутизації в C++20
rtmsg rtm{
    .rtm_family = AF_INET,
    .rtm_dst_len = 32,
    .rtm_src_len = 0,
    .rtm_tos = 0,
    .rtm_table = RT_TABLE_MAIN,
    .rtm_protocol = RTPROT_STATIC,
    .rtm_scope = RT_SCOPE_UNIVERSE,
    .rtm_type = RTN_UNICAST,
    .rtm_flags = 0
};
