#include <iostream>
#include <cstdint>
#include <expected>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>

namespace smbus_client {

class SmbusDevice {
public:
    explicit SmbusDevice(const char* device_path, uint8_t slave_addr) {
        m_fd = ::open(device_path, O_RDWR);
        if (m_fd >= 0) {
            ::ioctl(m_fd, I2C_SLAVE, slave_addr);
            ::ioctl(m_fd, I2C_PEC, 1); // Увімкнути PEC
        }
    }

    ~SmbusDevice() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }

    [[nodiscard]] bool is_valid() const noexcept {
        return m_fd >= 0;
    }

    [[nodiscard]] std::expected<uint16_t, int> read_word(uint8_t command) const noexcept {
        if (m_fd < 0) return std::unexpected(-1);

        i2c_smbus_data data{};
        i2c_smbus_ioctl_data args{
            .read_write = I2C_SMBUS_READ,
            .command = command,
            .size = I2C_SMBUS_WORD_DATA,
            .data = &data
        };

        if (::ioctl(m_fd, I2C_SMBUS, &args) < 0) {
            return std::unexpected(errno);
        }
        return data.word;
    }

private:
    int m_fd{-1};
};

} // namespace smbus_client

int main() {
    smbus_client::SmbusDevice battery{"/dev/i2c-0", 0x0B};
    if (!battery.is_valid()) {
        std::cerr << "Помилка доступу до шини SMBus\n";
        return 1;
    }

    auto voltage = battery.read_word(0x09);
    if (voltage) {
        std::cout << "Напруга акумулятора: " << *voltage << " мВ\n";
    } else {
        std::cerr << "Помилка читання напруги (помилка PEC або відсутність відповіді)\n";
    }
    return 0;
}
