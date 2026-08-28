#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>
#include <sys/ioctl.h>
#include <array>
#include <cstdint>
#include <span>
#include <system_error>

namespace linux_sensor {

class LinuxI2cBurstReader {
public:
    explicit LinuxI2cBurstReader(int fd, uint8_t dev_addr) noexcept
        : fd_(fd), dev_addr_(dev_addr) {}

    [[nodiscard]] std::error_code bulk_read(uint8_t reg_addr, std::span<uint8_t> out_buf) noexcept {
        std::array<i2c_msg, 2> msgs{};

        // Запис адреси початкового регістра
        msgs[0].addr  = dev_addr_;
        msgs[0].flags = 0;
        msgs[0].len   = 1;
        msgs[0].buf   = &reg_addr;

        // Пакетне вичитування N байтів за допомогою Repeated Start
        msgs[1].addr  = dev_addr_;
        msgs[1].flags = I2C_M_RD;
        msgs[1].len   = static_cast<__u16>(out_buf.size());
        msgs[1].buf   = out_buf.data();

        i2c_rdwr_ioctl_data packets{};
        packets.msgs  = msgs.data();
        packets.nmsgs = static_cast<__u32>(msgs.size());

        if (ioctl(fd_, I2C_RDWR, &packets) < 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }

private:
    int     fd_{-1};
    uint8_t dev_addr_{0};
};

} // namespace linux_sensor
