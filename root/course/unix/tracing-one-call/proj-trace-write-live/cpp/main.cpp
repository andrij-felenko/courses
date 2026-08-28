#include <unistd.h>
#include <fcntl.h>
#include <iostream>
#include <string_view>
#include <system_error>

class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) : fd_(fd) {}
    ~FileDescriptor() { if (fd_ >= 0) ::close(fd_); }
    int get() const noexcept { return fd_; }
    bool valid() const noexcept { return fd_ >= 0; }
};

int main()
{
    constexpr std::string_view msg = "HELLO\n";
    pid_t pid = getpid();

    std::cout << "PID тестового процесу: " << pid << '\n';
    std::cout << "Натисніть Enter для запису в TTY (stdout)...\n";
    std::cin.get();

    /* 1. Запис у термінал (псевдоконсоль) */
    ssize_t ret_tty = ::write(STDOUT_FILENO, msg.data(), msg.size());
    if (ret_tty < 0) {
        auto ec = std::error_code(errno, std::generic_category());
        std::cerr << "Помилка запису в TTY: " << ec.message() << '\n';
        return 1;
    }

    std::cout << "Натисніть Enter для запису у файл на диску (/tmp/trace_test.txt)...\n";
    std::cin.get();

    /* 2. Запис у звичайний файл на диску */
    FileDescriptor file(::open("/tmp/trace_test.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644));
    if (!file.valid()) {
        auto ec = std::error_code(errno, std::generic_category());
        std::cerr << "Помилка відкриття файлу: " << ec.message() << '\n';
        return 1;
    }

    ssize_t ret_file = ::write(file.get(), msg.data(), msg.size());
    if (ret_file < 0) {
        auto ec = std::error_code(errno, std::generic_category());
        std::cerr << "Помилка запису у файл: " << ec.message() << '\n';
        return 1;
    }

    std::cout << "Запис завершено успішно (TTY: " << ret_tty << " Б, Диск: " << ret_file << " Б).\n";
    return 0;
}
