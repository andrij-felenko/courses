#include <string>
#include <string_view>
#include <expected>
#include <format>
#include <memory>
#include <vector>
#include <span>
#include <iostream>

extern "C" {
#include "lfs.h"
}

enum class FsError {
    OpenFailed,
    WriteFailed,
    ReadFailed,
    CloseFailed
};

class LittleFsFile {
public:
    LittleFsFile(lfs_t *lfs, std::string_view path, int flags) : lfs_(lfs) {
        int err = lfs_file_open(lfs_, &file_, std::string(path).c_str(), flags);
        if (err == LFS_ERR_OK) {
            is_open_ = true;
        }
    }

    ~LittleFsFile() {
        close();
    }

    LittleFsFile(const LittleFsFile &) = delete;
    LittleFsFile &operator=(const LittleFsFile &) = delete;

    LittleFsFile(LittleFsFile &&other) noexcept 
        : lfs_(other.lfs_), file_(other.file_), is_open_(other.is_open_) {
        other.is_open_ = false;
    }

    [[nodiscard]] bool isOpen() const noexcept { return is_open_; }

    [[nodiscard]] std::expected<size_t, FsError> write(std::span<const char> data) noexcept {
        if (!is_open_) return std::unexpected(FsError::WriteFailed);

        auto written = lfs_file_write(lfs_, &file_, data.data(), static_cast<lfs_size_t>(data.size()));
        if (written < 0 || static_cast<size_t>(written) != data.size()) {
            return std::unexpected(FsError::WriteFailed);
        }
        return static_cast<size_t>(written);
    }

    [[nodiscard]] std::expected<size_t, FsError> read(std::span<char> buffer) noexcept {
        if (!is_open_) return std::unexpected(FsError::ReadFailed);

        auto bytes = lfs_file_read(lfs_, &file_, buffer.data(), static_cast<lfs_size_t>(buffer.size()));
        if (bytes < 0) {
            return std::unexpected(FsError::ReadFailed);
        }
        return static_cast<size_t>(bytes);
    }

    bool close() noexcept {
        if (is_open_) {
            is_open_ = false;
            return lfs_file_close(lfs_, &file_) == LFS_ERR_OK;
        }
        return true;
    }

private:
    lfs_t *lfs_{nullptr};
    lfs_file_t file_{};
    bool is_open_{false};
};

class TelemetryLogger {
public:
    explicit TelemetryLogger(lfs_t *lfs) : lfs_(lfs) {}

    [[nodiscard]] bool logEvent(uint32_t timestamp, float voltage, float temperature) {
        LittleFsFile file(lfs_, "/telemetry.log", LFS_O_WRONLY | LFS_O_CREAT | LFS_O_APPEND);
        if (!file.isOpen()) return false;

        std::string record = std::format("TS:{};V:{:.2f};T:{:.2f}\n", timestamp, voltage, temperature);
        auto result = file.write(std::span<const char>(record.data(), record.size()));
        return result.has_value();
    }

    void printLogs() {
        LittleFsFile file(lfs_, "/telemetry.log", LFS_O_RDONLY);
        if (!file.isOpen()) return;

        std::vector<char> buffer(128);
        while (true) {
            auto res = file.read(std::span<char>(buffer.data(), buffer.size() - 1));
            if (!res.has_value() || *res == 0) break;
            buffer[*res] = '\0';
            std::cout << buffer.data();
        }
    }

private:
    lfs_t *lfs_;
};
