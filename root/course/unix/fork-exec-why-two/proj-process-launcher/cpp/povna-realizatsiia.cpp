#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <system_error>
#include <memory>
#include <span>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <signal.h>
#include <sys/syscall.h>

struct ProcessConfigOptions {
    std::string executable;
    std::vector<std::string> argv;
    std::optional<std::vector<std::string>> envp;
    std::optional<std::string> working_dir;
    int stdin_fd = -1;
    int stdout_fd = -1;
    int stderr_fd = -1;
    rlim_t max_memory_bytes = 0;
    rlim_t max_cpu_seconds = 0;
};

class DiagnosticPipeRAII {
public:
    DiagnosticPipeRAII() {
        if (pipe2(fds_, O_CLOEXEC) == -1) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }
    }
    ~DiagnosticPipeRAII() noexcept {
        close_read();
        close_write();
    }
    DiagnosticPipeRAII(const DiagnosticPipeRAII&) = delete;
    DiagnosticPipeRAII& operator=(const DiagnosticPipeRAII&) = delete;

    void close_read() noexcept {
        if (fds_[0] != -1) { close(fds_[0]); fds_[0] = -1; }
    }
    void close_write() noexcept {
        if (fds_[1] != -1) { close(fds_[1]); fds_[1] = -1; }
    }
    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }

private:
    int fds_[2] = {-1, -1};
};

static void close_fds_above(int min_fd) noexcept {
#if defined(__NR_close_range)
    if (syscall(__NR_close_range, min_fd, ~0U, 0) == 0) {
        return;
    }
#endif
    long max_fd = sysconf(_SC_OPEN_MAX);
    if (max_fd < 0 || max_fd > 4096) max_fd = 4096;
    for (int fd = min_fd; fd < max_fd; ++fd) {
        close(fd);
    }
}

std::expected<pid_t, std::error_code> launch_process_cpp(const ProcessConfigOptions& opt) {
    if (opt.executable.empty() || opt.argv.empty()) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    DiagnosticPipeRAII err_pipe;

    pid_t pid = fork();
    if (pid < 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }

    if (pid == 0) {
        /* ДОЧІРНІЙ ПРОЦЕС */
        err_pipe.close_read();

        auto report_and_exit = [&](int err_code) noexcept {
            ssize_t w = write(err_pipe.write_fd(), &err_code, sizeof(err_code));
            (void)w;
            err_pipe.close_write();
            _exit(127);
        };

        if (setpgid(0, 0) == -1) report_and_exit(errno);

        if (opt.working_dir) {
            if (chdir(opt.working_dir->c_str()) == -1) report_and_exit(errno);
        }

        if (opt.max_memory_bytes > 0) {
            struct rlimit lim{ opt.max_memory_bytes, opt.max_memory_bytes };
            if (setrlimit(RLIMIT_AS, &lim) == -1) report_and_exit(errno);
        }

        if (opt.max_cpu_seconds > 0) {
            struct rlimit lim{ opt.max_cpu_seconds, opt.max_cpu_seconds };
            if (setrlimit(RLIMIT_CPU, &lim) == -1) report_and_exit(errno);
        }

        if (opt.stdin_fd >= 0 && opt.stdin_fd != STDIN_FILENO) {
            if (dup2(opt.stdin_fd, STDIN_FILENO) == -1) report_and_exit(errno);
        }
        if (opt.stdout_fd >= 0 && opt.stdout_fd != STDOUT_FILENO) {
            if (dup2(opt.stdout_fd, STDOUT_FILENO) == -1) report_and_exit(errno);
        }
        if (opt.stderr_fd >= 0 && opt.stderr_fd != STDERR_FILENO) {
            if (dup2(opt.stderr_fd, STDERR_FILENO) == -1) report_and_exit(errno);
        }

        sigset_t mask;
        sigemptyset(&mask);
        if (sigprocmask(SIG_SETMASK, &mask, nullptr) == -1) report_and_exit(errno);

        close_fds_above(3);

        std::vector<char*> c_argv;
        c_argv.reserve(opt.argv.size() + 1);
        for (const auto& arg : opt.argv) {
            c_argv.push_back(const_cast<char*>(arg.c_str()));
        }
        c_argv.push_back(nullptr);

        if (opt.envp) {
            std::vector<char*> c_envp;
            c_envp.reserve(opt.envp->size() + 1);
            for (const auto& env : *opt.envp) {
                c_envp.push_back(const_cast<char*>(env.c_str()));
            }
            c_envp.push_back(nullptr);
            execvpe(opt.executable.c_str(), c_argv.data(), c_envp.data());
        } else {
            execvp(opt.executable.c_str(), c_argv.data());
        }

        report_and_exit(errno);
    }

    /* БАТЬКІВСЬКИЙ ПРОЦЕС */
    err_pipe.close_write();

    int child_error = 0;
    ssize_t bytes_read = 0;
    do {
        bytes_read = read(err_pipe.read_fd(), &child_error, sizeof(child_error));
    } while (bytes_read == -1 && errno == EINTR);

    err_pipe.close_read();

    if (bytes_read == sizeof(child_error)) {
        waitpid(pid, nullptr, 0);
        return std::unexpected(std::make_error_code(static_cast<std::errc>(child_error)));
    }

    if (bytes_read == 0) {
        return pid;
    }

    waitpid(pid, nullptr, 0);
    return std::unexpected(std::make_error_code(std::errc::io_error));
}
