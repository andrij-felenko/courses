// timestamp_api_demo.cpp — Ідіоматична реалізація на C++20
#include <iostream>
#include <string_view>
#include <system_error>
#include <chrono>
#include <optional>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

class TimestampManager {
public:
    struct FileTimes {
        std::chrono::system_clock::time_point access;
        std::chrono::system_clock::time_point modification;
        std::chrono::system_clock::time_point status_change;
        std::optional<std::chrono::system_clock::time_point> creation;
    };

    [[nodiscard]] static std::error_code get_timestamps(std::string_view path,
                                                        FileTimes& out_times) noexcept {
        struct statx stx{};
        const int res = statx(AT_FDCWD, path.data(),
                              AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT,
                              STATX_BASIC_STATS | STATX_BTIME, &stx);
        if (res != 0) {
            return std::error_code(errno, std::generic_category());
        }

        out_times.access = convert_statx_ts(stx.stx_atime);
        out_times.modification = convert_statx_ts(stx.stx_mtime);
        out_times.status_change = convert_statx_ts(stx.stx_ctime);

        if (stx.stx_mask & STATX_BTIME) {
            out_times.creation = convert_statx_ts(stx.stx_btime);
        } else {
            out_times.creation = std::nullopt;
        }

        return {};
    }

    [[nodiscard]] static std::error_code update_mtime_now(std::string_view path) noexcept {
        struct timespec ts[2];
        ts[0].tv_sec = 0;
        ts[0].tv_nsec = UTIME_OMIT; // atime без змін
        ts[1].tv_sec = 0;
        ts[1].tv_nsec = UTIME_NOW;  // mtime оновлюється ядром

        if (utimensat(AT_FDCWD, path.data(), ts, 0) != 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }

private:
    [[nodiscard]] static std::chrono::system_clock::time_point
    convert_statx_ts(const struct statx_timestamp& ts) noexcept {
        using namespace std::chrono;
        const auto total_ns = seconds(ts.tv_sec) + nanoseconds(ts.tv_nsec);
        return system_clock::time_point(duration_cast<system_clock::duration>(total_ns));
    }
};
