// Ідіоматичні C++20 обгортки над ядровими структурами <linux/f2fs_fs.h>
#include <cstdint>
#include <linux/f2fs_fs.h>

namespace f2fs {

struct DefragRange {
    std::uint64_t start{0}; // початковий зсув у байтах
    std::uint64_t len{0};   // довжина ділянки
    
    [[nodiscard]] ::f2fs_defragment to_native() const noexcept {
        return ::f2fs_defragment{.start = start, .len = len};
    }
};

struct MoveRange {
    int target_fd{-1};
    std::uint64_t src_offset{0};
    std::uint64_t dst_offset{0};
    std::uint64_t length{0};

    [[nodiscard]] ::f2fs_move_range to_native() const noexcept {
        return ::f2fs_move_range{
            .dst_fd = static_cast<std::uint32_t>(target_fd),
            .pos_in = src_offset,
            .pos_out = dst_offset,
            .len = length
        };
    }
};

struct SecureTrimRange {
    std::uint64_t start{0};
    std::uint64_t len{0};
    std::uint64_t flags{0};

    [[nodiscard]] ::f2fs_sectrim_range to_native() const noexcept {
        return ::f2fs_sectrim_range{.start = start, .len = len, .flags = flags};
    }
};

struct FlushDeviceConfig {
    std::uint32_t device_index{0};
    std::uint32_t segments_count{0};

    [[nodiscard]] ::f2fs_flush_device to_native() const noexcept {
        return ::f2fs_flush_device{.dev_num = device_index, .segments = segments_count};
    }
};

} // namespace f2fs
