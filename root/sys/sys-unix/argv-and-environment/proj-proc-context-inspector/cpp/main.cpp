// Приклад на C++20: Системний інспектор контексту з використанням RAII
#include <iostream>
#include <vector>
#include <string_view>
#include <span >
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/auxv.h>
#include <sys/wait.h>

extern char **environ;

class SystemContextInspector {
public:
    static void inspect_stack(int argc, char *argv[]) {
        std::cout << "=== C++ System Context Inspector (PID: " << ::getpid() << ") ===\n";
        std::cout << "argc: " << argc << "\n";

        std::span<char*> arg_span(argv, static_cast<size_t>(argc));
        for (size_t i = 0; i < arg_span.size(); ++i) {
            std::cout << "  argv[" << i << "] (" << static_cast<void*>(arg_span[i]) 
                      << ") -> " << arg_span[i] << "\n";
        }

        std::cout << "\n--- Environment Snapshot (First 5) ---\n";
        size_t count = 0;
        for (char **env = environ; *env != nullptr && count < 5; ++env, ++count) {
            std::cout << "  env[" << count << "] (" << static_cast<void*>(*env) 
                      << ") -> " << *env << "\n";
        }

        std::cout << "\n--- Auxiliary Vector (Kernel Metadata) ---\n";
        std::cout << "  AT_PAGESZ : " << ::getauxval(AT_PAGESZ) << " bytes\n";
        std::cout << "  AT_ENTRY  : 0x" << std::hex << ::getauxval(AT_ENTRY) << std::dec << "\n";
        std::cout << "  AT_SECURE : " << ::getauxval(AT_SECURE) << "\n";

        long arg_max = ::sysconf(_SC_ARG_MAX);
        std::cout << "  ARG_MAX   : " << arg_max << " bytes\n\n";
    }

    static void run_cloexec_experiment() {
        std::cout << "=== Running C++ Descriptor Leakage Experiment ===\n";

        // RAII обгортка для файлового дескриптора
        struct ScopedDescriptor {
            int fd = -1;
            ~ScopedDescriptor() {
                if (fd >= 0) ::close(fd);
            }
        };

        ScopedDescriptor normal_fd{ ::open("/dev/null", O_RDONLY) };
        ScopedDescriptor cloexec_fd{ ::open("/dev/null", O_RDONLY | O_CLOEXEC) };

        if (normal_fd.fd < 0 || cloexec_fd.fd < 0) {
            throw std::system_error(errno, std::generic_category(), "open failed");
        }

        std::cout << "Normal FD  : " << normal_fd.fd << " (will survive execve)\n";
        std::cout << "CLOEXEC FD : " << cloexec_fd.fd << " (will close on execve)\n";

        pid_t pid = ::fork();
        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }

        if (pid == 0) {
            char *child_args[] = { const_cast<char*>("true"), nullptr };
            ::execve("/bin/true", child_args, environ);
            ::_exit(127);
        }

        int status = 0;
        ::waitpid(pid, &status, 0);
        std::cout << "Child completed with exit code: " << WEXITSTATUS(status) << "\n";
    }
};

int main(int argc, char *argv[]) {
    try {
        SystemContextInspector::inspect_stack(argc, argv);
        if (argc == 1) {
            SystemContextInspector::run_cloexec_experiment();
        }
    } catch (const std::exception& ex) {
        std::cerr << "Fatal Error: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
