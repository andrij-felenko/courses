#include <iostream>
#include <string_view>
#include <array>
#include <system_error>
#include <span>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

class FileDescriptor {
    int m_fd = -1;
public:
    explicit FileDescriptor(int fd) noexcept : m_fd(fd) {}
    ~FileDescriptor() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

void inspect_and_process_descriptor(int fd)
{
    struct stat st{};
    if (::fstat(fd, &st) == -1) {
        auto ec = std::error_code(errno, std::generic_category());
        std::cerr << "fstat failed: " << ec.message() << '\n';
        return;
    }

    std::string_view type_name = "невідомий";
    bool is_seekable = false;

    if (S_ISREG(st.st_mode)) {
        type_name = "регулярний файл на диску";
        is_seekable = true;
    } else if (S_ISSOCK(st.st_mode)) {
        type_name = "мережевий сокет";
    } else if (S_ISFIFO(st.st_mode)) {
        type_name = "канал (pipe/FIFO)";
    } else if (S_ISCHR(st.st_mode)) {
        type_name = "символьний пристрій (char device)";
    } else if (S_ISBLK(st.st_mode)) {
        type_name = "блоковий пристрій (block device)";
        is_seekable = true;
    }

    std::cout << "Дескриптор " << fd << ": тип = " << type_name 
              << ", inode = " << st.st_ino << '\n';

    if (is_seekable) {
        off_t current_pos = ::lseek(fd, 0, SEEK_CUR);
        if (current_pos != static_cast<off_t>(-1)) {
            std::cout << "  Поточна позиція у файлі: " << current_pos << " байтів\n";
        }
    } else {
        std::cout << "  Позиціювання не підтримується (потоковий ресурс)\n";
    }

    std::array<char, 256> buffer{};
    ssize_t bytes_read = ::read(fd, buffer.data(), buffer.size() - 1);

    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        std::string_view received(buffer.data(), static_cast<size_t>(bytes_read));
        std::cout << "  Прочитано " << bytes_read << " байтів: \"" << received << "\"\n";
    } else if (bytes_read == 0) {
        std::cout << "  Отримано кінець потоку (EOF або закриття з'єднання)\n";
    } else {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            std::cout << "  Дані ще не готові (режим O_NONBLOCK)\n";
        } else {
            auto ec = std::error_code(errno, std::generic_category());
            std::cerr << "  Помилка read(): " << ec.message() << '\n';
        }
    }
}
