// Безпечна передача секрету нащадку через RAII та пайпи мовою C++
#include <iostream>
#include <vector>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
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
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

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

void run_child(UniqueFd read_end) {
    constexpr int target_fd = 3;
    if (read_end.get() != target_fd) {
        if (::dup2(read_end.get(), target_fd) < 0) {
            std::exit(EXIT_FAILURE);
        }
        read_end.reset();
    }

    // Знімаємо прапорець FD_CLOEXEC з дескриптора target_fd
    int flags = ::fcntl(target_fd, F_GETFD);
    ::fcntl(target_fd, F_SETFD, flags & ~FD_CLOEXEC);

    char *const clean_env[] = {
        const_cast<char*>("PATH=/usr/bin:/bin"),
        const_cast<char*>("LANG=C.UTF-8"),
        nullptr
    };

    char *const child_argv[] = {
        const_cast<char*>("/usr/local/bin/worker"),
        const_cast<char*>("--secret-fd=3"),
        nullptr
    };

    ::execve(child_argv[0], child_argv, clean_env);
    std::exit(EXIT_FAILURE);
}

int main() {
    int raw_fds[2];
    if (::pipe2(raw_fds, O_CLOEXEC) < 0) {
        std::cerr << "Помилка pipe2\n";
        return EXIT_FAILURE;
    }

    UniqueFd read_pipe(raw_fds[0]);
    UniqueFd write_pipe(raw_fds[1]);

    pid_t pid = ::fork();
    if (pid < 0) {
        std::cerr << "Помилка fork\n";
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        write_pipe.reset(); // Закриваємо записуючий дескриптор
        run_child(std::move(read_pipe));
    } else {
        read_pipe.reset();  // Закриваємо читаючий дескриптор
        
        constexpr std::string_view secret = "SuperSecret_Database_Token_2026";
        ::write(write_pipe.get(), secret.data(), secret.size());
        write_pipe.reset(); // Закриття викликає EOF у дочірньому процесі

        ::waitpid(pid, nullptr, 0);
    }
    return EXIT_SUCCESS;
}
