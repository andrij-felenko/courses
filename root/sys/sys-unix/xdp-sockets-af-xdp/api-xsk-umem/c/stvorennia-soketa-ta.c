#include <sys/socket.h>
#include <linux/if_xdp.h>
#include <stdio.h>
#include <unistd.h>

int create_raw_xsk(void) {
    int xsk_fd = socket(AF_XDP, SOCK_RAW, 0);
    if (xsk_fd < 0) {
        perror("socket(AF_XDP) failed");
        return -1;
    }
    return xsk_fd;
}
