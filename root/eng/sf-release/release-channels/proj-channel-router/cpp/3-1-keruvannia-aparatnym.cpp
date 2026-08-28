#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>
#include <string_view>

class WatchdogDevice {
public:
    explicit WatchdogDevice(std::string_view dev_path = "/dev/watchdog") noexcept {
        fd_ = ::open(dev_path.data(), O_WRONLY);
    }
    ~WatchdogDevice() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    bool set_timeout(int seconds) noexcept {
        if (fd_ < 0) return false;
        return (::ioctl(fd_, WDIOC_SETTIMEOUT, &seconds) >= 0);
    }
private:
    int fd_{-1};
};
