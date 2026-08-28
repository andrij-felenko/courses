// psi_monitor.cpp — Демон спостереження за тиском пам'яті на C++20 (RAII)
#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <system_error>
#include <stdexcept>
#include <utility>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>

namespace sys {

// RAII-обгортка для безпечного управління файловими дескрипторами
class unique_fd {
    int m_fd{-1};

public:
    constexpr unique_fd() noexcept = default;
    explicit unique_fd(int fd) noexcept : m_fd(fd) {}
    ~unique_fd() { reset(); }

    unique_fd(const unique_fd&) = delete;
    unique_fd& operator=(const unique_fd&) = delete;

    unique_fd(unique_fd&& other) noexcept : m_fd(std::exchange(other.m_fd, -1)) {}
    unique_fd& operator=(unique_fd&& other) noexcept {
        if (this != &other) {
            reset();
            m_fd = std::exchange(other.m_fd, -1);
        }
        return *this;
    }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

} // namespace sys

class psi_monitor {
    static constexpr std::string_view TRIGGER_SPEC = "some 150000 1000000";
    static constexpr std::string_view PRESSURE_PATH = "/proc/pressure/memory";

    sys::unique_fd m_psi_fd;
    sys::unique_fd m_epoll_fd;

public:
    psi_monitor() {
        int fd = ::open(PRESSURE_PATH.data(), O_RDWR | O_CLOEXEC);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити вузол PSI");
        }
        m_psi_fd.reset(fd);

        ssize_t written = ::write(m_psi_fd.get(), TRIGGER_SPEC.data(), TRIGGER_SPEC.size());
        if (written < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося зареєструвати тригер PSI");
        }

        int efd = ::epoll_create1(EPOLL_CLOEXEC);
        if (efd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити epoll instance");
        }
        m_epoll_fd.reset(efd);

        epoll_event ev{};
        ev.events = EPOLLPRI;
        ev.data.fd = m_psi_fd.get();

        if (::epoll_ctl(m_epoll_fd.get(), EPOLL_CTL_ADD, m_psi_fd.get(), &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка додавання fd до epoll");
        }
    }

    void run() {
        std::cout << "[PSI Monitor C++] Тригер активовано: " << TRIGGER_SPEC << '\n';
        std::cout << "[PSI Monitor C++] Очікування на події тиску...\n";

        std::array<epoll_event, 8> events{};
        size_t alerts = 0;

        while (true) {
            int nfds = ::epoll_wait(m_epoll_fd.get(), events.data(), static_cast<int>(events.size()), -1);
            if (nfds < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "Помилка epoll_wait");
            }

            for (int i = 0; i < nfds; ++i) {
                if (events[i].data.fd == m_psi_fd.get() && (events[i].events & EPOLLPRI)) {
                    alerts++;
                    std::cout << "\n⚠️  [СПЛЕКСТ ТИСКУ #" << alerts << "] Сигнал тригера PSI! Аналіз пам'яті...\n";
                    print_metrics();
                }
            }
        }
    }

private:
    void print_metrics() const {
        sys::unique_fd fd(::open(PRESSURE_PATH.data(), O_RDONLY | O_CLOEXEC));
        if (!fd.valid()) return;

        std::array<char, 256> buf{};
        ssize_t bytes = ::read(fd.get(), buf.data(), buf.size() - 1);
        if (bytes > 0) {
            buf[bytes] = '\0';
            std::cout << "--- Поточний стан тиску ---\n" << buf.data() << "----------------------------\n";
        }
    }
};

int main() {
    try {
        psi_monitor daemon;
        daemon.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка демона: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
