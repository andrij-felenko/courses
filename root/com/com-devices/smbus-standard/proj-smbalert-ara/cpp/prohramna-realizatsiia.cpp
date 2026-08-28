#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <cstdint>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>

class SmbusController {
public:
    static constexpr uint8_t ARA_ADDRESS = 0x0C;
    static constexpr uint8_t CRC8_POLY   = 0x07;

    explicit SmbusController(const std::string& dev_path) {
        fd_ = ::open(dev_path.c_str(), O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити адаптер I2C");
        }
    }

    ~SmbusController() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SmbusController(const SmbusController&) = delete;
    SmbusController& operator=(const SmbusController&) = delete;

    SmbusController(SmbusController&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    SmbusController& operator=(SmbusController&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    /* Обчислення контрольної суми PEC на основі span байтів */
    [[nodiscard]] static constexpr uint8_t calculate_pec(std::span<const uint8_t> data) noexcept {
        uint8_t crc = 0x00;
        for (uint8_t byte_val : data) {
            crc ^= byte_val;
            for (int bit = 0; bit < 8; ++bit) {
                if (crc & 0x80) {
                    crc = static_cast<uint8_t>((crc << 1) ^ CRC8_POLY);
                } else {
                    crc = static_cast<uint8_t>(crc << 1);
                }
            }
        }
        return crc;
    }

    /* Зчитування адреси ініціатора сповіщення через Alert Response Address */
    [[nodiscard]] std::expected<uint8_t, int> poll_alert_response() const noexcept {
        uint8_t raw_addr = 0;
        i2c_msg msg{};
        msg.addr = ARA_ADDRESS;
        msg.flags = I2C_M_RD;
        msg.len = 1;
        msg.buf = &raw_addr;

        i2c_rdwr_ioctl_data rdwr_data{};
        rdwr_data.msgs = &msg;
        rdwr_data.nmsgs = 1;

        if (::ioctl(fd_, I2C_RDWR, &rdwr_data) < 0) {
            return std::unexpected(errno);
        }

        /* 7-бітна адреса видобувається зсувом бітів 7:1 */
        return static_cast<uint8_t>(raw_addr >> 1);
    }

    /* Повне обслуговування черги сповіщень */
    void process_active_alerts() const {
        size_t handled = 0;
        while (auto alert = poll_alert_response()) {
            ++handled;
            uint8_t slave = *alert;
            std::cout << "[SMBALERT++] Отримано тривогу від веденого чипа 0x"
                      << std::hex << static_cast<int>(slave) << std::dec << '\n';

            dispatch_alert(slave);

            if (handled > 32) {
                std::cerr << "[ПОМИЛКА] Зависання лінії переривань SMBALERT#!\n";
                break;
            }
        }
    }

private:
    int fd_{-1};

    static void dispatch_alert(uint8_t slave_addr) noexcept {
        switch (slave_addr) {
            case 0x16:
                std::cout << " -> Аварія BMS: зафіксовано небезпечну зміну параметрів батареї.\n";
                break;
            case 0x24:
                std::cout << " -> Телеметрія PMBus: спрацював компаратор захисту OVP/OCP.\n";
                break;
            case 0x48:
                std::cout << " -> Аварійне охолодження: термодавач зафіксував перегрів кристала!\n";
                break;
            default:
                std::cout << " -> Невідомий ведений пристрій: 0x"
                          << std::hex << static_cast<int>(slave_addr) << std::dec << '\n';
                break;
        }
    }
};
