#include <linux/gpio.h>
#include <sys/ioctl.h>
#include <cstdint>
#include <system_error>

void set_line_values_v2(int req_fd, std::uint64_t mask, std::uint64_t bits) {
    struct gpio_v2_line_values vals{};
    vals.mask = mask;
    vals.bits = bits;

    if (ioctl(req_fd, GPIO_V2_LINE_SET_VALUES_IOCTL, &vals) < 0) {
        throw std::system_error(errno, std::generic_category(), "GPIO_V2_LINE_SET_VALUES_IOCTL failed");
    }
}
