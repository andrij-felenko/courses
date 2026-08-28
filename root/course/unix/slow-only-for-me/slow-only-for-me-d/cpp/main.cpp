#include <iostream>
#include <vector>
#include <string_view>
#include <chrono>
#include <span>
#include <memory>
#include <fcntl.h>
#include <unistd.h>
#include <system_error>

namespace {

constexpr size_t TOTAL_RECORDS = 500'000;
constexpr std::string_view RECORD_TEXT = "METRIC:id=42,sensor=temp,val=23.75,status=OK\n";

// RAII обгортка для володіння дескриптором POSIX
class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(const char* path, int flags, mode_t mode = 0644) {
        fd_ = ::open(path, flags, mode);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити файл");
        }
    }

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

    void write_all(std::span<const char> data) const {
        size_t written_total = 0;
        while (written_total < data.size()) {
            ssize_t res = ::write(fd_, data.data() + written_total, data.size() - written_total);
            if (res < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "Помилка write");
            }
            written_total += static_cast<size_t>(res);
        }
    }
};

void write_unbuffered(const char* path) {
    FileDescriptor file(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    for (size_t i = 0; i < TOTAL_RECORDS; ++i) {
        file.write_all(std::span<const char>(RECORD_TEXT.data(), RECORD_TEXT.size()));
    }
}

void write_buffered(const char* path) {
    FileDescriptor file(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    constexpr size_t BUFFER_CAPACITY = 64 * 1024;
    std::vector<char> buffer;
    buffer.reserve(BUFFER_CAPACITY);

    for (size_t i = 0; i < TOTAL_RECORDS; ++i) {
        if (buffer.size() + RECORD_TEXT.size() > BUFFER_CAPACITY) {
            file.write_all(buffer);
            buffer.clear();
        }
        buffer.insert(buffer.end(), RECORD_TEXT.begin(), RECORD_TEXT.end());
    }

    if (!buffer.empty()) {
        file.write_all(buffer);
    }
}

} // namespace

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " [unbuffered|buffered]\n";
        return 1;
    }

    try {
        const std::string_view mode = argv[1];
        const auto start = std::chrono::steady_clock::now();

        if (mode == "unbuffered") {
            write_unbuffered("/tmp/bench_unbuffered_cpp.log");
        } else {
            write_buffered("/tmp/bench_buffered_cpp.log");
        }

        const auto end = std::chrono::steady_clock::now();
        const std::chrono::duration<double> elapsed = end - start;
        std::cout << "Режим " << mode << " виконано за " << elapsed.count() << " секунд\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
