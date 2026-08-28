#include <iostream>
#include <thread>
#include <atomic>
#include <vector>
#include <string_view>
#include <filesystem>
#include <chrono>
#include <cstdlib>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

namespace fs = std::filesystem;

class ScopedFileDescriptor {
public:
    explicit ScopedFileDescriptor(int fd = -1) noexcept : m_fd(fd) {}
    ~ScopedFileDescriptor() { reset(); }

    ScopedFileDescriptor(const ScopedFileDescriptor&) = delete;
    ScopedFileDescriptor& operator=(const ScopedFileDescriptor&) = delete;

    ScopedFileDescriptor(ScopedFileDescriptor&& other) noexcept : m_fd(other.release()) {}
    ScopedFileDescriptor& operator=(ScopedFileDescriptor&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    int release() noexcept {
        int old_fd = m_fd;
        m_fd = -1;
        return old_fd;
    }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }

private:
    int m_fd{-1};
};

[[noreturn]] static void inspect_child_fds() noexcept {
    int leaked_count = 0;
    try {
        for (const auto& entry : fs::directory_iterator("/proc/self/fd")) {
            const auto name = entry.path().filename().string();
            int fd = std::atoi(name.c_str());
            /* Дескриптори 0, 1, 2 — стандартні потоки вводу-виводу */
            if (fd > 2) {
                leaked_count++;
            }
        }
    } catch (...) {
        ::_exit(1);
    }

    /* directory_iterator сам тримає відкритий дескриптор каталогу procfs */
    if (leaked_count > 1) {
        ::_exit(42);
    }
    ::_exit(0);
}

int main(int argc, char* argv[]) {
    const bool use_atomic = (argc > 1 && std::string_view(argv[1]) == "--atomic");

    std::cout << (use_atomic 
        ? "=== Режим C++: Атомарний O_CLOEXEC (гонитва усунена) ===\n" 
        : "=== Режим C++: Неатомарний open() + fcntl() (стан гонитви) ===\n");

    std::atomic<bool> running{true};
    std::atomic<int> leaks_detected{0};

    std::thread worker([&running, use_atomic]() {
        while (running.load(std::memory_order_relaxed)) {
            ScopedFileDescriptor file;
            if (use_atomic) {
                file.reset(::open("/dev/null", O_RDONLY | O_CLOEXEC));
            } else {
                file.reset(::open("/dev/null", O_RDONLY));
                if (file.valid()) {
                    int flags = ::fcntl(file.get(), F_GETFD);
                    if (flags != -1) {
                        ::fcntl(file.get(), F_SETFD, flags | FD_CLOEXEC);
                    }
                }
            }

            if (file.valid()) {
                std::this_thread::sleep_for(std::chrono::microseconds(50));
            }
        }
    });

    constexpr int iterations = 500;
    for (int i = 0; i < iterations; ++i) {
        pid_t pid = ::fork();
        if (pid < 0) {
            break;
        }

        if (pid == 0) {
            inspect_child_fds();
        }

        int status = 0;
        ::waitpid(pid, &status, 0);
        if (WIFEXITED(status) && WEXITSTATUS(status) == 42) {
            leaks_detected.fetch_add(1, std::memory_order_relaxed);
        }
        std::this_thread::sleep_for(std::chrono::microseconds(150));
    }

    running.store(false, std::memory_order_relaxed);
    worker.join();

    std::cout << "Підсумок після " << iterations << " запусків fork():\n";
    std::cout << "  Зафіксовано витоків дескрипторів: " << leaks_detected.load() << "\n";

    return 0;
}
