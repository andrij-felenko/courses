#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <system_error>
#include <csignal>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

class PasswdDatabaseLock {
public:
    static constexpr std::string_view kPasswdPath = "/etc/passwd";
    static constexpr std::string_view kLockPath   = "/etc/ptmp";

    static std::expected<PasswdDatabaseLock, std::error_code> acquire() {
        setup_signal_handlers();

        int fd = ::open(kLockPath.data(), O_CREAT | O_EXCL | O_RDWR, 0600);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        s_active_lock = true;

        std::string pid_str = std::to_string(::getpid()) + "\n";
        if (::write(fd, pid_str.data(), pid_str.size()) != static_cast<ssize_t>(pid_str.size())) {
            ::close(fd);
            ::unlink(kLockPath.data());
            s_active_lock = false;
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return PasswdDatabaseLock(fd);
    }

    ~PasswdDatabaseLock() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        if (m_locked) {
            ::unlink(kLockPath.data());
            s_active_lock = false;
        }
    }

    PasswdDatabaseLock(const PasswdDatabaseLock&) = delete;
    PasswdDatabaseLock& operator=(const PasswdDatabaseLock&) = delete;

    PasswdDatabaseLock(PasswdDatabaseLock&& other) noexcept
        : m_fd(other.m_fd), m_locked(other.m_locked) {
        other.m_fd = -1;
        other.m_locked = false;
    }

    PasswdDatabaseLock& operator=(PasswdDatabaseLock&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            if (m_locked) ::unlink(kLockPath.data());

            m_fd = other.m_fd;
            m_locked = other.m_locked;
            other.m_fd = -1;
            other.m_locked = false;
        }
        return *this;
    }

    int file_descriptor() const noexcept { return m_fd; }

    std::expected<void, std::error_code> commit() {
        if (::fsync(m_fd) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        ::close(m_fd);
        m_fd = -1;

        if (::rename(kLockPath.data(), kPasswdPath.data()) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        m_locked = false;
        s_active_lock = false;
        return {};
    }

private:
    explicit PasswdDatabaseLock(int fd) : m_fd(fd), m_locked(true) {}

    int m_fd = -1;
    bool m_locked = false;
    static inline volatile sig_atomic_t s_active_lock = false;

    static void signal_handler(int) {
        if (s_active_lock) {
            ::unlink(kLockPath.data());
            s_active_lock = false;
        }
        ::_exit(1);
    }

    static void setup_signal_handlers() {
        struct sigaction sa{};
        sa.sa_handler = signal_handler;
        ::sigemptyset(&sa.sa_mask);

        ::sigaction(SIGINT,  &sa, nullptr);
        ::sigaction(SIGHUP,  &sa, nullptr);
        ::sigaction(SIGQUIT, &sa, nullptr);
        ::sigaction(SIGTERM, &sa, nullptr);
    }
};

std::expected<void, std::string> update_user_shell_cpp(std::string_view target_user, std::string_view new_shell) {
    auto lock_res = PasswdDatabaseLock::acquire();
    if (!lock_res) {
        return std::unexpected("Не вдалося захопити блокування: " + lock_res.error().message());
    }
    auto lock = std::move(*lock_res);

    std::ifstream in(PasswdDatabaseLock::kPasswdPath.data());
    if (!in.is_open()) {
        return std::unexpected("Не вдалося відкрити " + std::string(PasswdDatabaseLock::kPasswdPath));
    }

    std::ofstream out(PasswdDatabaseLock::kLockPath.data(), std::ios::app);
    if (!out.is_open()) {
        return std::unexpected("Не вдалося відкрити файл блокування для запису");
    }

    std::string line;
    bool user_found = false;
    std::string prefix = std::string(target_user) + ":";

    while (std::getline(in, line)) {
        if (line.starts_with(prefix)) {
            user_found = true;
            std::vector<std::string> parts;
            std::stringstream ss(line);
            std::string item;
            while (std::getline(ss, item, ':')) {
                parts.push_back(item);
            }
            if (parts.size() >= 7) {
                parts[6] = std::string(new_shell);
                for (size_t i = 0; i < parts.size(); ++i) {
                    out << parts[i] << (i + 1 == parts.size() ? "" : ":");
                }
                out << "\n";
                continue;
            }
        }
        out << line << "\n";
    }

    in.close();
    out.flush();

    if (!user_found) {
        return std::unexpected("Користувача «" + std::string(target_user) + "» не знайдено");
    }

    auto commit_res = lock.commit();
    if (!commit_res) {
        return std::unexpected("Помилка атомарної заміни бази: " + commit_res.error().message());
    }

    return {};
}
