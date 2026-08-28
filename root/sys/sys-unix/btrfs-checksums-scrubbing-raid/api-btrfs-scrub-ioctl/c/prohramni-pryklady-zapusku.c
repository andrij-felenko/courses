#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>
#include <inttypes.h>
#include <linux/btrfs.h>

int main(int argc, char *argv[])
{
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <точка_монтування> <devid>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *mount_point = argv[1];
    uint64_t devid = strtoull(argv[2], NULL, 10);

    int fd = open(mount_point, O_RDONLY | O_DIRECTORY);
    if (fd < 0) {
        perror("Не вдалося відкрити точку монтування Btrfs");
        return EXIT_FAILURE;
    }

    struct btrfs_ioctl_scrub_args args;
    memset(&args, 0, sizeof(args));
    args.devid = devid;
    args.start = 0;
    args.end = (uint64_t)-1; // Весь простір диска
    args.flags = 0;          // 0 - дозволити автоматичне самовідновлення (Self-Healing)

    printf("Запуск btrfs scrub для пристрою devid=%" PRIu64 " на %s...\n", devid, mount_point);

    if (ioctl(fd, BTRFS_IOC_SCRUB, &args) < 0) {
        fprintf(stderr, "Помилка ioctl BTRFS_IOC_SCRUB: %s\n", strerror(errno));
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Scrub успішно завершено!\n");
    printf("Проскановано даних: %llu МіБ\n", (unsigned long long)(args.progress.data_bytes_scrubbed / (1024 * 1024)));
    printf("Проскановано метаданих: %llu МіБ\n", (unsigned long long)(args.progress.tree_bytes_scrubbed / (1024 * 1024)));
    printf("Помилок контрольних сум (CSUM): %llu\n", (unsigned long long)args.progress.csum_errors);
    printf("Успішно відновлено з RAID: %llu\n", (unsigned long long)args.progress.corrected_errors);
    printf("НЕВІДНОВЛЮВАНИХ помилок: %llu\n", (unsigned long long)args.progress.uncorrectable_errors);

    close(fd);
    return EXIT_SUCCESS;
}
