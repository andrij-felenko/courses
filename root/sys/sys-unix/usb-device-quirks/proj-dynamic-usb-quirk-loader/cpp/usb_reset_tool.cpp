// usb_reset_tool.cpp — Скидання USB-пристрою (ідіоматичний C++20 з RAII)
#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/usbdevice_fs.h>

namespace fs = std::filesystem;

class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { if (fd_ >= 0) ::close(fd_); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_;
};

struct UsbDeviceId {
    uint16_t vid;
    uint16_t pid;
};

class UsbResetter {
public:
    static std::expected<void, std::string> reset_device(UsbDeviceId target) {
        const fs::path usb_base{"/dev/bus/usb"};
        if (!fs::exists(usb_base)) {
            return std::unexpected("Каталог /dev/bus/usb не знайдено в системі");
        }

        for (const auto& bus_entry : fs::directory_iterator(usb_base)) {
            if (!bus_entry.is_directory()) continue;

            for (const auto& dev_entry : fs::directory_iterator(bus_entry.path())) {
                if (!dev_entry.is_character_file()) continue;

                ScopedFd dev_fd{::open(dev_entry.path().c_str(), O_RDWR)};
                if (!dev_fd.valid()) continue;

                std::vector<uint8_t> desc(18);
                ssize_t bytes_read = ::read(dev_fd.get(), desc.data(), desc.size());
                if (bytes_read == static_cast<ssize_t>(desc.size())) {
                    uint16_t vid = static_cast<uint16_t>(desc[8] | (desc[9] << 8));
                    uint16_t pid = static_cast<uint16_t>(desc[10] | (desc[11] << 8));

                    if (vid == target.vid && pid == target.pid) {
                        std::cout << "Знайдено пристрій [" << std::hex << vid << ":" << pid
                                  << "] на шляху: " << dev_entry.path() << std::dec << "\n";
                        std::cout << "Виконання запиту USBDEVFS_RESET...\n";

                        if (::ioctl(dev_fd.get(), USBDEVFS_RESET, 0) < 0) {
                            return std::unexpected(std::string("Помилка ioctl USBDEVFS_RESET: ") + 
                                                   std::generic_category().message(errno));
                        }

                        std::cout << "Скидання порту успішно виконано.\n";
                        return {};
                    }
                }
            }
        }
        return std::unexpected("Пристрій із вказаними VID:PID не знайдено");
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <VID_hex> <PID_hex>\n"
                  << "Приклад: " << argv[0] << " 04b4 8613\n";
        return 1;
    }

    try {
        uint16_t vid = static_cast<uint16_t>(std::stoul(argv[1], nullptr, 16));
        uint16_t pid = static_cast<uint16_t>(std::stoul(argv[2], nullptr, 16));

        auto result = UsbResetter::reset_device({vid, pid});
        if (!result.has_value()) {
            std::cerr << "Збій: " << result.error() << "\n";
            return 1;
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка аргументів: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
