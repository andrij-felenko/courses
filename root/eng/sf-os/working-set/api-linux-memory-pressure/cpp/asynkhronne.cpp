#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/epoll.h>

class PsiMemoryMonitor {
public:
    PsiMemoryMonitor(std::string_view trigger_spec = "some 100000 1000000") {
        psi_fd_ = ::open("/proc/pressure/memory", O_RDWR | O_NONBLOCK);
        if (psi_fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "open(/proc/pressure/memory) failed");
        }

        if (::write(psi_fd_, trigger_spec.data(), trigger_spec.size()) < 0) {
            ::close(psi_fd_);
            throw std::system_error(errno, std::generic_category(), "write PSI trigger failed");
        }

        epoll_fd_ = ::epoll_create1(0);
        if (epoll_fd_ < 0) {
            ::close(psi_fd_);
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }

        struct epoll_event ev{};
        ev.events = EPOLLPRI;
        ev.data.fd = psi_fd_;

        if (::epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, psi_fd_, &ev) < 0) {
            ::close(psi_fd_);
            ::close(epoll_fd_);
            throw std::system_error(errno, std::generic_category(), "epoll_ctl failed");
        }
    }

    ~PsiMemoryMonitor() noexcept {
        if (psi_fd_ >= 0) ::close(psi_fd_);
        if (epoll_fd_ >= 0) ::close(epoll_fd_);
    }

    PsiMemoryMonitor(const PsiMemoryMonitor&) = delete;
    PsiMemoryMonitor& operator=(const PsiMemoryMonitor&) = delete;

    [[nodiscard]] bool wait_event(int timeout_ms = 5000) {
        struct epoll_event events[1];
        int nfds = ::epoll_wait(epoll_fd_, events, 1, timeout_ms);
        if (nfds < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_wait failed");
        }
        return (nfds > 0 && (events[0].events & EPOLLPRI));
    }

private:
    int psi_fd_{-1};
    int epoll_fd_{-1};
};

int main() {
    try {
        std::cout << "Ініціалізація C++ PSI монітора пам'яті...\n";
        PsiMemoryMonitor monitor("some 100000 1000000");

        std::cout << "Очікування сплеску навантаження (таймаут 10 с)...\n";
        bool triggered = monitor.wait_event(10000);

        if (triggered) {
            std::cout << "ПОПЕРЕДЖЕННЯ: Тиск на оперативну пам'ять перевищив 10%!\n";
        } else {
            std::cout << "Тиск у нормі: система працює без значних затримок пам'яті.\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
