// inspect_devices.cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <array>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>

namespace {
constexpr const char* ProcPath = "/proc/device_inventory";
constexpr std::size_t ChunkSize = 128;

class FileDescriptor {
public:
	explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
	~FileDescriptor() {
		if (fd_ >= 0) {
			::close(fd_);
		}
	}

	FileDescriptor(const FileDescriptor&) = delete;
	FileDescriptor& operator=(const FileDescriptor&) = delete;

	[[nodiscard]] int get() const noexcept { return fd_; }
	[[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

private:
	int fd_{-1};
};
}

int main()
{
	FileDescriptor fd(::open(ProcPath, O_RDONLY));
	if (!fd.isValid()) {
		std::cerr << "Помилка відкриття " << ProcPath << ": "
		          << std::error_code(errno, std::generic_category()).message() << '\n';
		return EXIT_FAILURE;
	}

	std::cout << "=== 1. Читання перших 256 байтів ===\n";
	std::array<char, ChunkSize> buffer{};
	std::size_t totalBytesRead = 0;

	while (totalBytesRead < 256) {
		ssize_t bytes = ::read(fd.get(), buffer.data(), buffer.size() - 1);
		if (bytes <= 0) {
			break;
		}
		buffer[bytes] = '\0';
		std::cout.write(buffer.data(), bytes);
		totalBytesRead += bytes;
	}

	std::cout << "\n=== 2. Перевірка lseek: повернення на початок ===\n";
	if (::lseek(fd.get(), 0, SEEK_SET) == -1) {
		std::cerr << "Помилка lseek: "
		          << std::error_code(errno, std::generic_category()).message() << '\n';
		return EXIT_FAILURE;
	}

	ssize_t bytes = ::read(fd.get(), buffer.data(), buffer.size() - 1);
	if (bytes > 0) {
		buffer[bytes] = '\0';
		std::cout << "Перший рядок після lseek(0):\n" << buffer.data() << '\n';
	}

	return EXIT_SUCCESS;
}
