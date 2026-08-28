#include <linux/media.h>
#include <sys/ioctl.h>
#include <string.h>
#include <stdio.h>

struct media_device_info dev_info;
memset(&dev_info, 0, sizeof(dev_info));

if (ioctl(media_fd, MEDIA_IOC_DEVICE_INFO, &dev_info) == 0) {
    printf("Driver: %s, Model: %s, Bus: %s\n",
           dev_info.driver, dev_info.model, dev_info.bus_info);
}
