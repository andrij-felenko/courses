#include <iostream>
#include <fstream>
#include <filesystem>
#include <system_error>
#include <csignal>
#include <atomic>
#include <thread>
#include <chrono>
#include <memory>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

namespace system_daemon {

std::atomic<bool> g_running{true};
std::atomic<bool> g_reload_requested{false};

void handle_signal(int signum) noexcept {
    if (signum == SIGTERM) {
        g_running.store(false, std::memory_order_relaxed);
    } else if (signum == SIGHUP) {
        g_reload_requested.store(true, std::memory_order_relaxed);
    }
}

class FileDescriptorWrapper {
public:
    explicit FileDescriptorWrapper(int fd) noexcept : fd_(fd) {}
    ~FileDescriptorWrapper() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    FileDescriptorWrapper(const FileDescriptorWrapper&) = delete;
    FileDescriptorWrapper& operator=(const FileDescriptorWrapper&) = delete;
    FileDescriptorWrapper(FileDescriptorWrapper&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    FileDescriptorWrapper& operator=(FileDescriptorWrapper&& other) noexcept {
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

class DaemonIsolation {
public:
    static void isolate(const std::filesystem::path& work_dir, const std::filesystem::path& log_path) {
        ::umask(0);

        pid_t pid1 = ::fork();
        if (pid1 < 0) {
            throw std::system_error(errno, std::generic_category(), "First fork failed");
        }
        if (pid1 > 0) {
            ::_exit(0);
        }

        if (::setsid() < 0) {
            throw std::system_error(errno, std::generic_category(), "setsid failed");
        }

        pid_t pid2 = ::fork();
        if (pid2 < 0) {
            throw std::system_error(errno, std::generic_category(), "Second fork failed");
        }
        if (pid2 > 0) {
            ::_exit(0);
        }

        std::filesystem::current_path(work_dir);

        setup_signals();
        redirect_standard_io(log_path);
    }

private:
    static void setup_signals() {
        struct sigaction sa{};
        sa.sa_handler = handle_signal;
        ::sigemptyset(&sa.sa_mask);

        if (::sigaction(SIGTERM, &sa, nullptr) < 0 || ::sigaction(SIGHUP, &sa, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "Signal registration failed");
        }
    }

    static void redirect_standard_io(const std::filesystem::path& log_path) {
        FileDescriptorWrapper null_fd(::open("/dev/null", O_RDWR));
        if (!null_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Failed to open /dev/null");
        }

        FileDescriptorWrapper log_fd(::open(log_path.c_str(), O_WRONLY | O_CREAT | O_APPEND, 0644));
        int target_out_fd = log_fd.valid() ? log_fd.get() : null_fd.get();

        if (::dup2(null_fd.get(), STDIN_FILENO) < 0 ||
            ::dup2(target_out_fd, STDOUT_FILENO) < 0 ||
            ::dup2(target_out_fd, STDERR_FILENO) < 0) {
            throw std::system_error(errno, std::generic_category(), "dup2 file descriptor redirection failed");
        }
    }
};

} // namespace system_daemon

int main() {
    try {
        system_daemon::DaemonIsolation::isolate("/", "/tmp/daemon_worker_cpp.log");

        std::cout << "Modern C++ Daemon running with PID " << ::getpid() << std::endl;

        while (system_daemon::g_running.load(std::memory_order_relaxed)) {
            if (system_daemon::g_reload_requested.exchange(false, std::memory_order_relaxed)) {
                std::cout << "Reloading config via SIGHUP at " 
                          << std::chrono::system_clock::now().time_since_epoch().count() 
                          << std::endl;
            }
            std::this_thread::sleep_for(std::chrono::seconds(2));
        }

        std::cout << "Daemon shutting down cleanly." << std::endl;
    } catch (const std::exception& ex) {
        return 1;
    }
    return 0;
}
