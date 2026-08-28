#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <stdint.h>
#include <linux/vhost.h>
#include <linux/virtio_ids.h>

#define VDPA_DEV_PATH "/dev/vhost-vdpa-0"

int main(void) {
    int fd = open(VDPA_DEV_PATH, O_RDWR);
    if (fd < 0) {
        perror("Не вдалося відкрити " VDPA_DEV_PATH);
        return EXIT_FAILURE;
    }

    uint32_t device_id = 0;
    if (ioctl(fd, VHOST_VDPA_GET_DEVICE_ID, &device_id) < 0) {
        perror("Помилка VHOST_VDPA_GET_DEVICE_ID");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("[+] vDPA Device ID: %u (%s)\n", device_id,
           device_id == VIRTIO_ID_NET ? "virtio-net" :
           device_id == VIRTIO_ID_BLOCK ? "virtio-blk" : "інший");

    uint64_t features = 0;
    if (ioctl(fd, VHOST_GET_FEATURES, &features) < 0) {
        perror("Помилка VHOST_GET_FEATURES");
        close(fd);
        return EXIT_FAILURE;
    }
    printf("[+] HW Feature Bits: 0x%llx\n", (unsigned long long)features);

    uint8_t status = 0;
    if (ioctl(fd, VHOST_VDPA_GET_STATUS, &status) < 0) {
        perror("Помилка VHOST_VDPA_GET_STATUS");
        close(fd);
        return EXIT_FAILURE;
    }
    printf("[+] Device Status Byte: 0x%02x\n", status);

    if (device_id == VIRTIO_ID_NET) {
        struct {
            uint32_t off;
            uint32_t len;
            uint8_t buf[6];
        } cfg = { .off = 0, .len = 6 };

        if (ioctl(fd, VHOST_VDPA_GET_CONFIG, &cfg) < 0) {
            perror("Помилка VHOST_VDPA_GET_CONFIG");
            close(fd);
            return EXIT_FAILURE;
        }

        printf("[+] Hardware MAC Address: %02x:%02x:%02x:%02x:%02x:%02x\n",
               cfg.buf[0], cfg.buf[1], cfg.buf[2],
               cfg.buf[3], cfg.buf[4], cfg.buf[5]);
    }

    close(fd);
    return EXIT_SUCCESS;
}
