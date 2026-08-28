// ============================================================================
// cluster_fencing_daemon.cpp — C++20 реалізація контролера з RAII та chrono
// ============================================================================
#include <iostream>
#include <string_view>
#include <chrono>
#include <expected>
#include <optional>
#include <thread>
#include <atomic>
#include <csignal>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>

using namespace std::chrono_literals;

namespace cluster {

constexpr auto kLoopWaitInterval = 2000ms;
constexpr auto kSafetyMargin = 5000ms;
constexpr auto kLeaseTtl = 10000ms;
constexpr std::string_view kWatchdogPath = "/dev/watchdog";
constexpr std::string_view kDbSocketPath = "/tmp/.s.PGSQL.5432";

enum class NodeRole {
    Follower,
    LeaderActive,
    LeaseDegraded,
    Fenced
};

// RAII обгортка над дескриптором файлу/сокета
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

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
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

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

private:
    int fd_{-1};
};

// RAII контролер апаратного сторожового пристрою Linux
class WatchdogDriver {
public:
    static std::expected<WatchdogDriver, std::string> create(std::chrono::seconds timeout) {
        int fd = ::open(kWatchdogPath.data(), O_WRONLY);
        if (fd < 0) {
            return std::unexpected(std::strerror(errno));
        }

        int t_sec = static_cast<int>(timeout.count());
        if (::ioctl(fd, WDIOC_SETTIMEOUT, &t_sec) < 0) {
            std::cerr << "[WARN] Не вдалося налаштувати таймаут watchdog: " << std::strerror(errno) << "\n";
        }
        return WatchdogDriver(UniqueFd(fd), timeout);
    }

    ~WatchdogDriver() {
        if (fd_.isValid() && !fenced_) {
            // Магічний символ 'V' дозволяє закрити пристрій без паніки ядра
            [[maybe_unused]] auto res = ::write(fd_.get(), "V", 1);
            std::cout << "[INFO] Watchdog коректно деактивовано.\n";
        }
    }

    WatchdogDriver(WatchdogDriver&&) noexcept = default;
    WatchdogDriver& operator=(WatchdogDriver&&) noexcept = default;

    void keepAlive() noexcept {
        if (fd_.isValid() && !fenced_) {
            int dummy = 0;
            ::ioctl(fd_.get(), WDIOC_KEEPALIVE, &dummy);
        }
    }

    void triggerFencing() noexcept {
        fenced_ = true;
        // Залишаємо дескриптор відкритим без подовження, щоб ядро ініціювало перезавантаження
        std::cerr << "[PANIC] Watchdog залишено без оновлення для апаратного скидання!\n";
    }

private:
    explicit WatchdogDriver(UniqueFd fd, std::chrono::seconds timeout)
        : fd_(std::move(fd)), timeout_(timeout) {}

    UniqueFd fd_;
    std::chrono::seconds timeout_{0};
    bool fenced_{false};
};

class FencingSupervisor {
public:
    explicit FencingSupervisor(std::optional<WatchdogDriver> watchdog)
        : watchdog_(std::move(watchdog)),
          role_(NodeRole::LeaderActive),
          last_heartbeat_(std::chrono::steady_clock::now()) {}

    void run(std::atomic<bool>& shutdown_requested) {
        std::cout << "[INFO] C++ Контролер огородження запущено. Роль: Primary.\n";
        int iteration = 0;

        while (!shutdown_requested && role_ != NodeRole::Fenced) {
            ++iteration;
            auto now = std::chrono::steady_clock::now();

            bool simulate_network_drop = (iteration >= 6 && iteration <= 8);
            bool db_alive = checkDatabaseHealth();
            bool dcs_ok = renewConsensusLease(simulate_network_drop);

            if (db_alive && dcs_ok) {
                last_heartbeat_ = now;
                role_ = NodeRole::LeaderActive;
                if (watchdog_) {
                    watchdog_->keepAlive();
                }
                std::cout << "[OK] Ітерація " << iteration << ": лізу підтверджено, сторож оновлений.\n";
            } else {
                role_ = NodeRole::LeaseDegraded;
                auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_heartbeat_);
                std::cerr << "[WARN] Ітерація " << iteration << ": втрата зв'язку. Минуло: "
                          << elapsed.count() << "мс із дозволених "
                          << std::chrono::duration_cast<std::chrono::milliseconds>(kSafetyMargin).count() << "мс\n";

                if (elapsed >= kSafetyMargin) {
                    performEmergencyFencing();
                    break;
                }
            }

            std::this_thread::sleep_for(kLoopWaitInterval);
        }
    }

    [[nodiscard]] NodeRole getRole() const noexcept { return role_; }

private:
    bool checkDatabaseHealth() const noexcept {
        UniqueFd sock(::socket(AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK, 0));
        if (!sock.isValid()) return false;

        sockaddr_un addr{};
        addr.sun_family = AF_UNIX;
        std::strncpy(addr.sun_path, kDbSocketPath.data(), sizeof(addr.sun_path) - 1);

        if (::connect(sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            if (errno != EINPROGRESS) return false;
        }

        pollfd pfd{.fd = sock.get(), .events = POLLOUT, .revents = 0};
        int res = ::poll(&pfd, 1, 300);
        if (res <= 0 || (pfd.revents & (POLLERR | POLLHUP))) return false;

        int error = 0;
        socklen_t len = sizeof(error);
        ::getsockopt(sock.get(), SOL_SOCKET, SO_ERROR, &error, &len);
        return (error == 0);
    }

    bool renewConsensusLease(bool simulate_drop) const noexcept {
        return !simulate_drop;
    }

    void performEmergencyFencing() {
        std::cerr << "[CRITICAL] ОГОРОДЖЕННЯ! Аварійна ізоляція вузла.\n";
        role_ = NodeRole::Fenced;
        std::system("pkill -9 -f postgres || true");
        if (watchdog_) {
            watchdog_->triggerFencing();
        }
    }

    std::optional<WatchdogDriver> watchdog_;
    NodeRole role_;
    std::chrono::steady_clock::time_point last_heartbeat_;
};

} // namespace cluster

static std::atomic<bool> g_stop_signal{false};

extern "C" void signal_handler(int) {
    g_stop_signal = true;
}

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    auto watchdog_res = cluster::WatchdogDriver::create(7s);
    std::optional<cluster::WatchdogDriver> watchdog;
    if (watchdog_res) {
        watchdog.emplace(std::move(*watchdog_res));
    } else {
        std::cerr << "[WARN] Працюємо без апаратного Watchdog: " << watchdog_res.error() << "\n";
    }

    cluster::FencingSupervisor supervisor(std::move(watchdog));
    supervisor.run(g_stop_signal);

    return (supervisor.getRole() == cluster::NodeRole::Fenced) ? 1 : 0;
}
