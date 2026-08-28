#include <iostream>
#include <system_error>
#include <unistd.h>
#include <sys/wait.h>

// RAII-обгортка для керування дочірнім процесом
class ScopedProcess {
public:
    explicit ScopedProcess(pid_t pid) : pid_(pid) {}

    ~ScopedProcess() {
        if (pid_ > 0) {
            int wstatus = 0;
            ::waitpid(pid_, &wstatus, 0);
        }
    }

    ScopedProcess(const ScopedProcess&) = delete;
    ScopedProcess& operator=(const ScopedProcess&) = delete;

    [[nodiscard]] pid_t id() const noexcept { return pid_; }

private:
    pid_t pid_;
};

int main() {
    pid_t raw_pid = ::fork();

    if (raw_pid < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка fork");
    }

    if (raw_pid == 0) {
        std::cout << "[Дочірній процес] PID = " << ::getpid()
                  << ", батьківський PID = " << ::getppid() << '\n';
        ::_exit(42);
    }

    ScopedProcess child(raw_pid);
    std::cout << "[Батьківський процес] Очікування нащадка PID = "
              << child.id() << " через RAII\n";

    return 0;
}
