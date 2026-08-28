#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>

void print_device_info(int fd) {
    struct input_id id;
    char name[256] = "Unknown";

    if (ioctl(fd, EVIOCGNAME(sizeof(name)), name) >= 0 &&
        ioctl(fd, EVIOCGID, &id) >= 0) {
        printf("Пристрій: %s (Bus: 0x%04x, Vendor: 0x%04x, Product: 0x%04x)\n",
               name, id.bustype, id.vendor, id.product);
    }
}
