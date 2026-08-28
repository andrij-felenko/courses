#include <iostream>
#include <array>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>

void print_device_info(int fd) {
    struct input_id id{};
    std::array<char, 256> name_buf{};
    name_buf.fill(0);

    if (::ioctl(fd, EVIOCGNAME(name_buf.size()), name_buf.data()) >= 0 &&
        ::ioctl(fd, EVIOCGID, &id) >= 0) {
        std::cout << "Device: " << name_buf.data()
                  << " (Bus: 0x" << std::hex << id.bustype
                  << ", Vendor: 0x" << id.vendor
                  << ", Product: 0x" << id.product << std::dec << ")\n";
    }
}
