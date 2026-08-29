#include "linux_i2c.hpp"

#include <cerrno>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>
#include <sys/ioctl.h>
#include <unistd.h>

namespace atecc {
namespace {

// I2C_RDWR, а не звичайні read/write: він дозволяє задати адресу для кожного
// повідомлення окремо — саме це потрібно для запису на адресу 0x00, якою
// драйвер виготовляє імпульс пробудження.
bool transfer(int fd, std::uint8_t address, std::uint8_t* buffer, std::size_t length,
              std::uint16_t flags)
{
    i2c_msg message{
        .addr = address,
        .flags = flags,
        .len = static_cast<std::uint16_t>(length),
        .buf = buffer,
    };
    i2c_rdwr_ioctl_data request{
        .msgs = &message,
        .nmsgs = 1,
    };

    while (::ioctl(fd, I2C_RDWR, &request) < 0) {
        if (errno == EINTR) {
            continue;
        }
        // ENXIO/EREMOTEIO — пристрій не підтвердив адресу; для крипточипа це
        // штатне «ще рахую», тож винятку тут не місце.
        return false;
    }
    return true;
}

} // namespace

LinuxI2cBus::LinuxI2cBus(std::string_view devicePath)
{
    fd_ = ::open(std::string(devicePath).c_str(), O_RDWR);
    if (fd_ < 0) {
        throw std::system_error(errno, std::generic_category(),
                                "не вдалося відкрити " + std::string(devicePath));
    }
}

LinuxI2cBus::~LinuxI2cBus()
{
    if (fd_ >= 0) {
        ::close(fd_);
    }
}

LinuxI2cBus::LinuxI2cBus(LinuxI2cBus&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}

LinuxI2cBus& LinuxI2cBus::operator=(LinuxI2cBus&& other) noexcept
{
    if (this != &other) {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = std::exchange(other.fd_, -1);
    }
    return *this;
}

bool LinuxI2cBus::write(std::uint8_t address, std::span<const std::uint8_t> data)
{
    // ioctl бере не-const покажчик, тож пакет доводиться скопіювати.
    std::vector<std::uint8_t> scratch(data.begin(), data.end());
    return transfer(fd_, address, scratch.data(), scratch.size(), 0);
}

bool LinuxI2cBus::read(std::uint8_t address, std::span<std::uint8_t> data)
{
    return transfer(fd_, address, data.data(), data.size(), I2C_M_RD);
}

} // namespace atecc
