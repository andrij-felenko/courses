#include <cstdint>
#include <cstring>
#include <string_view>
#include <span>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

class I2c10BitDevice {
public:
    explicit I2c10BitDevice(int fd) noexcept : fd_(fd) {}

    ~I2c10BitDevice() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    I2c10BitDevice(const I2c10BitDevice&) = delete;
    I2c10BitDevice& operator=(const I2c10BitDevice&) = delete;

    I2c10BitDevice(I2c10BitDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    I2c10BitDevice& operator=(I2c10BitDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    static std::expected<I2c10BitDevice, std::error_code> open(std::string_view bus_path) noexcept {
        int fd = ::open(bus_path.data(), O_RDWR);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        unsigned long funcs = 0;
        if (::ioctl(fd, I2C_FUNCS, &funcs) < 0) {
            int err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        if (!(funcs & I2C_FUNC_10BIT_ADDR) || !(funcs & I2C_FUNC_I2C)) {
            ::close(fd);
            return std::unexpected(std::make_error_code(std::errc::not_supported));
        }

        return I2c10BitDevice(fd);
    }

    std::expected<void, std::error_code> write(uint16_t addr10, std::span<const uint8_t> data) const noexcept {
        struct i2c_msg msg{};
        msg.addr  = addr10;
        msg.flags = I2C_M_TEN;
        msg.len   = static_cast<__u16>(data.size());
        msg.buf   = const_cast<__u8*>(data.data());

        struct i2c_rdwr_ioctl_data rdwr{};
        rdwr.msgs  = &msg;
        rdwr.nmsgs = 1;

        if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

    std::expected<void, std::error_code> readRegister(
        uint16_t addr10,
        uint8_t reg_addr,
        std::span<uint8_t> out_buf
    ) const noexcept {
        struct i2c_msg msgs[2]{};

        msgs[0].addr  = addr10;
        msgs[0].flags = I2C_M_TEN;
        msgs[0].len   = 1;
        msgs[0].buf   = &reg_addr;

        msgs[1].addr  = addr10;
        msgs[1].flags = I2C_M_TEN | I2C_M_RD;
        msgs[1].len   = static_cast<__u16>(out_buf.size());
        msgs[1].buf   = out_buf.data();

        struct i2c_rdwr_ioctl_data rdwr{};
        rdwr.msgs  = msgs;
        rdwr.nmsgs = 2;

        if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

private:
    int fd_{-1};
};
