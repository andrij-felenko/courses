#include <linux/gpio.h>
#include <sys/ioctl.h>
#include <span>
#include <string_view>
#include <system_error>

// Низькорівнева обгортка ioctl v2 у стилі C++20
struct ChardevLineRequest {
    int request_fd{-1};

    static ChardevLineRequest create(int chip_fd, std::span<const std::uint32_t> offsets, std::string_view consumer) {
        struct gpio_v2_line_request req{};
        req.num_lines = static_cast<std::uint32_t>(offsets.size());
        for (std::size_t i = 0; i < offsets.size(); ++i) {
            req.offsets[i] = offsets[i];
        }
        consumer.copy(req.consumer, sizeof(req.consumer) - 1);
        req.config.flags = GPIO_V2_LINE_FLAG_OUTPUT;

        if (ioctl(chip_fd, GPIO_V2_GET_LINE_IOCTL, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "GPIO_V2_GET_LINE_IOCTL failed");
        }
        return ChardevLineRequest{req.fd};
    }
};
