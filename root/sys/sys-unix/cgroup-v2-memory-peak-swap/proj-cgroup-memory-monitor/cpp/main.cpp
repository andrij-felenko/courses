#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <array>
#include <filesystem>
#include <system_error>
#include <cerrno>
#include <memory>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/epoll.h>

namespace fs = std::filesystem;

class ScopedFd {
    int m_fd{-1};
public:
    explicit ScopedFd(int fd) : m_fd(fd) {}
    ~ScopedFd() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

class CgroupMemoryMonitor {
    fs::path m_cgroupPath;

    void writeControlFile(std::string_view filename, std::string_view value) {
        fs::path target = m_cgroupPath / filename;
        std::ofstream ofs(target);
        if (!ofs) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Не вдалося відкрити " + target.string());
        }
        ofs << value;
        if (!ofs) {
            throw std::runtime_error("Помилка запису у " + target.string());
        }
    }

    void printControlFile(std::string_view filename, std::string_view label) const {
        fs::path target = m_cgroupPath / filename;
        std::ifstream ifs(target);
        if (!ifs) return;

        std::string content((std::istreambuf_iterator<char>(ifs)),
                             std::istreambuf_iterator<char>());
        std::cout << "--- " << label << " (" << filename << ") ---\n" << content;
    }

public:
    explicit CgroupMemoryMonitor(fs::path path) : m_cgroupPath(std::move(path)) {}

    void setup(uint64_t highBytes, uint64_t maxBytes) {
        std::error_code ec;
        fs::create_directories(m_cgroupPath, ec);
        if (ec) {
            throw std::system_error(ec, "Не вдалося створити cgroup каталог");
        }
        std::cout << "Cgroup створено: " << m_cgroupPath << "\n";

        writeControlFile("memory.high", std::to_string(highBytes));
        writeControlFile("memory.max", std::to_string(maxBytes));
    }

    void monitorEvents(int timeoutMs) {
        fs::path eventsPath = m_cgroupPath / "memory.events";
        ScopedFd eventsFd(::open(eventsPath.c_str(), O_RDONLY | O_NONBLOCK));
        if (!eventsFd.valid()) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка відкриття memory.events");
        }

        ScopedFd epollFd(::epoll_create1(0));
        if (!epollFd.valid()) {
            throw std::system_error(errno, std::generic_category(), 
                                   "epoll_create1 failed");
        }

        struct epoll_event ev{};
        ev.events = EPOLLPRI | EPOLLERR;
        ev.data.fd = eventsFd.get();
        if (::epoll_ctl(epollFd.get(), EPOLL_CTL_ADD, eventsFd.get(), &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "epoll_ctl failed");
        }

        std::cout << "Очікування подій пам'яті через epoll...\n";
        std::array<struct epoll_event, 4> readyEvents{};
        int n = ::epoll_wait(epollFd.get(), readyEvents.data(), readyEvents.size(), timeoutMs);

        if (n < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_wait failed");
        } else if (n == 0) {
            std::cout << "Таймаут очікування. Поточні метрики:\n";
        } else {
            std::cout << "Подію виявлено! Оновлені дані cgroup:\n";
        }

        printControlFile("memory.events", "Події пам'яті");
        printControlFile("memory.current", "Поточне споживання RAM");
        printControlFile("memory.peak", "Пікове споживання RAM");
    }
};

int main() {
    try {
        CgroupMemoryMonitor monitor("/sys/fs/cgroup/test_memcg_cpp");
        monitor.setup(52428800, 104857600); // 50MB high, 100MB max
        monitor.monitorEvents(5000);
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
