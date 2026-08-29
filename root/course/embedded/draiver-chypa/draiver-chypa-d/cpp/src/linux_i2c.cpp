#include "accel/linux_i2c.hpp"

#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>
#include <utility>

namespace accel {
namespace {

// Найдовший запис драйвера — байт адреси регістру плюс дані конфігурації.
constexpr std::size_t kWriteFrameMax = 32;

} // namespace

Result<LinuxI2cBus> LinuxI2cBus::open(const std::string &devicePath, std::uint8_t address) noexcept
{
    const int fd = ::open(devicePath.c_str(), O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        return std::unexpected(Status::CommFail);
    }
    return LinuxI2cBus{fd, address};
}

LinuxI2cBus::LinuxI2cBus(LinuxI2cBus &&other) noexcept
    : fd_(std::exchange(other.fd_, -1)), address_(other.address_)
{
}

LinuxI2cBus &LinuxI2cBus::operator=(LinuxI2cBus &&other) noexcept
{
    if (this != &other) {
        closeDescriptor();
        fd_ = std::exchange(other.fd_, -1);
        address_ = other.address_;
    }
    return *this;
}

LinuxI2cBus::~LinuxI2cBus()
{
    closeDescriptor();
}

void LinuxI2cBus::closeDescriptor() noexcept
{
    if (fd_ >= 0) {
        ::close(fd_);
        fd_ = -1;
    }
}

// Адреса регістру йде окремим повідомленням без умови STOP, далі повторний
// старт і читання: ядро формує Repeated Start саме між двома msg одного
// ioctl(I2C_RDWR). Пара STOP → START тут була б помилкою — на мультимастерній
// шині керування міг би перехопити інший ведучий.
Result<void> LinuxI2cBus::read(std::uint8_t reg, std::span<std::uint8_t> rx) noexcept
{
    if (fd_ < 0 || rx.empty()) {
        return std::unexpected(Status::InvalidParam);
    }

    std::uint8_t regAddress = reg;
    std::array<i2c_msg, 2> messages{};
    messages[0].addr = address_;
    messages[0].flags = 0;
    messages[0].len = 1;
    messages[0].buf = &regAddress;

    messages[1].addr = address_;
    messages[1].flags = I2C_M_RD;
    messages[1].len = static_cast<std::uint16_t>(rx.size());
    messages[1].buf = rx.data();

    i2c_rdwr_ioctl_data transfer{};
    transfer.msgs = messages.data();
    transfer.nmsgs = static_cast<std::uint32_t>(messages.size());

    if (::ioctl(fd_, I2C_RDWR, &transfer) < 0) {
        return std::unexpected(Status::CommFail);
    }
    return {};
}

Result<void> LinuxI2cBus::write(std::uint8_t reg, std::span<const std::uint8_t> tx) noexcept
{
    if (fd_ < 0 || tx.empty() || tx.size() + 1 > kWriteFrameMax) {
        return std::unexpected(Status::InvalidParam);
    }

    std::array<std::uint8_t, kWriteFrameMax> frame{};
    frame[0] = reg;
    std::memcpy(frame.data() + 1, tx.data(), tx.size());

    i2c_msg message{};
    message.addr = address_;
    message.flags = 0;
    message.len = static_cast<std::uint16_t>(tx.size() + 1);
    message.buf = frame.data();

    i2c_rdwr_ioctl_data transfer{};
    transfer.msgs = &message;
    transfer.nmsgs = 1;

    if (::ioctl(fd_, I2C_RDWR, &transfer) < 0) {
        return std::unexpected(Status::CommFail);
    }
    return {};
}

void LinuxI2cBus::delay(std::chrono::milliseconds pause) noexcept
{
    if (pause.count() <= 0) {
        return;
    }

    timespec request{};
    request.tv_sec = static_cast<time_t>(pause.count() / 1000);
    request.tv_nsec = static_cast<long>(pause.count() % 1000) * 1000000L;

    // nanosleep уміє повернутися раніше через сигнал — досипаємо залишок.
    timespec remaining{};
    while (::nanosleep(&request, &remaining) != 0 && errno == EINTR) {
        request = remaining;
    }
}

} // namespace accel
