#include <sys/socket.h>
#include <net/if.h>
#include <linux/if_xdp.h>
#include <system_error>
#include <string_view>
#include <cstring>

void bind_xsk_cpp(int xsk_fd, std::string_view ifname, uint32_t queue_id, uint16_t flags) {
    uint32_t ifindex = ::if_nametoindex(ifname.data());
    if (ifindex == 0) {
        throw std::system_error(errno, std::generic_category(), "if_nametoindex failed");
    }

    struct sockaddr_xdp sxdp{};
    sxdp.sxdp_family = AF_XDP;
    sxdp.sxdp_ifindex = ifindex;
    sxdp.sxdp_queue_id = queue_id;
    sxdp.sxdp_flags = flags;

    if (::bind(xsk_fd, reinterpret_cast<struct sockaddr*>(&sxdp), sizeof(sxdp)) < 0) {
        throw std::system_error(errno, std::generic_category(), "bind(AF_XDP) failed");
    }
}
