#include <iostream>
#include <system_error>
#include <expected>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

std::expected<void, std::error_code> reset_single_zone(int fd, std::uint64_t zone_start_sector, std::uint64_t zone_size_sectors) noexcept {
    struct blk_zone_range range{
        .sector = zone_start_sector,
        .nr_sectors = zone_size_sectors
    };

    if (::ioctl(fd, BLKRESETZONE, &range) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
