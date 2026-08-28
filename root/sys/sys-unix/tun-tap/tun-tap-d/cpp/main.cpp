// Приклад C++: RAII-клас керування TUN-пристроєм
#include <string>
#include <string_view>
#include <system_error>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/if.h>
#include <linux/if_tun.h>

class ScopedTun {
private:
    int fd_{-1};
    std::string name_;

public:
    explicit ScopedTun(std::string_view requested_name) {
        fd_ = ::open("/dev/net/tun", O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Cannot open /dev/net/tun");
        }

        struct ifreq ifr{};
        ifr.ifr_flags = IFF_TUN | IFF_NO_PI;
        if (!requested_name.empty()) {
            std::strncpy(ifr.ifr_name, requested_name.data(), IFNAMSIZ - 1);
        }

        if (::ioctl(fd_, TUNSETIFF, reinterpret_cast<void*>(&ifr)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "ioctl(TUNSETIFF) failed");
        }
        name_ = ifr.ifr_name;
    }

    ~ScopedTun() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }

    [[nodiscard]] int get_fd() const noexcept { return fd_; }
    [[nodiscard]] const std::string& get_name() const noexcept { return name_; }
};
