#include <iostream>
#include <memory>
#include <string_view>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <sys/signalfd.h>
#include <sys/epoll.h>
#include <linux/vt.h>
#include <linux/kd.h>
#include <xf86drm.h>

namespace vt {

constexpr int ReleaseSignal = SIGUSR1;
constexpr int AcquireSignal = SIGUSR2;

class UniqueFd {
    int m_fd = -1;
public:
    explicit UniqueFd(int fd = -1) noexcept : m_fd(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.m_fd);
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }
};

class VtSessionManager {
    UniqueFd m_ttyFd;
    UniqueFd m_drmFd;
    UniqueFd m_signalFd;
    UniqueFd m_epollFd;

    long m_origKbMode = K_XLATE;
    struct vt_mode m_origVtMode{};
    bool m_isActive = true;
    bool m_isRunning = true;

public:
    VtSessionManager(std::string_view ttyPath, std::string_view drmPath) {
        m_ttyFd.reset(::open(ttyPath.data(), O_RDWR | O_NOCTTY | O_CLOEXEC));
        if (!m_ttyFd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити TTY");
        }

        if (::ioctl(m_ttyFd.get(), KDGKBMODE, &m_origKbMode) < 0) {
            throw std::system_error(errno, std::generic_category(), "KDGKBMODE помилка");
        }

        if (::ioctl(m_ttyFd.get(), VT_GETMODE, &m_origVtMode) < 0) {
            throw std::system_error(errno, std::generic_category(), "VT_GETMODE помилка");
        }

        m_drmFd.reset(::open(drmPath.data(), O_RDWR | O_CLOEXEC));
        if (!m_drmFd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити DRM пристрій");
        }

        setupSignalHandling();
        setupConsoleModes();
    }

    ~VtSessionManager() noexcept {
        restoreConsole();
    }

    void runLoop() {
        struct epoll_event events[4];
        std::cout << "[VT C++] Головний цикл сесії запущено\n";

        while (m_isRunning) {
            int nfds = ::epoll_wait(m_epollFd.get(), events, 4, 1000);
            if (nfds < 0) {
                if (errno == EINTR) continue;
                break;
            }

            for (int i = 0; i < nfds; ++i) {
                if (events[i].data.fd == m_signalFd.get()) {
                    handleSignalEvent();
                }
            }

            if (m_isActive) {
                // Відмальовування графіки композитором
            }
        }
    }

private:
    void setupSignalHandling() {
        sigset_t mask;
        ::sigemptyset(&mask);
        ::sigaddset(&mask, ReleaseSignal);
        ::sigaddset(&mask, AcquireSignal);
        ::sigaddset(&mask, SIGINT);
        ::sigaddset(&mask, SIGTERM);

        if (::sigprocmask(SIG_BLOCK, &mask, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "sigprocmask помилка");
        }

        m_signalFd.reset(::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC));
        if (!m_signalFd.valid()) {
            throw std::system_error(errno, std::generic_category(), "signalfd помилка");
        }

        m_epollFd.reset(::epoll_create1(EPOLL_CLOEXEC));
        if (!m_epollFd.valid()) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 помилка");
        }

        struct epoll_event ev{};
        ev.events = EPOLLIN;
        ev.data.fd = m_signalFd.get();
        if (::epoll_ctl(m_epollFd.get(), EPOLL_CTL_ADD, m_signalFd.get(), &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl помилка");
        }
    }

    void setupConsoleModes() {
        // Вимикаємо трансляцію клавіатури у TTY
        ::ioctl(m_ttyFd.get(), KDSKBMODE, K_OFF);

        struct vt_mode mode{
            .mode = VT_PROCESS,
            .waitv = 0,
            .relsig = static_cast<short>(ReleaseSignal),
            .acqsig = static_cast<short>(AcquireSignal),
            .frsig = 0
        };

        if (::ioctl(m_ttyFd.get(), VT_SETMODE, &mode) < 0) {
            throw std::system_error(errno, std::generic_category(), "VT_SETMODE помилка");
        }
    }

    void handleSignalEvent() {
        struct signalfd_siginfo fdsi{};
        ssize_t s = ::read(m_signalFd.get(), &fdsi, sizeof(fdsi));
        if (s != sizeof(fdsi)) return;

        if (fdsi.ssi_signo == ReleaseSignal) {
            std::cout << "[VT C++] Звільнення консолі: drmDropMaster\n";
            m_isActive = false;
            ::drmDropMaster(m_drmFd.get());
            ::ioctl(m_ttyFd.get(), VT_RELDISP, 1);
        } else if (fdsi.ssi_signo == AcquireSignal) {
            std::cout << "[VT C++] Захоплення консолі: drmSetMaster\n";
            ::drmSetMaster(m_drmFd.get());
            ::ioctl(m_ttyFd.get(), VT_RELDISP, VT_ACKACQ);
            m_isActive = true;
        } else if (fdsi.ssi_signo == SIGINT || fdsi.ssi_signo == SIGTERM) {
            std::cout << "[VT C++] Завершення сесії...\n";
            m_isRunning = false;
        }
    }

    void restoreConsole() noexcept {
        if (m_ttyFd.valid()) {
            ::ioctl(m_ttyFd.get(), VT_SETMODE, &m_origVtMode);
            ::ioctl(m_ttyFd.get(), KDSKBMODE, m_origKbMode);
        }
    }
};

} // namespace vt

int main(int argc, char** argv) {
    const char* ttyPath = (argc > 1) ? argv[1] : "/dev/tty";
    const char* drmPath = (argc > 2) ? argv[2] : "/dev/dri/card0";

    try {
        vt::VtSessionManager manager(ttyPath, drmPath);
        manager.runLoop();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка VT сесії: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
