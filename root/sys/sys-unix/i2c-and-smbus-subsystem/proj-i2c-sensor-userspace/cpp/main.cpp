#include <iostream>
#include <vector>
#include <span>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* RAII-обгортка дескриптора I2C-адаптера */
class I2cBus {
public:
	explicit I2cBus(const std::string& dev_node) {
		fd_ = ::open(dev_node.c_str(), O_RDWR);
		if (fd_ < 0) {
			throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити I2C вузол");
		}

		unsigned long funcs = 0;
		if (::ioctl(fd_, I2C_FUNCS, &funcs) < 0) {
			::close(fd_);
			throw std::system_error(errno, std::generic_category(), "Помилка запиту I2C_FUNCS");
		}

		if (!(funcs & I2C_FUNC_I2C)) {
			::close(fd_);
			throw std::runtime_error("Адаптер не підтримує сирі I2C-транзакції");
		}
	}

	~I2cBus() noexcept {
		if (fd_ >= 0) {
			::close(fd_);
		}
	}

	I2cBus(const I2cBus&) = delete;
	I2cBus& operator=(const I2cBus&) = delete;
	I2cBus(I2cBus&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
	I2cBus& operator=(I2cBus&& other) noexcept {
		if (this != &other) {
			if (fd_ >= 0) ::close(fd_);
			fd_ = other.fd_;
			other.fd_ = -1;
		}
		return *this;
	}

	/* Атомарне читання регістрів через Repeated START */
	void read_registers(uint16_t addr, uint8_t reg, std::span<uint8_t> out_buf) const {
		uint8_t target_reg = reg;
		struct i2c_msg msgs[2];
		struct i2c_rdwr_ioctl_data rdwr;

		msgs[0].addr  = addr;
		msgs[0].flags = 0;
		msgs[0].len   = 1;
		msgs[0].buf   = &target_reg;

		msgs[1].addr  = addr;
		msgs[1].flags = I2C_M_RD;
		msgs[1].len   = static_cast<__u16>(out_buf.size());
		msgs[1].buf   = out_buf.data();

		rdwr.msgs  = msgs;
		rdwr.nmsgs = 2;

		if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
			throw std::system_error(errno, std::generic_category(), "Помилка I2C_RDWR читання");
		}
	}

	/* Запис байта в регістр */
	void write_register(uint16_t addr, uint8_t reg, uint8_t val) const {
		uint8_t buf[2] = { reg, val };
		struct i2c_msg msg;
		struct i2c_rdwr_ioctl_data rdwr;

		msg.addr  = addr;
		msg.flags = 0;
		msg.len   = 2;
		msg.buf   = buf;

		rdwr.msgs  = &msg;
		rdwr.nmsgs = 1;

		if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
			throw std::system_error(errno, std::generic_category(), "Помилка I2C_RDWR запису");
		}
	}

private:
	int fd_{-1};
};

int main() {
	constexpr const char* dev_path = "/dev/i2c-1";
	constexpr uint16_t bmp280_addr = 0x76;
	constexpr uint8_t reg_id       = 0xD0;
	constexpr uint8_t reg_ctrl     = 0xF4;
	constexpr uint8_t reg_data     = 0xF7;

	try {
		I2cBus bus(dev_path);

		uint8_t chip_id = 0;
		bus.read_registers(bmp280_addr, reg_id, std::span(&chip_id, 1));
		std::cout << "Зчитано Chip ID: 0x" << std::hex << static_cast<int>(chip_id) << std::dec << "\n";

		/* Normal Mode, передискретизація температури x2, тиску x16 */
		bus.write_register(bmp280_addr, reg_ctrl, 0x57);

		::usleep(50000);

		std::vector<uint8_t> raw_data(6);
		bus.read_registers(bmp280_addr, reg_data, std::span(raw_data));

		int32_t raw_press = (raw_data[0] << 12) | (raw_data[1] << 4) | (raw_data[2] >> 4);
		int32_t raw_temp  = (raw_data[3] << 12) | (raw_data[4] << 4) | (raw_data[5] >> 4);

		std::cout << "Сирі показники сенсора: Температура = " << raw_temp
		          << ", Тиск = " << raw_press << "\n";

	} catch (const std::exception& ex) {
		std::cerr << "Критична помилка: " << ex.what() << "\n";
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}
