#include <iostream>
#include <system_error>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>

void launch_target_under_trace_cpp(const char* binary_path) {
    const pid_t pid = ::fork();
    if (pid < 0) {
        throw std::system_error(errno, std::generic_category(), "fork failed");
    }

    if (pid == 0) {
        if (::ptrace(PTRACE_TRACEME, 0, nullptr, nullptr) < 0) {
            std::perror("ptrace(TRACEME) failed");
            std::_Exit(EXIT_FAILURE);
        }
        ::raise(SIGSTOP);
        ::execl(binary_path, binary_path, nullptr);
        std::perror("execl failed");
        std::_Exit(EXIT_FAILURE);
    }

    int status = 0;
    if (::waitpid(pid, &status, 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "waitpid failed");
    }

    if (WIFSTOPPED(status)) {
        std::cout << "[Tracer] Tracee stopped successfully, signal: " 
                  << WSTOPSIG(status) << "\n";
    }

    ::ptrace(PTRACE_CONT, pid, nullptr, nullptr);
}
