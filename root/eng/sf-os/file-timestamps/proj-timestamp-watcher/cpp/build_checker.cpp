// build_checker.cpp — Об'єктно-орієнтований аналізатор на C++20
#include <iostream>
#include <string_view>
#include <chrono>
#include <optional>
#include <system_error>
#include <fstream>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

class TimestampEngine {
public:
    struct Timestamp {
        std::chrono::seconds sec{0};
        std::chrono::nanoseconds nsec{0};

        auto operator<=>(const Timestamp&) const = default;
    };

    struct FileInfo {
        Timestamp mtime;
        std::optional<Timestamp> btime;
    };

    [[nodiscard]] static std::error_code get_info(std::string_view path,
                                                  FileInfo& info) noexcept {
        struct statx stx{};
        if (statx(AT_FDCWD, path.data(), AT_SYMLINK_NOFOLLOW,
                  STATX_MTIME | STATX_BTIME, &stx) != 0) {
            return std::error_code(errno, std::generic_category());
        }

        info.mtime = {
            std::chrono::seconds(stx.stx_mtime.tv_sec),
            std::chrono::nanoseconds(stx.stx_mtime.tv_nsec)
        };

        if (stx.stx_mask & STATX_BTIME) {
            info.btime = Timestamp{
                std::chrono::seconds(stx.stx_btime.tv_sec),
                std::chrono::nanoseconds(stx.stx_btime.tv_nsec)
            };
        } else {
            info.btime = std::nullopt;
        }

        return {};
    }

    [[nodiscard]] static std::error_code touch_target_mtime(std::string_view path) noexcept {
        struct timespec ts[2];
        ts[0].tv_sec = 0;
        ts[0].tv_nsec = UTIME_OMIT;
        ts[1].tv_sec = 0;
        ts[1].tv_nsec = UTIME_NOW;

        if (utimensat(AT_FDCWD, path.data(), ts, 0) != 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <source_file> <target_file>\n";
        return 1;
    }

    const std::string_view src_path = argv[1];
    const std::string_view tgt_path = argv[2];

    TimestampEngine::FileInfo src_info{};
    if (auto ec = TimestampEngine::get_info(src_path, src_info); ec) {
        std::cerr << "Помилка читання джерела: " << ec.message() << "\n";
        return 1;
    }

    TimestampEngine::FileInfo tgt_info{};
    bool target_exists = !TimestampEngine::get_info(tgt_path, tgt_info);

    std::cout << "=== Аналіз часових позначок (C++20 Engine) ===\n";
    std::cout << "Джерело: " << src_path << " -> "
              << src_info.mtime.sec.count() << "."
              << src_info.mtime.nsec.count() << " s\n";

    if (!target_exists) {
        std::cout << "Ціль:    " << tgt_path << " [відсутня]\n";
    } else {
        std::cout << "Ціль:    " << tgt_path << " -> "
                  << tgt_info.mtime.sec.count() << "."
                  << tgt_info.mtime.nsec.count() << " s\n";
    }

    if (!target_exists || src_info.mtime > tgt_info.mtime) {
        std::cout << "Рішення: Потрібна перекомпіляція артефакту.\n";
        
        {
            std::ofstream out(tgt_path.data(), std::ios::trunc);
            out << "Compiled binary data\n";
        }

        if (auto ec = TimestampEngine::touch_target_mtime(tgt_path); ec) {
            std::cerr << "Помилка оновлення часу: " << ec.message() << "\n";
            return 1;
        }
        std::cout << "Артефакт успішно зібрано та оновлено.\n";
    } else {
        std::cout << "Рішення: Ціль актуальна, збірку пропущено.\n";
    }

    return 0;
}
