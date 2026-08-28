#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

int create_rfcomm_tty(const char *dest_mac, uint8_t channel) {
    int ctl_fd = open("/dev/rfcomm", O_RDWR);
    if (ctl_fd < 0) return -1;

    struct rfcomm_dev_req req;
    memset(&req, 0, sizeof(req));
    req.dev_id = -1; // Автоматично призначити перший вільний індекс (/dev/rfcomm0)
    req.flags = (1 << RFCOMM_RELEASE_ONHUP);
    req.channel = channel;
    str2ba(dest_mac, &req.dst);

    int dev_id = ioctl(ctl_fd, RFCOMMCREATEDEV, &req);
    close(ctl_fd);
    return dev_id;
}
