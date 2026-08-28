#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/mount.h>

#define CONFIGFS_PATH "/sys/kernel/config"
#define OVERLAYS_PATH "/sys/kernel/config/device-tree/overlays"
#define FDT_MAGIC 0xd00dfeedU

/* Структура заголовка Flattened Device Tree (Big-Endian) */
struct fdt_header {
    uint32_t magic;
    uint32_t totalsize;
    uint32_t off_dt_struct;
    uint32_t off_dt_strings;
    uint32_t off_mem_rsvmap;
    uint32_t version;
    uint32_t last_comp_version;
    uint32_t boot_cpuid_phys;
    uint32_t size_dt_strings;
    uint32_t size_dt_struct;
};

static uint32_t fdt32_to_cpu(uint32_t val) {
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    return __builtin_bswap32(val);
#else
    return val;
#endif
}

/* Перевірка наявності та монтування ConfigFS */
static int ensure_configfs_mounted(void) {
    struct stat st;
    if (stat(OVERLAYS_PATH, &st) == 0 && S_ISDIR(st.st_mode)) {
        return 0;
    }

    if (stat(CONFIGFS_PATH, &st) != 0) {
        fprintf(stderr, "[ERR] Точка монтування %s відсутня\n", CONFIGFS_PATH);
        return -ENOENT;
    }

    if (mount("none", CONFIGFS_PATH, "configfs", 0, NULL) != 0) {
        if (errno != EBUSY) {
            perror("[ERR] Помилка монтування ConfigFS");
            return -errno;
        }
    }

    if (stat(OVERLAYS_PATH, &st) != 0 || !S_ISDIR(st.st_mode)) {
        fprintf(stderr, "[ERR] Ядро не підтримує підсистему DTBO ConfigFS (%s)\n", OVERLAYS_PATH);
        return -ENOPROTOOPT;
    }

    return 0;
}

/* Перевірка заголовка бінарного файлу DTBO */
static bool validate_dtbo_header(const uint8_t *buf, size_t size) {
    if (size < sizeof(struct fdt_header)) {
        fprintf(stderr, "[ERR] Файл занадто малий для заголовка FDT\n");
        return false;
    }

    const struct fdt_header *hdr = (const struct fdt_header *)buf;
    uint32_t magic = fdt32_to_cpu(hdr->magic);
    uint32_t totalsize = fdt32_to_cpu(hdr->totalsize);

    if (magic != FDT_MAGIC) {
        fprintf(stderr, "[ERR] Некоректний magic FDT: 0x%08x (очікувалося 0x%08x)\n", magic, FDT_MAGIC);
        return false;
    }

    if (totalsize > size) {
        fprintf(stderr, "[ERR] Заявлений розмір FDT (%u) перевищує розмір файлу (%zu)\n", totalsize, size);
        return false;
    }

    return true;
}

/* Завантаження та накладання оверлею */
int dtbo_apply(const char *overlay_name, const char *dtbo_filepath) {
    char target_dir[512];
    char dtbo_attr[512];
    char status_attr[512];
    uint8_t *buffer = NULL;
    int res = -1;
    int fd = -1;
    ssize_t nread, nwritten;
    struct stat st;

    if (ensure_configfs_mounted() != 0) {
        return -1;
    }

    fd = open(dtbo_filepath, O_RDONLY);
    if (fd < 0) {
        perror("[ERR] Помилка відкриття DTBO файлу");
        return -1;
    }

    if (fstat(fd, &st) != 0) {
        perror("[ERR] Помилка fstat");
        goto out_close_fd;
    }

    size_t file_size = (size_t)st.st_size;
    buffer = (uint8_t *)malloc(file_size);
    if (!buffer) {
        fprintf(stderr, "[ERR] Нестача пам'яті для читання DTBO\n");
        goto out_close_fd;
    }

    nread = read(fd, buffer, file_size);
    if (nread != (ssize_t)file_size) {
        fprintf(stderr, "[ERR] Неповне читання DTBO файлу\n");
        goto out_free_buf;
    }
    close(fd);
    fd = -1;

    if (!validate_dtbo_header(buffer, file_size)) {
        goto out_free_buf;
    }

    snprintf(target_dir, sizeof(target_dir), "%s/%s", OVERLAYS_PATH, overlay_name);
    if (mkdir(target_dir, 0755) != 0) {
        if (errno == EEXIST) {
            /* Каталог створив хтось інший — не чіпаємо чужий оверлей:
               інакше на будь-якій помилці нижче ми зробили б rmdir для нього. */
            fprintf(stderr, "[ERR] Оверлей %s вже існує\n", overlay_name);
        } else {
            perror("[ERR] Помилка створення каталогу оверлею в ConfigFS");
        }
        goto out_free_buf;
    }

    snprintf(dtbo_attr, sizeof(dtbo_attr), "%s/dtbo", target_dir);
    fd = open(dtbo_attr, O_WRONLY);
    if (fd < 0) {
        perror("[ERR] Помилка відкриття атрибута dtbo");
        rmdir(target_dir);
        goto out_free_buf;
    }

    nwritten = write(fd, buffer, file_size);
    close(fd);
    fd = -1;

    if (nwritten != (ssize_t)file_size) {
        fprintf(stderr, "[ERR] Помилка запису бінарного блоку в ConfigFS\n");
        rmdir(target_dir);
        goto out_free_buf;
    }

    /* Перевірка статусу накладання у ядрі */
    snprintf(status_attr, sizeof(status_attr), "%s/status", target_dir);
    fd = open(status_attr, O_RDONLY);
    if (fd >= 0) {
        char status_buf[64] = {0};
        nread = read(fd, status_buf, sizeof(status_buf) - 1);
        close(fd);
        fd = -1;
        if (nread > 0) {
            status_buf[strcspn(status_buf, "\r\n")] = 0;
            if (strcmp(status_buf, "applied") != 0) {
                fprintf(stderr, "[ERR] Ядро відхилило оверлей: %s\n", status_buf);
                rmdir(target_dir);
                goto out_free_buf;
            }
        }
    }

    printf("[OK] Оверлей '%s' успішно застосовано в ядрі\n", overlay_name);
    res = 0;

out_free_buf:
    free(buffer);
out_close_fd:
    if (fd >= 0) {
        close(fd);
    }
    return res;
}

/* Демонтування оверлею */
int dtbo_remove(const char *overlay_name) {
    char target_dir[512];
    snprintf(target_dir, sizeof(target_dir), "%s/%s", OVERLAYS_PATH, overlay_name);

    if (rmdir(target_dir) != 0) {
        perror("[ERR] Помилка видалення оверлею з ConfigFS");
        return -1;
    }

    printf("[OK] Оверлей '%s' успішно демонтовано\n", overlay_name);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Використання: %s <apply|remove> <ім'я_оверлею> [файл.dtbo]\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "apply") == 0) {
        if (argc < 4) {
            fprintf(stderr, "Потрібно вказати шлях до файлу .dtbo\n");
            return 1;
        }
        return dtbo_apply(argv[2], argv[3]) == 0 ? 0 : 1;
    } else if (strcmp(argv[1], "remove") == 0) {
        return dtbo_remove(argv[2]) == 0 ? 0 : 1;
    }

    fprintf(stderr, "Невідома команда: %s\n", argv[1]);
    return 1;
}
