#include <string_view>
#include <expected>
#include <system_error>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

std::expected<int, std::error_code> create_rfcomm_tty(std::string_view dest_mac, uint8_t channel) {
    int ctl_fd = ::open("/dev/rfcomm", O_RDWR);
    if (ctl_fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    struct rfcomm_dev_req req{};
    req.dev_id = -1; // Автоматичний вибір /dev/rfcommN
    req.flags = (1 << RFCOMM_RELEASE_ONHUP);
    req.channel = channel;
    
    std::string mac_str(dest_mac);
    if (str2ba(mac_str.c_str(), &req.dst) < 0) {
        ::close(ctl_fd);
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    int dev_id = ::ioctl(ctl_fd, RFCOMMCREATEDEV, &req);
    ::close(ctl_fd);
    
    if (dev_id < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return dev_id;
}
