// mini_shell.cpp — Ідіоматична C++20 реалізація з RAII-обгортками дескрипторів
#include <iostream>
#include <string>
#include <vector>
#include <string_view>
#include <sstream>
#include <memory>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

namespace shell {

// RAII обгортка для безпечного керування файловими дескрипторами POSIX
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

// Розбиття рядка на токени без сирого malloc
static std::vector<std::string> tokenize(std::string_view line) {
    std::vector<std::string> tokens;
    std::istringstream iss{std::string(line)};
    std::string token;
    while (iss >> token) {
        tokens.push_back(token);
    }
    return tokens;
}

// Перетворення std::vector<std::string> у char* array для execvp
class ExecArgs {
    std::vector<char*> ptrs_;
public:
    explicit ExecArgs(const std::vector<std::string>& args) {
        ptrs_.reserve(args.size() + 1);
        for (const auto& arg : args) {
            ptrs_.push_back(const_cast<char*>(arg.c_str()));
        }
        ptrs_.push_back(nullptr);
    }

    [[nodiscard]] char** data() noexcept { return ptrs_.data(); }
};

// Перевірка та виконання вбудованих команд
static bool handle_builtin(const std::vector<std::string>& args) {
    if (args.empty()) return true;

    if (args[0] == "exit") {
        std::exit(0);
    }
    if (args[0] == "cd") {
        std::string dir = (args.size() > 1) ? args[1] : (::getenv("HOME") ? ::getenv("HOME") : "/");
        if (::chdir(dir.c_str()) != 0) {
            std::perror("mini-shell: cd failed");
        }
        return true;
    }
    return false;
}

// Виконання одиночної команди
static void execute_simple(const std::vector<std::string>& args) {
    ExecArgs exec_args{args};
    pid_t pid = ::fork();
    if (pid < 0) {
        std::perror("mini-shell: fork failed");
        return;
    }
    if (pid == 0) {
        ::execvp(exec_args.data()[0], exec_args.data());
        std::perror("mini-shell: execvp failed");
        std::exit(127);
    }

    int status = 0;
    ::waitpid(pid, &status, 0);
}

// Виконання конвеєра з двох команд з автоматичним закриттям RAII дескрипторів
static void execute_pipeline(const std::vector<std::string>& cmd1, const std::vector<std::string>& cmd2) {
    int pipe_raw[2];
    if (::pipe(pipe_raw) < 0) {
        std::perror("mini-shell: pipe failed");
        return;
    }

    UniqueFd read_end{pipe_raw[0]};
    UniqueFd write_end{pipe_raw[1]};

    pid_t pid1 = ::fork();
    if (pid1 == 0) {
        ::dup2(write_end.get(), STDOUT_FILENO);
        read_end.reset();
        write_end.reset();

        ExecArgs exec_args1{cmd1};
        ::execvp(exec_args1.data()[0], exec_args1.data());
        std::perror("mini-shell: execvp cmd1 failed");
        std::exit(127);
    }

    pid_t pid2 = ::fork();
    if (pid2 == 0) {
        ::dup2(read_end.get(), STDIN_FILENO);
        read_end.reset();
        write_end.reset();

        ExecArgs exec_args2{cmd2};
        ::execvp(exec_args2.data()[0], exec_args2.data());
        std::perror("mini-shell: execvp cmd2 failed");
        std::exit(127);
    }

    // Завдяки RAII дескриптори батька закриються автоматично при виході UniqueFd з області видимості
    read_end.reset();
    write_end.reset();

    int status1 = 0, status2 = 0;
    ::waitpid(pid1, &status1, 0);
    ::waitpid(pid2, &status2, 0);
}

} // namespace shell

int main() {
    std::string line;
    while (true) {
        std::cout << "mini-shell> " << std::flush;
        if (!std::getline(std::cin, line)) {
            break;
        }

        auto pipe_pos = line.find('|');
        if (pipe_pos != std::string::npos) {
            auto left = line.substr(0, pipe_pos);
            auto right = line.substr(pipe_pos + 1);

            auto cmd1 = shell::tokenize(left);
            auto cmd2 = shell::tokenize(right);

            if (!cmd1.empty() && !cmd2.empty()) {
                shell::execute_pipeline(cmd1, cmd2);
            }
        } else {
            auto args = shell::tokenize(line);
            if (!args.empty() && !shell::handle_builtin(args)) {
                shell::execute_simple(args);
            }
        }
    }
    std::cout << "\nGoodbye!\n";
    return 0;
}
