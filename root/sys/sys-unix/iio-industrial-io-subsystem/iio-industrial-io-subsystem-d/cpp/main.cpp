#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <chrono>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/poll.h>

namespace fs = std::filesystem;

class IIOBufferReader {
private:
    int dev_fd_ = -1;
    fs::path sysfs_dev_;
    fs::path dev_node_;

    std::expected<void, std::error_code> sysfs_write(const std::string& subpath, const std::string& value) {
        std::ofstream ofs(sysfs_dev_ / subpath);
        if (!ofs.is_open()) {
            return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
        }
        ofs << value << std::endl;
        return ofs.good() ? std::expected<void, std::error_code>{} 
                          : std::unexpected(std::make_error_code(std::errc::io_error));
    }

public:
    struct alignas(8) Frame {
        uint16_t raw_value;
        uint16_t padding[3];
        int64_t timestamp_ns;
    };

    explicit IIOBufferReader(std::string_view dev_name = "iio:device0")
        : sysfs_dev_("/sys/bus/iio/devices" / fs::path(dev_name)),
          dev_node_("/dev" / fs::path(dev_name)) {}

    ~IIOBufferReader() {
        stop();
        if (dev_fd_ >= 0) ::close(dev_fd_);
    }

    std::expected<void, std::error_code> start(std::size_t buffer_depth = 128) {
        (void)sysfs_write("buffer/enable", "0");
        if (auto r = sysfs_write("scan_elements/in_voltage0_en", "1"); !r) return r;
        if (auto r = sysfs_write("scan_elements/in_timestamp_en", "1"); !r) return r;
        if (auto r = sysfs_write("buffer/length", std::to_string(buffer_depth)); !r) return r;
        if (auto r = sysfs_write("buffer/enable", "1"); !r) return r;

        dev_fd_ = ::open(dev_node_.c_str(), O_RDONLY);
        if (dev_fd_ < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }
        return {};
    }

    void stop() noexcept {
        (void)sysfs_write("buffer/enable", "0");
    }

    std::expected<Frame, std::error_code> read_frame(int timeout_ms = 2000) {
        if (dev_fd_ < 0) return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));

        ::pollfd pfd{ .fd = dev_fd_, .events = POLLIN, .revents = 0 };
        int ret = ::poll(&pfd, 1, timeout_ms);
        if (ret == 0) return std::unexpected(std::make_error_code(std::errc::timed_out));
        if (ret < 0)  return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));

        Frame frame{};
        ssize_t bytes = ::read(dev_fd_, &frame, sizeof(frame));
        if (bytes != sizeof(frame)) {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }
        return frame;
    }
};

int main() {
    IIOBufferReader reader("iio:device0");

    if (auto res = reader.start(128); !res) {
        std::cerr << "Не вдалося ініціалізувати буфер IIO\n";
        return 1;
    }

    std::cout << "Читання 5 семплів у С++23...\n";
    for (int i = 0; i < 5; ++i) {
        auto frame_res = reader.read_frame();
        if (frame_res) {
            const auto& f = frame_res.value();
            std::cout << "Семпл [" << i << "]: RAW = " << f.raw_value 
                      << " | Time = " << f.timestamp_ns << " ns\n";
        }
    }
    return 0;
}
