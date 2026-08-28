#include <iostream>
#include <string_view>
#include <system_error>
#include <expected>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>

class TraceeProcess {
    pid_t pid_{-1};

    void release() noexcept {
        if (pid_ > 0) {
            int status;
            ptrace(PTRACE_DETACH, pid_, nullptr, nullptr);
            waitpid(pid_, &status, WNOHANG);
        }
        pid_ = -1;
    }

public:
    explicit TraceeProcess(pid_t pid) : pid_(pid) {}

    ~TraceeProcess() { release(); }

    TraceeProcess(const TraceeProcess&) = delete;
    TraceeProcess& operator=(const TraceeProcess&) = delete;

    TraceeProcess(TraceeProcess&& other) noexcept : pid_(other.pid_) {
        other.pid_ = -1;
    }

    TraceeProcess& operator=(TraceeProcess&& other) noexcept {
        if (this != &other) {
            release();               /* спершу відпускаємо власний процес */
            pid_ = other.pid_;
            other.pid_ = -1;
        }
        return *this;
    }

    [[nodiscard]] pid_t pid() const noexcept { return pid_; }
};

class SyscallTracer {
public:
    static std::expected<void, std::string_view> run(char* const argv[]) {
        pid_t pid = fork();
        if (pid < 0) {
            return std::unexpected("Не вдалося виконати fork()");
        }

        if (pid == 0) {
            if (ptrace(PTRACE_TRACEME, 0, nullptr, nullptr) < 0) {
                std::perror("PTRACE_TRACEME failed");
                std::_Exit(EXIT_FAILURE);
            }
            execvp(argv[0], argv);
            std::perror("execvp failed");
            std::_Exit(EXIT_FAILURE);
        }

        TraceeProcess tracee(pid);
        int status = 0;
        waitpid(tracee.pid(), &status, 0);

        if (ptrace(PTRACE_SETOPTIONS, tracee.pid(), 0, PTRACE_O_TRACESYSGOOD) < 0) {
            return std::unexpected("Помилка при встановленні PTRACE_O_TRACESYSGOOD");
        }

        bool is_entry = true;

        while (true) {
            if (ptrace(PTRACE_SYSCALL, tracee.pid(), 0, 0) < 0) {
                break;
            }

            waitpid(tracee.pid(), &status, 0);

            if (WIFEXITED(status) || WIFSIGNALED(status)) {
                std::cout << "[Процес " << tracee.pid() << " завершив роботу]\n";
                break;
            }

            if (WIFSTOPPED(status) && WSTOPSIG(status) == (SIGTRAP | 0x80)) {
                struct user_regs_struct regs{};
                if (ptrace(PTRACE_GETREGS, tracee.pid(), 0, &regs) < 0) {
                    return std::unexpected("Помилка зчитування регістрів через PTRACE_GETREGS");
                }

                if (is_entry) {
                    std::cout << "[SYSCALL Entry] № " << regs.orig_rax 
                              << " (rdi: 0x" << std::hex << regs.rdi 
                              << ", rsi: 0x" << regs.rsi 
                              << ", rdx: 0x" << regs.rdx << std::dec << ")\n";
                    is_entry = false;
                } else {
                    std::cout << "[SYSCALL Exit ] № " << regs.orig_rax 
                              << " -> Код повернення: " << static_cast<long long>(regs.rax) << "\n";
                    is_entry = true;
                }
            }
        }
        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <програма_для_запуску> [аргументи...]\n";
        return EXIT_FAILURE;
    }

    auto result = SyscallTracer::run(&argv[1]);
    if (!result) {
        std::cerr << "Помилка: " << result.error() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
