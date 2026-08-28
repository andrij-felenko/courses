#include <linux/spi/spidev.h>
#include <sys/ioctl.h>
#include <cstdint>
#include <span>
#include <expected>
#include <unistd.h>

class SpiUserDevice {
public:
    enum class Error { IoctlFailed, InvalidBuffer };

    explicit SpiUserDevice(int fd) : fd_(fd) {}

    [[nodiscard]] std::expected<void, Error> transfer(
        std::span<const uint8_t> tx,
        std::span<uint8_t> rx,
        uint32_t speedHz = 25'000'000
    ) const noexcept {
        if (tx.size() != rx.size() || tx.empty()) {
            return std::unexpected(Error::InvalidBuffer);
        }

        spi_ioc_transfer tr{};
        tr.tx_buf = reinterpret_cast<unsigned long>(tx.data());
        tr.rx_buf = reinterpret_cast<unsigned long>(rx.data());
        tr.len = static_cast<uint32_t>(tx.size());
        tr.speed_hz = speedHz;
        tr.bits_per_word = 8;
        tr.cs_change = 0;

        if (ioctl(fd_, SPI_IOC_MESSAGE(1), &tr) < 0) {
            return std::unexpected(Error::IoctlFailed);
        }
        return {};
    }

private:
    int fd_{-1};
};
