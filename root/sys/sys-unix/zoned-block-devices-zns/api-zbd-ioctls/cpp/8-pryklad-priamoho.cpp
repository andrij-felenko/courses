#include <iostream>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

void reset_single_zone_cpp(int dev_fd, std::uint64_t zone_start_sector, std::uint64_t zone_size_sectors) {
    struct blk_zone_range range{};
    range.sector = zone_start_sector;
    range.nr_sectors = zone_size_sectors;

    if (::ioctl(dev_fd, BLKRESETZONE, &range) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка виконання ioctl BLKRESETZONE");
    }

    std::cout << "Зону за сектором " << zone_start_sector << " успішно скинуто у C++\n";
}
