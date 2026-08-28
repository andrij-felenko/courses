#include <iostream>
#include <vector>
#include <cstdint>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

class I2c10BitScanner {
public:
    static std::vector<uint16_t> scan(int fd) noexcept {
        std::vector<uint16_t> foundDevices;
        foundDevices.reserve(16);

        for (uint16_t addr = 0x008; addr <= 0x3F7; ++addr) {
            struct i2c_msg msg{};
            msg.addr  = addr;
            msg.flags = I2C_M_TEN;
            msg.len   = 0;
            msg.buf   = nullptr;

            struct i2c_rdwr_ioctl_data rdwr{};
            rdwr.msgs  = &msg;
            rdwr.nmsgs = 1;

            if (::ioctl(fd, I2C_RDWR, &rdwr) >= 0) {
                foundDevices.push_back(addr);
            }
        }
        return foundDevices;
    }
};
