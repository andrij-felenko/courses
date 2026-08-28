#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <charconv>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>

namespace sysinfo {

// Автоматичне керування дескриптором через RAII
class FileDescriptor {
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

// Читання конкретного поля з /proc/self/status
std::string readStatusField(std::string_view key) {
    std::ifstream file("/proc/self/status");
    if (!file.is_open()) {
        return "N/A";
    }

    std::string line;
    while (std::getline(file, line)) {
        if (line.rfind(key, 0) == 0 && line.size() > key.size() && line[key.size()] == ':') {
            auto val_start = line.find_first_not_of(" \t", key.size() + 1);
            if (val_start != std::string::npos) {
                return line.substr(val_start);
            }
        }
    }
    return "N/A";
}

// Розбір аргументів командного рядка з нуль-розділеного /proc/self/cmdline
std::vector<std::string> readCmdline() {
    std::vector<std::string> args;
    FileDescriptor fd(::open("/proc/self/cmdline", O_RDONLY));
    if (!fd.isValid()) {
        return args;
    }

    std::array<char, 1024> buffer{};
    ssize_t bytes_read = ::read(fd.get(), buffer.data(), buffer.size() - 1);
    if (bytes_read <= 0) {
        return args;
    }

    ssize_t start = 0;
    for (ssize_t i = 0; i < bytes_read; ++i) {
        if (buffer[i] == '\0') {
            if (i > start) {
                args.emplace_back(&buffer[start]);
            }
            start = i + 1;
        }
    }
    return args;
}

// Читання однорядкового атрибута sysfs
std::string readSysfsAttribute(std::string_view path) {
    std::ifstream file(std::string(path));
    if (!file.is_open()) {
        return "N/A";
    }

    std::string value;
    if (std::getline(file, value)) {
        return value;
    }
    return "N/A";
}

// Читання структурованого запису з /dev/kmsg
void inspectKernelLog() {
    FileDescriptor fd(::open("/dev/kmsg", O_RDONLY | O_NONBLOCK));
    if (!fd.isValid()) {
        if (errno == EACCES) {
            std::cout << "  [/dev/kmsg]: Потрібні права CAP_SYSLOG або root для читання\n";
        } else {
            std::cout << "  [/dev/kmsg]: Неможливо відкрити пристрій (" << std::strerror(errno) << ")\n";
        }
        return;
    }

    std::array<char, 2048> buffer{};
    ssize_t n = ::read(fd.get(), buffer.data(), buffer.size() - 1);
    if (n > 0) {
        buffer[n] = '\0';
        std::string_view raw(buffer.data(), n);
        auto sep = raw.find(';');
        if (sep != std::string_view::npos) {
            auto meta = raw.substr(0, sep);
            auto text = raw.substr(sep + 1);
            if (!text.empty() && text.back() == '\n') {
                text.remove_suffix(1);
            }
            std::cout << "  [/dev/kmsg]: метадані=[" << meta << "] -> \"" << text << "\"\n";
        }
    } else if (errno == EAGAIN) {
        std::cout << "  [/dev/kmsg]: Буфер повідомлень порожній\n";
    }
}

} // namespace sysinfo

int main() {
    std::cout << "=== Інспекція багатошарового системного стану (C++) ===\n\n";

    // 1. Процесний стан
    std::cout << "1. Процесний шар (/proc/self/):\n";
    std::cout << "  [status] Резидентна пам'ять (VmRSS): " << sysinfo::readStatusField("VmRSS") << "\n";
    std::cout << "  [status] Кількість потоків:           " << sysinfo::readStatusField("Threads") << "\n";

    auto args = sysinfo::readCmdline();
    std::cout << "  [cmdline]: ";
    for (const auto& arg : args) {
        std::cout << "[" << arg << "] ";
    }
    std::cout << "\n";

    // 2. Апаратний шар
    std::cout << "\n2. Апаратний / пристроєвий шар (/sys/class/net/lo/):\n";
    std::cout << "  [interface] Стан lo (operstate): "
              << sysinfo::readSysfsAttribute("/sys/class/net/lo/operstate") << "\n";
    std::cout << "  [interface] MTU lo:              "
              << sysinfo::readSysfsAttribute("/sys/class/net/lo/mtu") << " байтів\n";

    // 3. Рантайм-шар
    std::cout << "\n3. Летючий рантайм-стан (/run/):\n";
    if (::access("/run/systemd/system", F_OK) == 0) {
        std::cout << "  [runtime] Виявлено активний екземпляр systemd у /run/systemd/system\n";
    } else {
        std::cout << "  [runtime] systemd не виявлено або /run недоступний\n";
    }

    // 4. Телеметрія ядра
    std::cout << "\n4. Телеметрія кільцевого буфера ядра (/dev/kmsg):\n";
    sysinfo::inspectKernelLog();

    return 0;
}
