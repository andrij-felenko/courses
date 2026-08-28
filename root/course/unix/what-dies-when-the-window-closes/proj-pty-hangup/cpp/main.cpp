#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <memory>
#include <chrono>
#include <thread>
#include <system_error>
#include <csignal>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/wait.h>

namespace pty_demo {

static volatile std::sig_atomic_t g_hup_flag = 0;

void signal_handler(int sig) noexcept {
    if (sig == SIGHUP) {
        g_hup_flag = 1;
    }
}

class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() noexcept { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

private:
    int fd_;
};

void run_child(std::string_view slave_path) {
    if (::setsid() < 0) {
        std::exit(EXIT_FAILURE);
    }

    FileDescriptor sfd(::open(slave_path.data(), O_RDWR));
    if (!sfd.valid()) {
        std::exit(EXIT_FAILURE);
    }

    if (::ioctl(sfd.get(), TIOCSCTTY, 0) < 0) {
        std::exit(EXIT_FAILURE);
    }

    ::dup2(sfd.get(), STDIN_FILENO);
    ::dup2(sfd.get(), STDOUT_FILENO);
    ::dup2(sfd.get(), STDERR_FILENO);

    struct sigaction sa{};
    sa.sa_handler = signal_handler;
    ::sigemptyset(&sa.sa_mask);
    ::sigaction(SIGHUP, &sa, nullptr);

    std::ofstream log_stream("/tmp/pty_child.log", std::ios::out | std::ios::trunc);
    if (!log_stream.is_open()) {
        std::exit(EXIT_FAILURE);
    }

    const pid_t my_pid = ::getpid();
    log_stream << "[CHILD " << my_pid << "] Сеанс створено. Очікування подій...\n" << std::flush;

    for (int i = 0; i < 30; ++i) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        if (g_hup_flag) {
            log_stream << "[CHILD " << my_pid << "] Отримано сигнал SIGHUP від ядра!\n";

            int flags = ::fcntl(STDIN_FILENO, F_GETFL, 0);
            ::fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);
            std::array<char, 64> buffer{};
            const ssize_t nr = ::read(STDIN_FILENO, buffer.data(), buffer.size());
            log_stream << "[CHILD " << my_pid << "] Спроба read(0): повернуто " << nr
                       << " (errno=" << errno << ": " << std::strerror(errno) << ")\n";

            constexpr std::string_view msg = "test\n";
            const ssize_t nw = ::write(STDOUT_FILENO, msg.data(), msg.size());
            log_stream << "[CHILD " << my_pid << "] Спроба write(1): повернуто " << nw
                       << " (errno=" << errno << ": " << std::strerror(errno) << ")\n";

            log_stream << "[CHILD " << my_pid << "] Завершення роботи після розриву.\n" << std::flush;
            std::exit(EXIT_SUCCESS);
        }
    }

    log_stream << "[CHILD " << my_pid << "] Таймаут очікування.\n" << std::flush;
    std::exit(EXIT_SUCCESS);
}

} // namespace pty_demo

int main() {
    pty_demo::FileDescriptor mfd(::posix_openpt(O_RDWR | O_NOCTTY));
    if (!mfd.valid()) {
        std::cerr << "Помилка відкриття posix_openpt\n";
        return EXIT_FAILURE;
    }

    if (::grantpt(mfd.get()) < 0 || ::unlockpt(mfd.get()) < 0) {
        std::cerr << "Помилка grantpt / unlockpt\n";
        return EXIT_FAILURE;
    }

    const char* pts_name = ::ptsname(mfd.get());
    if (!pts_name) {
        std::cerr << "Помилка отримання імені ptsname\n";
        return EXIT_FAILURE;
    }

    std::cout << "[PARENT] PTY Master відкрито (fd=" << mfd.get() << "). Slave: " << pts_name << '\n';

    const pid_t child_pid = ::fork();
    if (child_pid < 0) {
        std::cerr << "Помилка fork\n";
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        mfd.reset();
        pty_demo::run_child(pts_name);
    }

    std::cout << "[PARENT] Дочірній процес запущено (PID=" << child_pid << "). Вікно відкрите...\n";
    std::this_thread::sleep_for(std::chrono::seconds(1));

    std::cout << "[PARENT] Закриваємо master_fd (" << mfd.get() << "), емулюючи закриття вікна...\n";
    mfd.reset();

    int status = 0;
    ::waitpid(child_pid, &status, 0);

    if (WIFEXITED(status)) {
        std::cout << "[PARENT] Дочірній процес завершився із кодом " << WEXITSTATUS(status) << ".\n";
    } else if (WIFSIGNALED(status)) {
        std::cout << "[PARENT] Дочірній процес вбито сигналом " << WTERMSIG(status) << ".\n";
    }

    std::cout << "\n--- Протокол дочірнього процесу (/tmp/pty_child.log) ---\n";
    std::ifstream log_file("/tmp/pty_child.log");
    if (log_file.is_open()) {
        std::string line;
        while (std::getline(log_file, line)) {
            std::cout << line << '\n';
        }
        log_file.close();
        ::unlink("/tmp/pty_child.log");
    }

    return EXIT_SUCCESS;
}
