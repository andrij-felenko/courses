// i3c_user_app.cpp - Приклад користувацької програми на ідіоматичному C++20
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/types.h>

struct i3c_ioc_priv_xfer {
	uint16_t len;
	uint8_t rnw;
	uint8_t pad;
	uint64_t data;
};

#define I3C_IOC_MAGIC 'I'
#define I3C_IOC_PRIV_XFER(n) _IOC(_IOC_WRITE, I3C_IOC_MAGIC, 0x01, (n) * sizeof(struct i3c_ioc_priv_xfer))

// RAII обгортка для файлового дескриптора Linux
class ScopedFd {
public:
	explicit ScopedFd(const char* path, int flags) 
		: fd_(::open(path, flags)) {}

	~ScopedFd() {
		if (fd_ >= 0) ::close(fd_);
	}

	[[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
	[[nodiscard]] int get() const noexcept { return fd_; }

	ScopedFd(const ScopedFd&) = delete;
	ScopedFd& operator=(const ScopedFd&) = delete;

private:
	int fd_{-1};
};

int main()
{
	ScopedFd dev("/dev/i3c-0", O_RDWR);
	if (!dev.valid()) {
		std::cerr << "Помилка відкриття символьного пристрою I3C\n";
		return 1;
	}

	uint8_t reg_addr = 0x0A;
	std::array<uint8_t, 4> read_buf{};

	std::array<i3c_ioc_priv_xfer, 2> xfers{{
		{
			.len = 1,
			.rnw = 0,
			.pad = 0,
			.data = reinterpret_cast<uint64_t>(&reg_addr)
		},
		{
			.len = static_cast<uint16_t>(read_buf.size()),
			.rnw = 1,
			.pad = 0,
			.data = reinterpret_cast<uint64_t>(read_buf.data())
		}
	}};

	if (::ioctl(dev.get(), I3C_IOC_PRIV_XFER(xfers.size()), xfers.data()) < 0) {
		std::cerr << "Помилка ioctl виконання транзакції I3C\n";
		return 2;
	}

	std::cout << "Прочитано байтів: ";
	for (auto byte : read_buf) {
		std::cout << "0x" << std::hex << static_cast<int>(byte) << " ";
	}
	std::cout << "\n";

	return 0;
}
