#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <system_error>
#include <utility>
#include <cerrno>
#include <csignal>
#include <cstdio>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>

namespace sys {

// RAII обгортка для безпечного володіння файловими дескрипторами
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

} // namespace sys

class PsiMonitor {
    static constexpr std::string_view kMemoryPath = "/proc/pressure/memory";
    static constexpr std::string_view kTriggerSpec = "some 150000 1000000";

    sys::UniqueFd psi_fd_;
    sys::UniqueFd epoll_fd_;
    bool running_{true};

public:
    void init() {
        int raw_psi = ::open(kMemoryPath.data(), O_RDWR | O_NONBLOCK);
        if (raw_psi < 0) {
            throw std::system_error(errno, std::generic_category(), "open " + std::string(kMemoryPath));
        }
        psi_fd_.reset(raw_psi);

        ssize_t written = ::write(psi_fd_.get(), kTriggerSpec.data(), kTriggerSpec.size());
        if (written < 0) {
            throw std::system_error(errno, std::generic_category(), "write PSI trigger");
        }

        int raw_epoll = ::epoll_create1(0);
        if (raw_epoll < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1");
        }
        epoll_fd_.reset(raw_epoll);

        epoll_event ev{};
        ev.events = EPOLLPRI;
        ev.data.fd = psi_fd_.get();

        if (::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, psi_fd_.get(), &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl ADD");
        }
    }

    void stop() noexcept {
        running_ = false;
    }

    void run_loop() {
        std::cout << "Демон PSI (C++) запущений. Очікування подій...\n";
        std::array<epoll_event, 1> events{};

        while (running_) {
            int nfds = ::epoll_wait(epoll_fd_.get(), events.data(), static_cast<int>(events.size()), 1000);
            if (nfds < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "epoll_wait failure");
            }

            if (nfds > 0 && (events[0].events & EPOLLPRI)) {
                on_pressure_event();
            }
        }
        std::cout << "Демон PSI (C++) успішно зупинений.\n";
    }

private:
    void on_pressure_event() {
        std::array<char, 512> buffer{};
        if (::lseek(psi_fd_.get(), 0, SEEK_SET) < 0) {
            std::cerr << "Помилка lseek на psi_fd\n";
            return;
        }

        ssize_t count = ::read(psi_fd_.get(), buffer.data(), buffer.size() - 1);
        if (count > 0) {
            buffer[count] = '\0';
            log_event_details(buffer.data());
        } else if (count < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            std::cerr << "Помилка читання даних PSI в C++\n";
        }
    }

    void log_event_details(const char* raw_text) {
        float avg10 = 0.0f, avg60 = 0.0f, avg300 = 0.0f;
        unsigned long long total = 0;

        if (std::sscanf(raw_text, "some avg10=%f avg60=%f avg300=%f total=%llu",
                        &avg10, &avg60, &avg300, &total) == 4) {
            std::cout << "[УВАГА C++] Виявлено тиск пам'яті! avg10=" << avg10 
                      << "% avg60=" << avg60 << "% total=" << total << " us\n";
        } else {
            std::cout << "[УВАГА C++] Сирий вивід PSI:\n" << raw_text;
        }
    }
};

static PsiMonitor* g_monitor_ptr = nullptr;

static void signal_handler(int sig) {
    (void)sig;
    if (g_monitor_ptr) {
        g_monitor_ptr->stop();
    }
}

int main() {
    try {
        PsiMonitor monitor;
        g_monitor_ptr = &monitor;

        struct sigaction sa{};
        sa.sa_handler = signal_handler;
        ::sigaction(SIGINT, &sa, nullptr);
        ::sigaction(SIGTERM, &sa, nullptr);

        monitor.init();
        monitor.run_loop();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка демона: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
