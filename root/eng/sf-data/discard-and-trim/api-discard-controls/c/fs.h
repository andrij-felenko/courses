#include <linux/fs.h>     /* FITRIM; struct fstrim_range оголошено тут:
                             __u64 start   — звідки шукати вільні блоки, байти
                             __u64 len     — скільки байтів переглянути
                             __u64 minlen  — найкоротша суцільна смуга, варта запиту */

struct fstrim_range r = { .start = 0, .len = UINT64_MAX, .minlen = 0 };
int fd = open("/", O_RDONLY);

if (ioctl(fd, FITRIM, &r) == 0)
        printf("віддано вниз %llu байтів\n", (unsigned long long)r.len);
