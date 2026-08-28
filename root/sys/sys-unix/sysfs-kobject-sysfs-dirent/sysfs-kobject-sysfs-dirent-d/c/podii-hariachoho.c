/* Зчитування подій uevent через Netlink сокет у C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>

int main(void) {
    int fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT);
    if (fd < 0) return 1;

    struct sockaddr_nl nls;
    memset(&nls, 0, sizeof(nls));
    nls.nl_family = AF_NETLINK;
    nls.nl_pid = getpid();
    nls.nl_groups = -1; /* Слухати всі групи uevent */

    if (bind(fd, (struct sockaddr *)&nls, sizeof(nls)) < 0) {
        close(fd);
        return 1;
    }

    char buf[4096];
    while (1) {
        ssize_t len = recv(fd, buf, sizeof(buf) - 1, 0);
        if (len > 0) {
            buf[len] = '\0';
            printf("Uevent: %s\n", buf);
        }
    }

    close(fd);
    return 0;
}
