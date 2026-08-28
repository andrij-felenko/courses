#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <cstdint>
#include <string_view>
#include <system_error>

class LinuxSpidev {
public:
    enum class Mode : uint8_t {
        Mode0 = SPI_MODE_0,
        Mode1 = SPI_MODE_1,
        Mode2 = SPI_MODE_2,
        Mode3 = SPI_MODE_3
    };

    explicit LinuxSpidev(std::string_view path, Mode mode) {
        fd_ = ::open(path.data(), O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити пристрій spidev");
        }

        uint8_t raw_mode = static_cast<uint8_t>(mode);
        if (::ioctl(fd_, SPI_IOC_WR_MODE, &raw_mode) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Помилка встановлення режиму SPI_IOC_WR_MODE");
        }
    }

    ~LinuxSpidev() {
        if (fd_ >= 0) ::close(fd_);
    }

    int native_handle() const noexcept { return fd_; }

private:
    int fd_{-1};
};
