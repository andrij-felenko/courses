// timestamp_demo.cpp — Безпечна обгортка з RAII на C++20
#include <iostream>
#include <string_view>
#include <chrono>
#include <optional>
#include <system_error>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

class FileTimeHelper {
public:
    struct TimestampSnapshot {
        std::chrono::system_clock::time_point access_time;
        std::chrono::system_clock::time_point modify_time;
        std::chrono::system_clock::time_point change_time;
        std::optional<std::chrono::system_clock::time_point> birth_time;
    };

    [[nodiscard]] static std::error_code read_timestamps(std::string_view path,
                                                         TimestampSnapshot& snapshot) noexcept {
        struct statx stx{};
        if (statx(AT_FDCWD, path.data(), AT_SYMLINK_NOFOLLOW,
                  STATX_BASIC_STATS | STATX_BTIME, &stx) != 0) {
            return std::error_code(errno, std::generic_category());
        }

        snapshot.access_time = to_time_point(stx.stx_atime);
        snapshot.modify_time = to_time_point(stx.stx_mtime);
        snapshot.change_time = to_time_point(stx.stx_ctime);

        if (stx.stx_mask & STATX_BTIME) {
            snapshot.birth_time = to_time_point(stx.stx_btime);
        } else {
            snapshot.birth_time = std::nullopt;
        }

        return {};
    }

    [[nodiscard]] static std::error_code touch_mtime_only(std::string_view path) noexcept {
        struct timespec ts[2];
        ts[0].tv_sec = 0;
        ts[0].tv_nsec = UTIME_OMIT; // Залишити atime без змін
        ts[1].tv_sec = 0;
        ts[1].tv_nsec = UTIME_NOW;  // Встановити поточний час

        if (utimensat(AT_FDCWD, path.data(), ts, 0) != 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }

private:
    [[nodiscard]] static std::chrono::system_clock::time_point
    to_time_point(const struct statx_timestamp& ts) noexcept {
        using namespace std::chrono;
        const auto dur = seconds(ts.tv_sec) + nanoseconds(ts.tv_nsec);
        return system_clock::time_point(duration_cast<system_clock::duration>(dur));
    }
};
