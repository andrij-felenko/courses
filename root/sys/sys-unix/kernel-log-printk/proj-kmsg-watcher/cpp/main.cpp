#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <charconv>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <cerrno>
#include <cstring>

namespace kmsg {

// RAII обгортка для файлового дескриптора POSIX
class FileDescriptor {
    int fd_{-1};
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
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct KernelRecord {
    int level{6};
    uint64_t sequence{0};
    uint64_t timestamp_nsec{0};
    char flags{'-'};
    std::string message;
    std::string subsystem{"kernel"};
};

constexpr std::string_view loglevel_to_string(int level) noexcept {
    switch (level & 0x07) {
        case 0: return "EMERG";
        case 1: return "ALERT";
        case 2: return "CRIT";
        case 3: return "ERR";
        case 4: return "WARN";
        case 5: return "NOTICE";
        case 6: return "INFO";
        case 7: return "DEBUG";
        default: return "UNK";
    }
}

class MessageParser {
public:
    static bool parse(std::string_view raw, KernelRecord& rec) {
        auto semicolon_pos = raw.find(';');
        if (semicolon_pos == std::string_view::npos) {
            return false;
        }

        std::string_view header = raw.substr(0, semicolon_pos);
        std::string_view payload = raw.substr(semicolon_pos + 1);

        // Парсимо розширене поле заголовка (level,seq,nsec,flags)
        auto comma1 = header.find(',');
        auto comma2 = header.find(',', comma1 + 1);
        auto comma3 = header.find(',', comma2 + 1);

        if (comma1 == std::string_view::npos || comma2 == std::string_view::npos) {
            return false;
        }

        std::from_chars(header.data(), header.data() + comma1, rec.level);
        std::from_chars(header.data() + comma1 + 1, header.data() + comma2, rec.sequence);

        if (comma3 != std::string_view::npos) {
            std::from_chars(header.data() + comma2 + 1, header.data() + comma3, rec.timestamp_nsec);
            if (comma3 + 1 < header.size()) {
                rec.flags = header[comma3 + 1];
            }
        } else {
            std::from_chars(header.data() + comma2 + 1, header.data() + header.size(), rec.timestamp_nsec);
        }

        // Текст повідомлення — перший рядок корисної ноші
        auto newline_pos = payload.find('\n');
        if (newline_pos != std::string_view::npos) {
            rec.message = payload.substr(0, newline_pos);

            // Шукаємо метадані SUBSYSTEM= у наступних рядках
            std::string_view metadata = payload.substr(newline_pos + 1);
            constexpr std::string_view subsys_prefix = " SUBSYSTEM=";
            auto subsys_pos = metadata.find(subsys_prefix);
            if (subsys_pos != std::string_view::npos) {
                auto subsys_start = subsys_pos + subsys_prefix.size();
                auto subsys_end = metadata.find('\n', subsys_start);
                if (subsys_end != std::string_view::npos) {
                    rec.subsystem = metadata.substr(subsys_start, subsys_end - subsys_start);
                } else {
                    rec.subsystem = metadata.substr(subsys_start);
                }
            } else {
                rec.subsystem = "kernel";
            }
        } else {
            rec.message = payload;
            rec.subsystem = "kernel";
        }

        return true;
    }
};

} // namespace kmsg

int main() {
    using namespace kmsg;

    int raw_fd = ::open("/dev/kmsg", O_RDWR | O_NONBLOCK);
    if (raw_fd < 0) {
        std::cerr << "Failed to open /dev/kmsg: " << std::strerror(errno) << '\n';
        return EXIT_FAILURE;
    }

    FileDescriptor kmsg_fd(raw_fd);

    if (::lseek(kmsg_fd.get(), 0, SEEK_END) < 0) {
        std::cerr << "Failed to lseek SEEK_END: " << std::strerror(errno) << '\n';
        return EXIT_FAILURE;
    }

    std::string_view init_msg = "<6>kmsg_watcher_cpp: C++ daemon initialized\n";
    if (::write(kmsg_fd.get(), init_msg.data(), init_msg.size()) < 0) {
        std::cerr << "Failed to write init message: " << std::strerror(errno) << '\n';
    }

    std::cout << "C++ watcher daemon listening on /dev/kmsg...\n";

    pollfd pfd{.fd = kmsg_fd.get(), .events = POLLIN, .revents = 0};
    std::vector<char> buffer(8192);

    while (true) {
        int poll_ret = ::poll(&pfd, 1, -1);
        if (poll_ret < 0) {
            if (errno == EINTR) continue;
            std::cerr << "Poll error: " << std::strerror(errno) << '\n';
            break;
        }

        if (pfd.revents & POLLIN) {
            while (true) {
                ssize_t bytes = ::read(kmsg_fd.get(), buffer.data(), buffer.size() - 1);
                if (bytes < 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK) {
                        break; // Буфер спорожнів
                    }
                    if (errno == EPIPE) {
                        std::cerr << "WARN: Kernel log buffer overrun, messages skipped\n";
                        continue;
                    }
                    std::cerr << "Read error: " << std::strerror(errno) << '\n';
                    return EXIT_FAILURE;
                }

                buffer[bytes] = '\0';
                std::string_view raw_record(buffer.data(), static_cast<size_t>(bytes));

                KernelRecord rec;
                if (MessageParser::parse(raw_record, rec)) {
                    double sec = static_cast<double>(rec.timestamp_nsec) / 1e9;
                    std::cout << '[' << sec << "] ["
                              << loglevel_to_string(rec.level) << "] ["
                              << rec.subsystem << "] (seq=" << rec.sequence << "): "
                              << rec.message << '\n';
                }
            }
        }
    }

    return EXIT_SUCCESS;
}
