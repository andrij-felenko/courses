#include <sys/socket.h>
#include <net/if.h>
#include <linux/if_xdp.h>
#include <stdio.h>
#include <string.h>

int bind_xsk(int xsk_fd, const char *ifname, uint32_t queue_id, uint16_t flags) {
    uint32_t ifindex = if_nametoindex(ifname);
    if (ifindex == 0) {
        perror("if_nametoindex failed");
        return -1;
    }

    struct sockaddr_xdp sxdp;
    memset(&sxdp, 0, sizeof(sxdp));
    sxdp.sxdp_family = AF_XDP;
    sxdp.sxdp_ifindex = ifindex;
    sxdp.sxdp_queue_id = queue_id;
    sxdp.sxdp_flags = flags;

    if (bind(xsk_fd, (struct sockaddr *)&sxdp, sizeof(sxdp)) < 0) {
        perror("bind(AF_XDP) failed");
        return -1;
    }

    return 0;
}
