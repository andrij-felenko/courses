#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

int reset_single_zone(int dev_fd, uint64_t zone_start_sector, uint64_t zone_size_sectors) {
    struct blk_zone_range range;
    range.sector = zone_start_sector;
    range.nr_sectors = zone_size_sectors;

    if (ioctl(dev_fd, BLKRESETZONE, &range) < 0) {
        perror("Помилка виконання ioctl(BLKRESETZONE)");
        return -1;
    }

    printf("Зону за сектором %" PRIu64 " успішно скинуто в Empty\n", zone_start_sector);
    return 0;
}
