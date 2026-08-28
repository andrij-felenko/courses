#include <iostream>
#include <string>
#include <vector>
#include <array>
#include <cstdint>
#include <cstring>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>

// RAII обгортка для файлового дескриптора evdev
class EvdevDevice {
private:
    int fd_{-1};

public:
    explicit EvdevDevice(const std::string& path) {
        fd_ = ::open(path.c_str(), O_RDONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + path);
        }
    }

    ~EvdevDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    EvdevDevice(const EvdevDevice&) = delete;
    EvdevDevice& operator=(const EvdevDevice&) = delete;

    EvdevDevice(EvdevDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    EvdevDevice& operator=(EvdevDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    [[nodiscard]] std::uint32_t get_version() const {
        int version = 0;
        if (::ioctl(fd_, EVIOCGVERSION(&version)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка EVIOCGVERSION");
        }
        return static_cast<std::uint32_t>(version);
    }

    [[nodiscard]] ::input_id get_id() const {
        ::input_id id{};
        if (::ioctl(fd_, EVIOCGID(&id)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка EVIOCGID");
        }
        return id;
    }

    [[nodiscard]] std::string get_name() const {
        std::array<char, 256> buf{};
        if (::ioctl(fd_, EVIOCGNAME(buf.size()), buf.data()) < 0) {
            return "Невідомо";
        }
        return std::string(buf.data());
    }

    [[nodiscard]] std::vector<std::uint8_t> get_bitmask(int ev_type, std::size_t max_bytes) const {
        std::vector<std::uint8_t> mask(max_bytes, 0);
        if (::ioctl(fd_, EVIOCGBIT(ev_type, mask.size()), mask.data()) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка EVIOCGBIT");
        }
        return mask;
    }

    [[nodiscard]] ::input_absinfo get_abs_info(int axis) const {
        ::input_absinfo abs{};
        if (::ioctl(fd_, EVIOCGABS(axis), &abs) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка EVIOCGABS");
        }
        return abs;
    }
};

static bool check_bit(const std::vector<std::uint8_t>& mask, int bit) {
    std::size_t byte_idx = static_cast<std::size_t>(bit) / 8;
    if (byte_idx >= mask.size()) return false;
    return (mask[byte_idx] & (1U << (static_cast<std::size_t>(bit) % 8))) != 0;
}

int main(int argc, char* argv[]) {
    const std::string dev_path = (argc > 1) ? argv[1] : "/dev/input/event0";

    try {
        EvdevDevice dev(dev_path);

        auto ver = dev.get_version();
        std::cout << "Версія evdev API: "
                  << (ver >> 16) << "." << ((ver >> 8) & 0xff) << "." << (ver & 0xff) << "\n";

        auto id = dev.get_id();
        std::cout << "ID: Bus=0x" << std::hex << id.bustype
                  << " Vendor=0x" << id.vendor
                  << " Product=0x" << id.product
                  << " Version=0x" << id.version << std::dec << "\n";

        std::cout << "Назва: " << dev.get_name() << "\n";

        auto evbit = dev.get_bitmask(0, (EV_MAX / 8) + 1);
        std::cout << "Підтримувані типи подій:\n";
        if (check_bit(evbit, EV_KEY)) std::cout << "  - EV_KEY (Клавіші)\n";
        if (check_bit(evbit, EV_REL)) std::cout << "  - EV_REL (Відносні осі)\n";
        if (check_bit(evbit, EV_ABS)) std::cout << "  - EV_ABS (Абсолютні осі)\n";

        if (check_bit(evbit, EV_ABS)) {
            auto absbit = dev.get_bitmask(EV_ABS, (ABS_MAX / 8) + 1);
            if (check_bit(absbit, ABS_X)) {
                auto abs = dev.get_abs_info(ABS_X);
                std::cout << "Вісь ABS_X: min=" << abs.minimum
                          << ", max=" << abs.maximum
                          << ", fuzz=" << abs.fuzz
                          << ", flat=" << abs.flat << "\n";
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
