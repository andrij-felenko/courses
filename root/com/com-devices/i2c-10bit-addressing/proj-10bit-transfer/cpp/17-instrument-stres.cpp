#include <iostream>
#include <cstdint>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

class I2cStressTester {
public:
    struct TestResult {
        int totalIterations;
        int failedIterations;
        double errorRatePercent;
    };

    static TestResult run(int fd, uint16_t addr10, int iterations) noexcept {
        int errors = 0;
        uint8_t reg = 0x00;
        uint8_t val = 0;

        for (int i = 0; i < iterations; ++i) {
            struct i2c_msg msgs[2]{};
            msgs[0].addr  = addr10;
            msgs[0].flags = I2C_M_TEN;
            msgs[0].len   = 1;
            msgs[0].buf   = &reg;

            msgs[1].addr  = addr10;
            msgs[1].flags = I2C_M_TEN | I2C_M_RD;
            msgs[1].len   = 1;
            msgs[1].buf   = &val;

            struct i2c_rdwr_ioctl_data rdwr{};
            rdwr.msgs  = msgs;
            rdwr.nmsgs = 2;

            if (::ioctl(fd, I2C_RDWR, &rdwr) < 0) {
                errors++;
            }
            ::usleep(1000);
        }

        double rate = (static_cast<double>(errors) * 100.0) / static_cast<double>(iterations);
        return TestResult{iterations, errors, rate};
    }
};
