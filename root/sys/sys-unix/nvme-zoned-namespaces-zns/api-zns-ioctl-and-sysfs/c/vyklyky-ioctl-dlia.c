#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

int reset_single_zone(int fd, uint64_t zone_start_sector, uint64_t zone_size_sectors) {
    struct blk_zone_range range;
    range.sector = zone_start_sector;
    range.nr_sectors = zone_size_sectors;

    if (ioctl(fd, BLKRESETZONE, &range) < 0) {
        perror("BLKRESETZONE failed");
        return -1;
    }
    return 0;
}
