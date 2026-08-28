#include <iostream>
#include <fstream>
#include <filesystem>
#include <system_error>
#include <string_view>
#include <expected>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

/*
 * RAII-обгортка для управління дескриптором PM QoS (/dev/cpu_dma_latency).
 * Автоматично вивільняє ресурси та знімає обмеження C-станів при виході з області видимості.
 */
class pm_qos_latency_lock {
public:
    explicit pm_qos_latency_lock(std::int32_t target_latency_us) {
        fd_ = ::open("/dev/cpu_dma_latency", O_WRONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити /dev/cpu_dma_latency");
        }

        if (::write(fd_, &target_latency_us, sizeof(target_latency_us)) != sizeof(target_latency_us)) {
            ::close(fd_);
            fd_ = -1;
            throw std::system_error(errno, std::generic_category(), "Помилка запису в PM QoS");
        }

        std::cout << "[PM QoS RAII] Фіксація затримки на " << target_latency_us << " мкс активована.\n";
    }

    ~pm_qos_latency_lock() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            std::cout << "[PM QoS RAII] Дескриптор закрито, обмеження C-станів знято.\n";
        }
    }

    pm_qos_latency_lock(const pm_qos_latency_lock&) = delete;
    pm_qos_latency_lock& operator=(const pm_qos_latency_lock&) = delete;

    pm_qos_latency_lock(pm_qos_latency_lock&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    pm_qos_latency_lock& operator=(pm_qos_latency_lock&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

private:
    int fd_{-1};
};

/* Клас для керування політиками cpufreq через std::filesystem та iostreams */
class cpufreq_manager {
public:
    static std::expected<void, std::string> set_governor(std::size_t cpu_index, std::string_view governor) {
        fs::path path = fs::path("/sys/devices/system/cpu") / ("cpu" + std::to_string(cpu_index)) / "cpufreq/scaling_governor";

        if (!fs::exists(path)) {
            return std::unexpected("Шлях sysfs не існує: " + path.string());
        }

        std::ofstream sysfs_file(path);
        if (!sysfs_file.is_open()) {
            return std::unexpected("Помилка відкриття файлу для запису: " + path.string());
        }

        sysfs_file << governor;
        if (sysfs_file.fail()) {
            return std::unexpected("Помилка запису регулятора у sysfs");
        }

        std::cout << "[cpufreq C++] Регулятор для CPU " << cpu_index << " змінено на: " << governor << "\n";
        return {};
    }
};

int main() {
    std::cout << "=== Налаштування параметрів живлення та затримок CPU (C++23 API) ===\n";

    /* 1. Встановлюємо регулятор performance через C++ manager */
    auto result = cpufreq_manager::set_governor(0, "performance");
    if (!result) {
        std::cerr << "Помилка cpufreq: " << result.error() << "\n";
    }

    try {
        /* 2. Створюємо RAII-об'єкт фіксації затримки PM QoS */
        pm_qos_latency_lock qos_lock(0);

        std::cout << "Виконання високонавантаженої обчислювальної задачі без затримок...\n";
        ::sleep(2);

    } catch (const std::exception& ex) {
        std::cerr << "Виняток PM QoS: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
