#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

namespace sys {

// RAII-обгортка для безпечного керування файловими дескрипторами ядра
class FileDescriptor {
    int fd_{-1};
public:
    constexpr FileDescriptor() noexcept = default;
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.release()) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
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

class PipelineExecutor {
public:
    // Запуск програми з перенаправленням stdout у файл
    static void redirect_stdout_to_file(const std::string& cmd,
                                        const std::vector<std::string>& args,
                                        const std::string& output_filepath) {
        // 1. Очищення буферів C++ streams та C libc перед fork
        std::cout.flush();
        std::cerr.flush();
        ::fflush(nullptr);

        pid_t pid = ::fork();
        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }

        if (pid == 0) {
            // Дочірній процес
            FileDescriptor file_fd(::open(output_filepath.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644));
            if (!file_fd.valid()) {
                ::perror("open output file failed");
                ::_exit(1);
            }

            if (::dup2(file_fd.get(), STDOUT_FILENO) < 0) {
                ::perror("dup2 failed");
                ::_exit(1);
            }
            file_fd.reset(); // RAII закриває початковий FD

            // Формуємо масив аргументів C-style для execvp
            std::vector<char*> c_argv;
            c_argv.reserve(args.size() + 2);
            c_argv.push_back(const_cast<char*>(cmd.c_str()));
            for (const auto& arg : args) {
                c_argv.push_back(const_cast<char*>(arg.c_str()));
            }
            c_argv.push_back(nullptr);

            ::execvp(cmd.c_str(), c_argv.data());
            ::perror("execvp failed");
            ::_exit(127);
        }

        int status = 0;
        while (::waitpid(pid, &status, 0) < 0) {
            if (errno != EINTR) {
                throw std::system_error(errno, std::generic_category(), "waitpid failed");
            }
        }

        if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
            throw std::runtime_error("Process exited with non-zero code: " + 
                                     std::to_string(WEXITSTATUS(status)));
        }
    }

    // Запуск двох програм через міжпроцесний канал (cmd1 | cmd2)
    static void execute_pipeline(const std::string& cmd1, const std::vector<std::string>& args1,
                                 const std::string& cmd2, const std::vector<std::string>& args2) {
        std::cout.flush();
        std::cerr.flush();
        ::fflush(nullptr);

        int raw_pipe[2];
        if (::pipe(raw_pipe) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe failed");
        }

        FileDescriptor pipe_read(raw_pipe[0]);
        FileDescriptor pipe_write(raw_pipe[1]);

        pid_t pid1 = ::fork();
        if (pid1 < 0) {
            throw std::system_error(errno, std::generic_category(), "fork pid1 failed");
        }

        if (pid1 == 0) {
            pipe_read.reset(); // Закриваємо читальний кінець

            if (::dup2(pipe_write.get(), STDOUT_FILENO) < 0) {
                ::perror("dup2 write failed");
                ::_exit(1);
            }
            pipe_write.reset();

            std::vector<char*> c_argv1;
            c_argv1.push_back(const_cast<char*>(cmd1.c_str()));
            for (const auto& a : args1) c_argv1.push_back(const_cast<char*>(a.c_str()));
            c_argv1.push_back(nullptr);

            ::execvp(cmd1.c_str(), c_argv1.data());
            ::_exit(127);
        }

        pid_t pid2 = ::fork();
        if (pid2 < 0) {
            throw std::system_error(errno, std::generic_category(), "fork pid2 failed");
        }

        if (pid2 == 0) {
            pipe_write.reset(); // Закриваємо писальний кінець

            if (::dup2(pipe_read.get(), STDIN_FILENO) < 0) {
                ::perror("dup2 read failed");
                ::_exit(1);
            }
            pipe_read.reset();

            std::vector<char*> c_argv2;
            c_argv2.push_back(const_cast<char*>(cmd2.c_str()));
            for (const auto& a : args2) c_argv2.push_back(const_cast<char*>(a.c_str()));
            c_argv2.push_back(nullptr);

            ::execvp(cmd2.c_str(), c_argv2.data());
            ::_exit(127);
        }

        // Батьківський процес закриває свої RAII дескриптори каналу
        pipe_read.reset();
        pipe_write.reset();

        int status1 = 0, status2 = 0;
        while (::waitpid(pid1, &status1, 0) < 0) {
            if (errno != EINTR) break;
        }
        while (::waitpid(pid2, &status2, 0) < 0) {
            if (errno != EINTR) break;
        }
    }
};

} // namespace sys

int main() {
    try {
        std::cout << "[C++] Виконання перенаправлення через RAII обгортку...\n";
        sys::PipelineExecutor::redirect_stdout_to_file("uname", {"-a"}, "system_info.txt");
        std::cout << "[C++] Успішно збережено систему в system_info.txt\n";

        std::cout << "[C++] Виконання C++ конвеєра: ls -la / | grep dev...\n";
        sys::PipelineExecutor::execute_pipeline("ls", {"-la", "/"}, "grep", {"dev"});
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
