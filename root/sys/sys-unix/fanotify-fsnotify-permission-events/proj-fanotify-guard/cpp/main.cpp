#include <iostream>
#include <vector>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <string>
#include <cstring>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/fanotify.h>
#include <sys/stat.h>

namespace guard {

// RAII обгортка для безпечного управління файловими дескрипторами (RAII)
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
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

class FanotifyGuard {
    UniqueFd fanotify_fd_;
    pid_t daemon_pid_;

    void process_event(const fanotify_event_metadata& event) {
        // Упаковуємо дескриптор події в RAII обгортку для автоматичного закриття при виході
        UniqueFd event_fd(event.fd);
        fanotify_response response{event.fd, FAN_ALLOW};

        // Запобігання рекурсивному блокуванню власного процесу
        if (event.pid == daemon_pid_) {
            ::write(fanotify_fd_.get(), &response, sizeof(response));
            return;
        }

        char magic[4] = {0};
        ssize_t bytes_read = ::pread(event_fd.get(), magic, sizeof(magic), 0);

        if (bytes_read >= 4 && std::string_view(magic, 4) == "BAD!") {
            std::cout << "[GUARD-CPP] БЛОКУВАННЯ: PID=" << event.pid 
                      << " намагався відкрити заблокований вміст\n";
            response.response = FAN_DENY;
        } else {
            std::cout << "[GUARD-CPP] ДОЗВОЛЕНО: PID=" << event.pid << '\n';
            response.response = FAN_ALLOW;
        }

        if (::write(fanotify_fd_.get(), &response, sizeof(response)) < 0) {
            std::cerr << "Помилка надсилання рішення ядру: " << std::strerror(errno) << '\n';
        }
        // event_fd деструктор автоматично закриває дескриптор події
    }

public:
    explicit FanotifyGuard(const std::string& target_path) 
        : daemon_pid_(::getpid()) {
        
        int fd = ::fanotify_init(FAN_CLASS_CONTENT | FAN_CLOEXEC, O_RDONLY | O_CLOEXEC);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "fanotify_init failed");
        }
        fanotify_fd_.reset(fd);

        if (::fanotify_mark(fanotify_fd_.get(), FAN_MARK_ADD | FAN_MARK_MOUNT,
                           FAN_OPEN_PERM | FAN_OPEN_EXEC_PERM,
                           AT_FDCWD, target_path.c_str()) < 0) {
            throw std::system_error(errno, std::generic_category(), "fanotify_mark failed");
        }

        std::cout << "[GUARD-CPP] Моніторинг увімкнено на: " << target_path << '\n';
    }

    void run() {
        alignas(fanotify_event_metadata) char buffer[4096];

        while (true) {
            ssize_t len = ::read(fanotify_fd_.get(), buffer, sizeof(buffer));
            if (len < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "read failed");
            }

            const auto* metadata = reinterpret_cast<const fanotify_event_metadata*>(buffer);
            while (FAN_EVENT_OK(metadata, len)) {
                if (metadata->vers != FANOTIFY_METADATA_VERSION) {
                    throw std::runtime_error("Mismatched fanotify metadata version");
                }

                if (metadata->mask & (FAN_OPEN_PERM | FAN_OPEN_EXEC_PERM)) {
                    process_event(*metadata);
                }

                metadata = FAN_EVENT_NEXT(metadata, len);
            }
        }
    }
};

} // namespace guard

int main(int argc, char* argv[]) {
    try {
        const std::string path = (argc > 1) ? argv[1] : "/tmp";
        guard::FanotifyGuard daemon(path);
        daemon.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка демона: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
