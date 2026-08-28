#include <linux/rtnetlink.h>
#include <sys/socket.h>

// Створення заповненої структури rtmsg у C++20
rtmsg rtm{
    .rtm_family = AF_INET,
    .rtm_dst_len = 24,
    .rtm_src_len = 0,
    .rtm_tos = 0,
    .rtm_table = RT_TABLE_MAIN,
    .rtm_protocol = RTPROT_STATIC,
    .rtm_scope = RT_SCOPE_LINK,
    .rtm_type = RTN_UNICAST,
    .rtm_flags = 0
};
