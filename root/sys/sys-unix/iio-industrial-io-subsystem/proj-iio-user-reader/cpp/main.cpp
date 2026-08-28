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

class IIODevice {
private:
    fs::path sysfs_base_;
    fs::path dev_path_;
    int dev_fd_ = -1;

    std::expected<void, std::error_code> write_sysfs(const std::string& relative_path, const std::string& val) {
        std::ofstream ofs(sysfs_base_ / relative_path);
        if (!ofs.is_open()) {
            return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
        }
        ofs << val << std::endl;
        return ofs.good() ? std::expected<void, std::error_code>{} 
                          : std::unexpected(std::make_error_code(std::errc::io_error));
    }

public:
    struct alignas(8) SampleFrame {
        uint16_t raw_value;
        uint16_t padding[3];
        int64_t timestamp_ns;
    };

    explicit IIODevice(std::string device_name = "iio:device0")
        : sysfs_base_("/sys/bus/iio/devices" / fs::path(device_name)),
          dev_path_("/dev" / fs::path(device_name)) {}

    ~IIODevice() {
        stop_buffer();
        if (dev_fd_ >= 0) {
            ::close(dev_fd_);
        }
    }

    std::expected<void, std::error_code> configure_buffer(std::size_t buffer_length = 128, std::size_t watermark = 16) {
        stop_buffer();
        if (auto res = write_sysfs("scan_elements/in_voltage0_en", "1"); !res) return res;
        if (auto res = write_sysfs("scan_elements/in_timestamp_en", "1"); !res) return res;
        if (auto res = write_sysfs("buffer/length", std::to_string(buffer_length)); !res) return res;
        if (auto res = write_sysfs("buffer/watermark", std::to_string(watermark)); !res) return res;
        return {};
    }

    std::expected<void, std::error_code> start_buffer() {
        if (auto res = write_sysfs("buffer/enable", "1"); !res) return res;
        dev_fd_ = ::open(dev_path_.c_str(), O_RDONLY);
        if (dev_fd_ < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }
        return {};
    }

    void stop_buffer() noexcept {
        (void)write_sysfs("buffer/enable", "0");
    }

    std::expected<SampleFrame, std::error_code> read_sample(int timeout_ms = 1000) {
        if (dev_fd_ < 0) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        ::pollfd pfd{ .fd = dev_fd_, .events = POLLIN, .revents = 0 };
        int ret = ::poll(&pfd, 1, timeout_ms);
        if (ret == 0) return std::unexpected(std::make_error_code(std::errc::timed_out));
        if (ret < 0)  return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));

        SampleFrame frame{};
        ssize_t n = ::read(dev_fd_, &frame, sizeof(frame));
        if (n != sizeof(frame)) {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }
        return frame;
    }
};

int main() {
    std::cout << "Ініціалізація IIODevice (C++23 RAII)..." << std::endl;
    IIODevice sensor("iio:device0");

    if (auto res = sensor.configure_buffer(128, 16); !res) {
        std::cerr << "Помилка конфігурації буфера IIO у sysfs" << std::endl;
        return 1;
    }

    if (auto res = sensor.start_buffer(); !res) {
        std::cerr << "Помилка запуску буфера IIO" << std::endl;
        return 1;
    }

    std::cout << "Успішно запущено. Зчитування семплів..." << std::endl;
    for (int i = 0; i < 10; ++i) {
        auto sample_res = sensor.read_sample(2000);
        if (sample_res) {
            const auto& sample = sample_res.value();
            auto time_pt = std::chrono::nanoseconds(sample.timestamp_ns);
            std::cout << "[" << i << "] RAW: " << sample.raw_value 
                      << " | Timestamp: " << time_pt.count() << " ns" << std::endl;
        } else {
            std::cerr << "Помилка зчитування семпла з буфера" << std::endl;
            break;
        }
    }

    return 0;
}
