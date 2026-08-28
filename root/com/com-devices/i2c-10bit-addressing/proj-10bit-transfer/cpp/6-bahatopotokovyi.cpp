#include <mutex>
#include <span>
#include <vector>
#include <expected>
#include <system_error>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

class ThreadSafeI2cBus {
public:
    explicit ThreadSafeI2cBus(int fd) noexcept : fd_(fd) {}

    std::expected<void, std::error_code> transfer(std::span<struct i2c_msg> msgs) noexcept {
        std::lock_guard<std::mutex> lock(mutex_);

        struct i2c_rdwr_ioctl_data rdwr{};
        rdwr.msgs  = msgs.data();
        rdwr.nmsgs = static_cast<__u32>(msgs.size());

        if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

private:
    int fd_{-1};
    std::mutex mutex_;
};
