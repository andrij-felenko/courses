#include <sys/ioctl.h>
#include <linux/blkzoned.h>

// 1. Запит звіту про стан зон пристрою
// int ret = ioctl(fd, BLKREPORTZONE, struct blk_zone_report *rep);

// 2. Скидання покажчика запису для діапазону секторів (BLKRESETZONE)
// int ret = ioctl(fd, BLKRESETZONE, struct blk_zone_range *range);

// 3. Явне відкриття зон (BLKOPENZONE)
// int ret = ioctl(fd, BLKOPENZONE, struct blk_zone_range *range);

// 4. Явне закриття зон (BLKCLOSEZONE)
// int ret = ioctl(fd, BLKCLOSEZONE, struct blk_zone_range *range);

// 5. Завершення заповнення зон (BLKFINISHZONE)
// int ret = ioctl(fd, BLKFINISHZONE, struct blk_zone_range *range);
