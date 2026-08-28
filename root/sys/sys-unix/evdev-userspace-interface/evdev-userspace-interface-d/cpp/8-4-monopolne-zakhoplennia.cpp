#include <iostream>
#include <system_error>
#include <sys/ioctl.h>
#include <linux/input.h>

void set_device_grab(int fd, bool enable) {
    if (::ioctl(fd, EVIOCGRAB, enable ? 1 : 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "EVIOCGRAB failed");
    }
}
