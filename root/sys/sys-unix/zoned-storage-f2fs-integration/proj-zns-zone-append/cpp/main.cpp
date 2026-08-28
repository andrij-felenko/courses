#include <iostream>
#include <vector>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cstdint>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

// RAII обгортка для безпечного керування файловим дескриптором ZNS пристрою
class ZnsDevice {
    int fd_{-1};

public:
    explicit ZnsDevice(const char* path) {
        fd_ = ::open(path, O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити ZNS пристрій");
        }
    }

    ~ZnsDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Забороняємо копіювання файлового дескриптора (Rule of Five)
    ZnsDevice(const ZnsDevice&) = delete;
    ZnsDevice& operator=(const ZnsDevice&) = delete;

    // Дозволяємо переміщення (Move semantics)
    ZnsDevice(ZnsDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    ZnsDevice& operator=(ZnsDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    // Безпечне отримання звіту про стан зони з виділенням векторного буфера
    [[nodiscard]] blk_zone get_zone_info(std::uint64_t start_sector) const {
        std::size_t rep_size = sizeof(blk_zone_report) + sizeof(blk_zone);
        std::vector<std::uint8_t> buffer(rep_size, 0);

        auto* rep = reinterpret_cast<blk_zone_report*>(buffer.data());
        rep->sector = start_sector;
        rep->nr_zones = 1;

        if (::ioctl(fd_, BLKREPORTZONE, rep) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(BLKREPORTZONE)");
        }

        if (rep->nr_zones == 0) {
            throw std::runtime_error("Зону за вказаним сектором не знайдено");
        }

        return rep->zones[0];
    }

    // Виконання апаратного скидання зони (BLKRESETZONE)
    void reset_zone(std::uint64_t start_sector, std::uint64_t sector_count) {
        blk_zone_range range{};
        range.sector = start_sector;
        range.nr_sectors = sector_count;

        if (::ioctl(fd_, BLKRESETZONE, &range) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(BLKRESETZONE)");
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " /dev/nvmeXnY\n";
        return 1;
    }

    try {
        ZnsDevice dev(argv[1]);

        std::cout << "=== Стан зони ДО скидання ===\n";
        auto z1 = dev.get_zone_info(0);
        std::cout << "Зона від сектора " << z1.start
                  << ": довжина=" << z1.len
                  << ", WP=" << z1.wp
                  << ", стан=0x" << std::hex << static_cast<unsigned int>(z1.cond) << std::dec << "\n";

        std::cout << "\nНадсилання команди BLKRESETZONE...\n";
        dev.reset_zone(0, 524288);

        std::cout << "\n=== Стан зони ПІСЛЯ скидання ===\n";
        auto z2 = dev.get_zone_info(0);
        std::cout << "Зона від сектора " << z2.start
                  << ": довжина=" << z2.len
                  << ", WP=" << z2.wp << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Виняток системи: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
