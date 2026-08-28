#include <cstdint>
#include <span>
#include <expected>
#include <system_error>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

struct SensorReading {
    uint8_t high;
    uint8_t low;
};

/* Зчитування показів 10-бітного датчика з використанням сучасних безпечних типів C++ */
std::expected<SensorReading, std::error_code> readSensor10Bit(
    int fd,
    uint16_t addr10,
    uint8_t reg
) noexcept {
    uint8_t reg_addr = reg;
    uint8_t buffer[2] = {0, 0};

    struct i2c_msg msgs[2]{};

    msgs[0].addr  = addr10;
    msgs[0].flags = I2C_M_TEN;
    msgs[0].len   = 1;
    msgs[0].buf   = &reg_addr;

    msgs[1].addr  = addr10;
    msgs[1].flags = I2C_M_TEN | I2C_M_RD;
    msgs[1].len   = 2;
    msgs[1].buf   = buffer;

    struct i2c_rdwr_ioctl_data rdwr{};
    rdwr.msgs  = msgs;
    rdwr.nmsgs = 2;

    if (::ioctl(fd, I2C_RDWR, &rdwr) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return SensorReading{buffer[0], buffer[1]};
}
