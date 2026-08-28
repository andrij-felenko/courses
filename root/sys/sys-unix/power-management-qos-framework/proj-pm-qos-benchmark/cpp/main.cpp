#include <iostream>
#include <fstream>
#include <system_error>
#include <string_view>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>

namespace pm_qos {

// RAII обгортка для безпечного керування дескриптором CPU Latency QoS
class CpuLatencyLock {
public:
    explicit CpuLatencyLock(std::int32_t target_latency_us) {
        fd_ = ::open(device_path_.data(), O_WRONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Failed to open " + std::string(device_path_));
        }

        if (::write(fd_, &target_latency_us, sizeof(target_latency_us)) != sizeof(target_latency_us)) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(),
                                    "Failed to write target latency to " + std::string(device_path_));
        }
    }

    ~CpuLatencyLock() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання для запобігання подвійному закриттю дескриптора
    CpuLatencyLock(const CpuLatencyLock&) = delete;
    CpuLatencyLock& operator=(const CpuLatencyLock&) = delete;

    // Дозвіл переміщення ресурсу
    CpuLatencyLock(CpuLatencyLock&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    CpuLatencyLock& operator=(CpuLatencyLock&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

private:
    static constexpr std::string_view device_path_ = "/dev/cpu_dma_latency";
    int fd_{-1};
};

} // namespace pm_qos

int main() {
    try {
        std::cout << "[C++] Створюємо RAII-замок затримки (0 мкс)...\n";
        pm_qos::CpuLatencyLock latency_lock(0);

        std::cout << "[C++] PM QoS замок активний. Виконуємо обчислення без затримок пробудження...\n";
        ::usleep(500000); // 500 мс

        std::cout << "[C++] Завершено. Вихід із області видимості знищить замок RAII.\n";
    } catch (const std::exception& ex) {
        std::cerr << "[C++] Помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
