#include <iostream>
#include <vector>
#include <string_view>
#include <system_error>
#include <memory>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd) : fd_(fd) {}
    ~ScopedFd() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct RedirectionOptions {
    std::string_view infile;
    std::string_view outfile;
    bool append{false};
    bool merge_stderr{false};
};

class MiniRunner {
public:
    static int run(const std::vector<std::string_view>& raw_args) {
        std::vector<char*> exec_args;
        RedirectionOptions opts;

        for (size_t i = 0; i < raw_args.size(); ++i) {
            if (raw_args[i] == "<" && i + 1 < raw_args.size()) {
                opts.infile = raw_args[++i];
            } else if (raw_args[i] == ">" && i + 1 < raw_args.size()) {
                opts.outfile = raw_args[++i];
                opts.append = false;
            } else if (raw_args[i] == ">>" && i + 1 < raw_args.size()) {
                opts.outfile = raw_args[++i];
                opts.append = true;
            } else if (raw_args[i] == "2>&1") {
                opts.merge_stderr = true;
            } else {
                exec_args.push_back(const_cast<char*>(raw_args[i].data()));
            }
        }
        exec_args.push_back(nullptr);

        if (exec_args.size() <= 1) {
            std::cerr << "Помилка: відсутня команда\n";
            return 1;
        }

        pid_t pid = ::fork();
        if (pid < 0) {
            std::perror("fork");
            return 1;
        }

        if (pid == 0) {
            child_execute(exec_args.data(), opts);
        }

        int status{0};
        if (::waitpid(pid, &status, 0) < 0) {
            std::perror("waitpid");
            return 1;
        }

        if (WIFEXITED(status)) {
            std::cout << "[Процес завершено з кодом: " << WEXITSTATUS(status) << "]\n";
        }
        return 0;
    }

private:
    [[noreturn]] static void child_execute(char** argv, const RedirectionOptions& opts) {
        if (!opts.infile.empty()) {
            ScopedFd fd_in(::open(opts.infile.data(), O_RDONLY));
            if (!fd_in.valid()) {
                std::perror("open infile");
                std::exit(EXIT_FAILURE);
            }
            if (::dup2(fd_in.get(), STDIN_FILENO) < 0) {
                std::perror("dup2 stdin");
                std::exit(EXIT_FAILURE);
            }
        }

        if (!opts.outfile.empty()) {
            int flags = O_WRONLY | O_CREAT | (opts.append ? O_APPEND : O_TRUNC);
            ScopedFd fd_out(::open(opts.outfile.data(), flags, 0644));
            if (!fd_out.valid()) {
                std::perror("open outfile");
                std::exit(EXIT_FAILURE);
            }
            if (::dup2(fd_out.get(), STDOUT_FILENO) < 0) {
                std::perror("dup2 stdout");
                std::exit(EXIT_FAILURE);
            }
        }

        if (opts.merge_stderr) {
            if (::dup2(STDOUT_FILENO, STDERR_FILENO) < 0) {
                std::perror("dup2 merge stderr");
                std::exit(EXIT_FAILURE);
            }
        }

        ::execvp(argv[0], argv);
        std::perror("execvp");
        std::exit(EXIT_FAILURE);
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <команда> [перенаправлення...]\n";
        return 1;
    }

    std::vector<std::string_view> args(argv + 1, argv + argc);
    return MiniRunner::run(args);
}
