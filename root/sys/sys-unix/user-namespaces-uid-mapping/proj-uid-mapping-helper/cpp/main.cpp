#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <system_error>
#include <expected>
#include <memory>
#include <array>
#include <cerrno>
#include <cstring>
#include <csignal>
#include <sched.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>

namespace userns {

// RAII обгортка для файлового дескриптора
class Pipe {
    std::array<int, 2> fds_{-1, -1};
public:
    Pipe() {
        if (::pipe(fds_.data()) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe failed");
        }
    }
    ~Pipe() {
        close_read();
        close_write();
    }
    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }

    void close_read() noexcept {
        if (fds_[0] != -1) { ::close(fds_[0]); fds_[0] = -1; }
    }
    void close_write() noexcept {
        if (fds_[1] != -1) { ::close(fds_[1]); fds_[1] = -1; }
    }
};

// Запис рядка у procfs файл із обробкою помилок
std::expected<void, std::error_code> write_proc(const std::string& path, std::string_view content) {
    int fd = ::open(path.c_str(), O_WRONLY);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    auto cleanup = std::unique_ptr<void, void(*)(void*)>((void*)(intptr_t)fd, [](void* f) {
        ::close((int)(intptr_t)f);
    });

    ssize_t written = ::write(fd, content.data(), content.size());
    if (written != static_cast<ssize_t>(content.size())) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

struct ChildContext {
    Pipe pipe;
    uid_t parent_uid;
    gid_t parent_gid;
};

int child_main(void* arg) {
    auto* ctx = static_cast<ChildContext*>(arg);
    ctx->pipe.close_write();

    char sync_byte;
    // Очікуємо закриття pipe батьківським процесом
    if (::read(ctx->pipe.read_fd(), &sync_byte, 1) != 0) {
        std::cerr << "[Child C++] Sync error\n";
        return 1;
    }
    ctx->pipe.close_read();

    std::cout << "[Child C++] Ізольоване середовище створено:\n"
              << "  UID: " << ::getuid() << " (euid: " << ::geteuid() << ")\n"
              << "  GID: " << ::getgid() << " (egid: " << ::getegid() << ")\n";

    std::array<const char*, 3> args = {"/bin/sh", "-c", "id", nullptr};
    ::execvp(args[0], const_cast<char* const*>(args.data()));
    return 1;
}

} // namespace userns

int main() {
    try {
        userns::ChildContext ctx{
            .pipe = {},
            .parent_uid = ::getuid(),
            .parent_gid = ::getgid()
        };

        constexpr size_t STACK_SIZE = 1024 * 1024;
        auto stack = std::make_unique<char[]>(STACK_SIZE);

        pid_t pid = ::clone(userns::child_main, stack.get() + STACK_SIZE,
                            CLONE_NEWUSER | SIGCHLD, &ctx);
        if (pid < 0) {
            std::cerr << "clone failed: " << std::strerror(errno) << "\n";
            return 1;
        }

        std::cout << "[Parent C++] Створено namespace для PID " << pid << "\n";

        std::string setgroups_path = "/proc/" + std::to_string(pid) + "/setgroups";
        std::string uid_map_path   = "/proc/" + std::to_string(pid) + "/uid_map";
        std::string gid_map_path   = "/proc/" + std::to_string(pid) + "/gid_map";

        if (auto res = userns::write_proc(setgroups_path, "deny"); !res) {
            std::cerr << "Failed setgroups: " << res.error().message() << "\n";
            ::kill(pid, SIGKILL);
            return 1;
        }

        if (auto res = userns::write_proc(uid_map_path, "0 " + std::to_string(ctx.parent_uid) + " 1\n"); !res) {
            std::cerr << "Failed uid_map: " << res.error().message() << "\n";
            ::kill(pid, SIGKILL);
            return 1;
        }

        if (auto res = userns::write_proc(gid_map_path, "0 " + std::to_string(ctx.parent_gid) + " 1\n"); !res) {
            std::cerr << "Failed gid_map: " << res.error().message() << "\n";
            ::kill(pid, SIGKILL);
            return 1;
        }

        std::cout << "[Parent C++] Мапінг успішно записано. Сигналізуємо нащадку...\n";
        ctx.pipe.close_write();

        int status = 0;
        ::waitpid(pid, &status, 0);
        std::cout << "[Parent C++] Дочірній процес завершився.\n";

    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
