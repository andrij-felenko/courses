#include "linux_i2c.hpp"

#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <cerrno>
#include <system_error>
#include <utility>

namespace sht3x {

LinuxI2c::LinuxI2c(const std::string& bus_path, std::uint8_t address7)
{
    fd_ = ::open(bus_path.c_str(), O_RDWR | O_CLOEXEC);
    if (fd_ < 0) {
        throw std::system_error(errno, std::generic_category(),
                                "не відкривається шина " + bus_path);
    }

    // Ядро саме зсуне 7-бітну адресу й додасть біт напрямку.
    if (::ioctl(fd_, I2C_SLAVE, static_cast<unsigned long>(address7)) < 0) {
        const int saved = errno;
        close_fd();
        throw std::system_error(saved, std::generic_category(),
                                "адреса на шині недоступна");
    }
}

LinuxI2c::~LinuxI2c()
{
    close_fd();
}

LinuxI2c::LinuxI2c(LinuxI2c&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}

LinuxI2c& LinuxI2c::operator=(LinuxI2c&& other) noexcept
{
    if (this != &other) {
        close_fd();
        fd_ = std::exchange(other.fd_, -1);
    }
    return *this;
}

void LinuxI2c::close_fd() noexcept
{
    if (fd_ >= 0) {
        ::close(fd_);
        fd_ = -1;
    }
}

bool LinuxI2c::write(std::span<const std::uint8_t> tx) noexcept
{
    // Транзакція I2C неподільна: або пройшли всі байти, або жоден.
    // Перерваний сигналом виклик (EINTR) повторюємо, це не помилка шини.
    for (;;) {
        const ssize_t n = ::write(fd_, tx.data(), tx.size());
        if (n == static_cast<ssize_t>(tx.size())) {
            return true;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        return false;  // NACK від сенсора приходить сюди як EREMOTEIO
    }
}

bool LinuxI2c::read(std::span<std::uint8_t> rx) noexcept
{
    for (;;) {
        const ssize_t n = ::read(fd_, rx.data(), rx.size());
        if (n == static_cast<ssize_t>(rx.size())) {
            return true;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        return false;
    }
}

}  // namespace sht3x
