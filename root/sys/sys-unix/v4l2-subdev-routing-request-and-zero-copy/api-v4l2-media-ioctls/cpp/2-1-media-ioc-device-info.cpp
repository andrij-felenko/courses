#include <linux/media.h>
#include <sys/ioctl.h>
#include <string_view>
#include <system_error>

// Ініціалізація та безпечне вичитування полів у C++20
media_device_info dev_info{};
if (::ioctl(media_fd, MEDIA_IOC_DEVICE_INFO, &dev_info) < 0) {
    throw std::system_error(errno, std::generic_category(), "MEDIA_IOC_DEVICE_INFO failed");
}

std::string_view driver{dev_info.driver};
std::string_view model{dev_info.model};
std::string_view bus{dev_info.bus_info};
