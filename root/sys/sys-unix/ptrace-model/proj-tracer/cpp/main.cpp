#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <system_error>
#include <memory>
#include <cstdint>
#include <iomanip>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>

// Клас RAII для надійного управління життєвим циклом цільового процесу
class TracedProcess {
    pid_t pid_{-1};

public:
    explicit TracedProcess(pid_t pid) noexcept : pid_(pid) {}
    
    ~TracedProcess() {
        if (pid_ > 0) {
            int status = 0;
            if (::waitpid(pid_, &status, WNOHANG) == 0) {
                ::ptrace(PTRACE_KILL, pid_, nullptr, nullptr);
                ::waitpid(pid_, nullptr, 0);
            }
        }
    }

    TracedProcess(const TracedProcess&) = delete;
    TracedProcess& operator=(const TracedProcess&) = delete;
    TracedProcess(TracedProcess&& other) noexcept : pid_(other.pid_) { other.pid_ = -1; }
    TracedProcess& operator=(TracedProcess&& other) noexcept {
        if (this != &other) {
            pid_ = other.pid_;
            other.pid_ = -1;
        }
        return *this;
    }

    [[nodiscard]] pid_t get_pid() const noexcept { return pid_; }
};

class SyscallTracer {
    static constexpr std::string_view get_syscall_name(std::int64_t nr) noexcept {
        switch (nr) {
            case 0:   return "read";
            case 1:   return "write";
            case 2:   return "open";
            case 3:   return "close";
            case 9:   return "mmap";
            case 10:  return "mprotect";
            case 11:  return "munmap";
            case 12:  return "brk";
            case 59:  return "execve";
            case 231: return "exit_group";
            default:  return "unknown_syscall";
        }
    }

    static std::string read_remote_string(pid_t child, std::uint64_t addr, std::size_t max_len = 64) {
        std::string result;
        result.reserve(max_len);
        std::size_t bytes_read = 0;

        while (bytes_read < max_len) {
            errno = 0;
            const long val = ::ptrace(PTRACE_PEEKDATA, child, reinterpret_cast<void*>(addr + bytes_read), nullptr);
            if (val == -1 && errno != 0) {
                break;
            }
            const auto* p = reinterpret_cast<const char*>(&val);
            for (std::size_t i = 0; i < sizeof(long); ++i) {
                if (p[i] == '\0' || bytes_read >= max_len) {
                    return result;
                }
                result.push_back(p[i]);
                bytes_read++;
            }
        }
        return result;
    }

public:
    static void trace(pid_t child_pid) {
        TracedProcess process(child_pid);
        int status = 0;

        if (::waitpid(child_pid, &status, 0) < 0 || !WIFSTOPPED(status)) {
            throw std::system_error(errno, std::generic_category(), "Початкова зупинка tracee не вдалася");
        }

        if (::ptrace(PTRACE_SETOPTIONS, child_pid, nullptr, PTRACE_O_TRACESYSGOOD) < 0) {
            throw std::system_error(errno, std::generic_category(), "PTRACE_SETOPTIONS failed");
        }

        bool in_syscall = false;

        while (true) {
            if (::ptrace(PTRACE_SYSCALL, child_pid, nullptr, nullptr) < 0) {
                std::perror("PTRACE_SYSCALL failed");
                break;
            }

            if (::waitpid(child_pid, &status, 0) < 0) {
                break;
            }

            if (WIFEXITED(status)) {
                std::cout << "\n[Tracer] Процес завершився з кодом: " << WEXITSTATUS(status) << "\n";
                break;
            }

            if (WIFSIGNALED(status)) {
                std::cout << "\n[Tracer] Процес знищено сигналом: " << WTERMSIG(status) << "\n";
                break;
            }

            if (WIFSTOPPED(status)) {
                const int sig = WSTOPSIG(status);

                if (sig == (SIGTRAP | 0x80)) {
                    user_regs_struct regs{};
                    if (::ptrace(PTRACE_GETREGS, child_pid, nullptr, &regs) < 0) {
                        std::perror("PTRACE_GETREGS failed");
                        break;
                    }

                    if (!in_syscall) {
                        in_syscall = true;
                        const auto sys_nr = static_cast<std::int64_t>(regs.orig_rax);
                        std::cout << "[SYS_ENTER] " << std::left << std::setw(12) 
                                  << get_syscall_name(sys_nr)
                                  << " (arg1=0x" << std::hex << regs.rdi
                                  << ", arg2=0x" << regs.rsi
                                  << ", arg3=0x" << regs.rdx << std::dec << ")";

                        if (sys_nr == 1 && regs.rsi != 0) {
                            const auto str = read_remote_string(child_pid, regs.rsi);
                            std::cout << " [buf=\"" << str << "\"]";
                        }
                        std::cout.flush();
                    } else {
                        in_syscall = false;
                        const auto res = static_cast<std::int64_t>(regs.rax);
                        std::cout << " = " << res << "\n";
                    }
                } else {
                    std::cout << "\n[Tracer] Сигнал зупинки: " << sig << "\n";
                }
            }
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <програма> [аргументи...]\n";
        return EXIT_FAILURE;
    }

    const pid_t pid = ::fork();
    if (pid < 0) {
        std::perror("fork failed");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        if (::ptrace(PTRACE_TRACEME, 0, nullptr, nullptr) < 0) {
            std::perror("PTRACE_TRACEME failed");
            std::_Exit(EXIT_FAILURE);
        }
        ::raise(SIGSTOP);
        ::execvp(argv[1], &argv[1]);
        std::perror("execvp failed");
        std::_Exit(EXIT_FAILURE);
    }

    try {
        SyscallTracer::trace(pid);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка трасування: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
