#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

/* Форматування часової позначки struct statx_timestamp */
static void print_time(const char *label, const struct statx_timestamp *ts) {
    time_t sec = (time_t)ts->tv_sec;
    struct tm tm_buf;
    char time_str[64];
    
    if (localtime_r(&sec, &tm_buf) != NULL) {
        strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", &tm_buf);
        printf("  %-16s: %s.%09u нс\n", label, time_str, ts->tv_nsec);
    } else {
        printf("  %-16s: %lld с, %u нс\n", label, (long long)ts->tv_sec, ts->tv_nsec);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *path = argv[1];
    struct statx stx;
    memset(&stx, 0, sizeof(stx));

    /* Сформувати маску запиту розширених полів */
    unsigned int request_mask = STATX_BASIC_STATS | STATX_BTIME;
#ifdef STATX_DIOALIGN
    request_mask |= STATX_DIOALIGN;
#endif

    /* Викликати statx з прапорцем невимогливої синхронізації кешу */
    int res = statx(AT_FDCWD, path, AT_SYMLINK_NOFOLLOW | AT_STATX_SYNC_AS_STAT,
                    request_mask, &stx);

    if (res != 0) {
        if (errno == ENOSYS || errno == EOPNOTSUPP) {
            fprintf(stderr, "Помилка: системний виклик statx не підтримується ядром.\n");
        } else {
            perror("Помилка виконання statx");
        }
        return EXIT_FAILURE;
    }

    printf("=== Інспектування файлу: %s ===\n", path);
    printf("Розмір файлу        : %llu байтів\n", (unsigned long long)stx.stx_size);
    printf("Номер Inode         : %llu\n", (unsigned long long)stx.stx_ino);
    printf("Кількість посилань  : %u\n", stx.stx_nlink);
    printf("Права (stx_mode)    : 0%o\n", stx.stx_mode & 07777);

    /* Перевірка наявності часу створення (btime) у повернутій масці */
    printf("\n--- Часові позначки ---\n");
    if (stx.stx_mask & STATX_ATIME) print_time("Доступ (atime)", &stx.stx_atime);
    if (stx.stx_mask & STATX_MTIME) print_time("Модифікація (mtime)", &stx.stx_mtime);
    if (stx.stx_mask & STATX_CTIME) print_time("Зміна inode (ctime)", &stx.stx_ctime);

    if (stx.stx_mask & STATX_BTIME) {
        print_time("Створення (btime)", &stx.stx_btime);
    } else {
        printf("  Створення (btime): [НЕ ПІДТРИМУЄТЬСЯ ФАЙЛОВОЮ СИСТЕМОЮ]\n");
    }

    /* Перевірка прапорців атрибутів файлу */
    printf("\n--- Розширені атрибути (stx_attributes) ---\n");
    uint64_t mask_attr = stx.stx_attributes_mask;
    uint64_t val_attr = stx.stx_attributes;

    if (mask_attr & STATX_ATTR_IMMUTABLE) {
        printf("  Immutable (+i)   : %s\n", (val_attr & STATX_ATTR_IMMUTABLE) ? "ТАК" : "НІ");
    }
    if (mask_attr & STATX_ATTR_APPEND) {
        printf("  Append-only (+a) : %s\n", (val_attr & STATX_ATTR_APPEND) ? "ТАК" : "НІ");
    }
    if (mask_attr & STATX_ATTR_COMPRESSED) {
        printf("  Compressed       : %s\n", (val_attr & STATX_ATTR_COMPRESSED) ? "ТАК" : "НІ");
    }
    if (mask_attr & STATX_ATTR_ENCRYPTED) {
        printf("  Encrypted        : %s\n", (val_attr & STATX_ATTR_ENCRYPTED) ? "ТАК" : "НІ");
    }
#ifdef STATX_ATTR_VERITY
    if (mask_attr & STATX_ATTR_VERITY) {
        printf("  fs-verity        : %s\n", (val_attr & STATX_ATTR_VERITY) ? "ТАК" : "НІ");
    }
#endif
#ifdef STATX_ATTR_DAX
    if (mask_attr & STATX_ATTR_DAX) {
        printf("  DAX (Direct Acc) : %s\n", (val_attr & STATX_ATTR_DAX) ? "ТАК" : "НІ");
    }
#endif

    /* Перевірка параметрів вирівнювання O_DIRECT */
#ifdef STATX_DIOALIGN
    printf("\n--- Параметри вирівнювання O_DIRECT (STATX_DIOALIGN) ---\n");
    if (stx.stx_mask & STATX_DIOALIGN) {
        printf("  Вирівнювання буфера пам'яті : %u байтів\n", stx.stx_dio_mem_align);
        printf("  Вирівнювання зсуву у файлі  : %u байтів\n", stx.stx_dio_offset_align);
    } else {
        printf("  Вирівнювання O_DIRECT       : [НЕ ПІДТРИМУЄТЬСЯ ЯДРОМ ТА ФС]\n");
    }
#endif

    return EXIT_SUCCESS;
}
