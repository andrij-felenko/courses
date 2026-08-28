// Демон супервізії сторожового таймера на мові C++ (C++20 RAII & System Interfaces)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <atomic>
#include <csignal>
#include <cerrno>
#include <cstring>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>

namespace {
std::atomic<bool> g_running{true};

void signal_handler(int) {
    g_running.store(false);
}
}

class WatchdogDevice {
public:
    explicit WatchdogDevice(std::string_view path, int timeout_sec)
        : dev_path_(path) {
        fd_ = ::open(dev_path_.c_str(), O_RDWR | O_CLOEXEC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Failed to open watchdog device " + dev_path_);
        }

        struct watchdog_info info{};
        if (::ioctl(fd_, WDIOC_GETSUPPORT, &info) == 0) {
            identity_ = reinterpret_cast<const char*>(info.identity);
            supports_magic_close_ = (info.options & WDIOF_MAGICCLOSE) != 0;
        }

        int t = timeout_sec;
        if (::ioctl(fd_, WDIOC_SETTIMEOUT, &t) == 0) {
            active_timeout_ = t;
        } else {
            active_timeout_ = timeout_sec;
        }
    }

    ~WatchdogDevice() {
        if (fd_ >= 0) {
            if (supports_magic_close_) {
                const char v = 'V';
                [[maybe_unused]] auto ret = ::write(fd_, &v, 1);
            }
            ::close(fd_);
        }
    }

    WatchdogDevice(const WatchdogDevice&) = delete;
    WatchdogDevice& operator=(const WatchdogDevice&) = delete;

    WatchdogDevice(WatchdogDevice&& other) noexcept 
        : fd_(other.fd_), dev_path_(std::move(other.dev_path_)),
          identity_(std::move(other.identity_)),
          active_timeout_(other.active_timeout_),
          supports_magic_close_(other.supports_magic_close_) {
        other.fd_ = -1;
    }

    void keep_alive() {
        if (::ioctl(fd_, WDIOC_KEEPALIVE, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "WDIOC_KEEPALIVE failed");
        }
    }

    [[nodiscard]] int timeout() const noexcept { return active_timeout_; }
    [[nodiscard]] const std::string& identity() const noexcept { return identity_; }

private:
    int fd_{-1};
    std::string dev_path_;
    std::string identity_;
    int active_timeout_{30};
    bool supports_magic_close_{false};
};

bool is_system_healthy() {
    std::ifstream meminfo("/proc/meminfo");
    if (!meminfo.is_open()) return true;  // немає /proc/meminfo — це не привід глушити Heartbeat

    std::string key;
    long value = 0;
    std::string unit;
    long total_kb = 0, avail_kb = 0;

    while (meminfo >> key >> value >> unit) {
        if (key == "MemTotal:") total_kb = value;
        else if (key == "MemAvailable:") avail_kb = value;
    }

    if (total_kb > 0 && avail_kb > 0) {
        double ratio = static_cast<double>(avail_kb) / static_cast<double>(total_kb);
        return ratio >= 0.02; // Поріг здоров'я — мінімум 2% вільної RAM
    }
    return true;
}

int main(int argc, char* argv[]) {
    std::string_view dev = (argc > 1) ? argv[1] : "/dev/watchdog";

    std::signal(SIGTERM, signal_handler);
    std::signal(SIGINT, signal_handler);

    try {
        WatchdogDevice wd(dev, 30);
        std::cout << "Watchdog initialized: " << wd.identity() 
                  << " (Timeout: " << wd.timeout() << "s)\n";

        const auto ping_interval = std::chrono::seconds(wd.timeout() / 2);

        while (g_running.load()) {
            if (is_system_healthy()) {
                wd.keep_alive();
                std::cout << "[Heartbeat] Ping sent to " << dev << '\n';
            } else {
                std::cerr << "[CRITICAL] Health check failed, ping suppressed!\n";
            }
            std::this_thread::sleep_for(ping_interval);
        }

        std::cout << "Gracefully shutting down supervisor daemon...\n";
    } catch (const std::exception& ex) {
        std::cerr << "Fatal Error: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
