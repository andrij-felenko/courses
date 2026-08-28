#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>

// Функція запиту стану зони ZNS накопичувача через ioctl(BLKREPORTZONE)
static int print_zone_report(int fd, unsigned long long start_sector) {
    // Обчислюємо розмір буфера з урахуванням одного елемента гнучкого масиву
    size_t rep_size = sizeof(struct blk_zone_report) + sizeof(struct blk_zone);
    struct blk_zone_report *rep = (struct blk_zone_report *)malloc(rep_size);
    if (!rep) {
        perror("Помилка виділення пам'яті під звіт зон");
        return -1;
    }

    memset(rep, 0, rep_size);
    rep->sector = start_sector;
    rep->nr_zones = 1;

    // Виконуємо системний виклик ioctl до ядра Linux
    if (ioctl(fd, BLKREPORTZONE, rep) < 0) {
        perror("Помилка виконання виклику BLKREPORTZONE");
        free(rep);
        return -1;
    }

    if (rep->nr_zones > 0) {
        struct blk_zone *z = &rep->zones[0];
        printf("Зона від сектора %llu: довжина=%llu, WP=%llu, стан=0x%x\n",
               (unsigned long long)z->start,
               (unsigned long long)z->len,
               (unsigned long long)z->wp,
               (unsigned int)z->cond);
    } else {
        printf("Зону за сектором %llu не знайдено на пристрої\n", start_sector);
    }

    free(rep);
    return 0;
}

// Функція скидання покажчика запису зони через ioctl(BLKRESETZONE)
static int reset_zone(int fd, unsigned long long start_sector, unsigned long long sector_count) {
    struct blk_zone_range range;
    range.sector = start_sector;
    range.nr_sectors = sector_count;

    if (ioctl(fd, BLKRESETZONE, &range) < 0) {
        perror("Помилка виконання виклику BLKRESETZONE");
        return -1;
    }

    printf("Успішно скинуто покажчик запису зони від сектора %llu (%llu секторів)\n",
           start_sector, sector_count);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/nvmeXnY\n", argv[0]);
        return 1;
    }

    // Відкриваємо блочний пристрій у режимі читання та запису (O_RDWR)
    int fd = open(argv[1], O_RDWR);
    if (fd < 0) {
        perror("Не вдалося відкрити зонований пристрій");
        return 1;
    }

    printf("=== Стан зони ДО скидання ===\n");
    if (print_zone_report(fd, 0) < 0) {
        close(fd);
        return 1;
    }

    printf("\nНадсилання команди BLKRESETZONE...\n");
    if (reset_zone(fd, 0, 524288) == 0) {
        printf("\n=== Стан зони ПІСЛЯ скидання ===\n");
        print_zone_report(fd, 0);
    }

    close(fd);
    return 0;
}
