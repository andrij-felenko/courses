#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <syscall.h>
#include <unistd.h>
#include <iostream>
#include <vector>
#include <string>
#include <system_error>
#include <cerrno>

/* Об'єктно-орієнтована реалізація C++ трасувальника */
class PtraceTracer {
public:
    explicit PtraceTracer(pid_t childPid) : pid_(childPid) {}

    void run() {
        int status = 0;
        if (waitpid(pid_, &status, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося виконати початковий waitpid");
        }

        // Налаштовуємо розширені опції трасування ptrace
        if (ptrace(PTRACE_SETOPTIONS, pid_, 0, PTRACE_O_TRACESYSGOOD | PTRACE_O_EXITKILL) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка встановлення PTRACE_SETOPTIONS");
        }

        std::cout << "[C++ Tracer] Моніторинг активовано для PID: " << pid_ << "\n";

        bool isEnter = true;
        while (true) {
            if (ptrace(PTRACE_SYSCALL, pid_, 0, 0) < 0) {
                if (errno == ESRCH) break; // Процес завершився
                throw std::system_error(errno, std::generic_category(), "PTRACE_SYSCALL failed");
            }

            if (waitpid(pid_, &status, 0) < 0) {
                break;
            }

            if (WIFEXITED(status)) {
                std::cout << "[C++ Tracer] Процес нормалізовано завершився з кодом: "
                          << WEXITSTATUS(status) << "\n";
                break;
            }
            if (WIFSIGNALED(status)) {
                std::cout << "[C++ Tracer] Процес вбито сигналом: "
                          << WTERMSIG(status) << "\n";
                break;
            }

            if (WIFSTOPPED(status) && WSTOPSIG(status) == (SIGTRAP | 0x80)) {
                user_regs_struct regs{};
                if (ptrace(PTRACE_GETREGS, pid_, 0, &regs) < 0) {
                    break;
                }

                if (isEnter) {
                    std::cout << "[sys_enter] Виклик #" << regs.orig_rax
                              << " (rdi: 0x" << std::hex << regs.rdi
                              << ", rsi: 0x" << regs.rsi << std::dec << ")\n";
                    isEnter = false;
                } else {
                    std::cout << "[sys_exit ] Виклик #" << regs.orig_rax
                              << " -> Результат: " << static_cast<long long>(regs.rax) << "\n";
                    isEnter = true;
                }
            }
        }
    }

private:
    pid_t pid_;
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <програма> [аргументи...]\n";
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }

    if (pid == 0) {
        if (ptrace(PTRACE_TRACEME, 0, nullptr, nullptr) < 0) {
            perror("PTRACE_TRACEME");
            _exit(1);
        }
        raise(SIGSTOP);
        execvp(argv[1], &argv[1]);
        perror("execvp");
        _exit(1);
    }

    try {
        PtraceTracer tracer(pid);
        tracer.run();
    } catch (const std::exception& e) {
        std::cerr << "Критична помилка трасувальника: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
