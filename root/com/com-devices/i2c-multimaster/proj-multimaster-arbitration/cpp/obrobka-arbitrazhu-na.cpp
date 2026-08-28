#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <chrono>
#include <thread>
#include <random>
#include <expected>
#include <span>
#include <cerrno>

/* Обробка втрати арбітражу I2C у Linux (C++) */
class LinuxI2cBus {
public:
    explicit LinuxI2cBus(int fd) : fd_{fd}, rng_{std::random_device{}()} {}

    [[nodiscard]] std::expected<void, int> transfer(std::span<i2c_msg> messages, int maxRetries = 5) {
        i2c_rdwr_ioctl_data packets{
            .msgs = messages.data(),
            .nmsgs = static_cast<__u32>(messages.size())
        };

        std::uniform_int_distribution<int> jitterDist(100, 600);

        for (int attempt = 0; attempt < maxRetries; ++attempt) {
            if (::ioctl(fd_, I2C_RDWR, &packets) >= 0) {
                return {};
            }

            if (errno == EAGAIN || errno == EBUSY) {
                /* Втрата арбітражу: неблокувальна пауза з джиттером */
                std::this_thread::sleep_for(std::chrono::microseconds(jitterDist(rng_)));
            } else {
                return std::unexpected(errno);
            }
        }
        return std::unexpected(ETIMEDOUT);
    }

private:
    int fd_{-1};
    std::mt19937 rng_;
};
