/* cpio_parser.c — Парсер cpio newc мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>

#define CPIO_MAGIC_NEWC "070701"
#define CPIO_MAGIC_CRC  "070702"
#define CPIO_TRAILER    "TRAILER!!!"
#define MAX_HARDLINKS   256

struct cpio_newc_header {
    char c_magic[6];
    char c_ino[8];
    char c_mode[8];
    char c_uid[8];
    char c_gid[8];
    char c_nlink[8];
    char c_mtime[8];
    char c_filesize[8];
    char c_maj[8];
    char c_min[8];
    char c_rmaj[8];
    char c_rmin[8];
    char c_namesize[8];
    char c_chksum[8];
};

struct hardlink_entry {
    uint32_t ino;
    char path[512];
};

static struct hardlink_entry g_hardlinks[MAX_HARDLINKS];
static size_t g_hardlink_count = 0;

/* Безпечна конверсія 8-значного hex ASCII в uint32_t без sscanf */
static uint32_t parse_hex8(const char *hex_str) {
    uint32_t val = 0;
    for (int i = 0; i < 8; ++i) {
        char c = hex_str[i];
        val <<= 4;
        if (c >= '0' && c <= '9')      val |= (c - '0');
        else if (c >= 'A' && c <= 'F') val |= (c - 'A' + 10);
        else if (c >= 'a' && c <= 'f') val |= (c - 'a' + 10);
    }
    return val;
}

/* Обчислення падінгу до межі 4 байтів */
static inline size_t align4(size_t offset) {
    return (4 - (offset % 4)) % 4;
}

/* Перевірка на відсутність виходу за межі батьків Path Traversal */
static int is_safe_path(const char *path) {
    if (strstr(path, "../") != NULL || strstr(path, "/..") != NULL) {
        return 0;
    }
    return 1;
}

/* Рекурсивне створення батьківських каталогів */
static void make_parent_dirs(char *path) {
    char *p = path;
    if (*p == '/') p++;
    while ((p = strchr(p, '/')) != NULL) {
        *p = '\0';
        mkdir(path, 0755);
        *p = '/';
        p++;
    }
}

/* Створення описувача файлової системи за типом у mode */
static int extract_node(const char *path, uint32_t ino, uint32_t mode, 
                        const uint8_t *data, uint32_t filesize) {
    uint32_t file_type = mode & 0170000;
    mode_t perms = mode & 07777;

    if (!is_safe_path(path)) {
        fprintf(stderr, "Попередження: Блоковано небезпечний шлях: %s\n", path);
        return -1;
    }

    /* Перевірка наявних жорстких посилань за номер іноди */
    if (file_type == 0100000 && filesize == 0) {
        for (size_t i = 0; i < g_hardlink_count; ++i) {
            if (g_hardlinks[i].ino == ino) {
                link(g_hardlinks[i].path, path);
                return 0;
            }
        }
    }

    if (file_type == 0040000) { /* S_IFDIR */
        char path_copy[1024];
        strncpy(path_copy, path, sizeof(path_copy));
        make_parent_dirs(path_copy);
        mkdir(path, perms);
    } else if (file_type == 0100000) { /* S_IFREG */
        char path_copy[1024];
        strncpy(path_copy, path, sizeof(path_copy));
        make_parent_dirs(path_copy);

        int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, perms);
        if (fd < 0) return -1;
        if (filesize > 0) {
            ssize_t written = write(fd, data, filesize);
            (void)written;
        }
        close(fd);

        /* Реєстрація першого файлу для жорстких посилань */
        if (g_hardlink_count < MAX_HARDLINKS) {
            g_hardlinks[g_hardlink_count].ino = ino;
            strncpy(g_hardlinks[g_hardlink_count].path, path, 512);
            g_hardlink_count++;
        }
    } else if (file_type == 0120000) { /* S_IFLNK */
        char target[512] = {0};
        if (filesize < sizeof(target)) {
            memcpy(target, data, filesize);
            symlink(target, path);
        }
    }
    return 0;
}

/* Головний цикл парсингу буфера cpio */
int unpack_cpio_buffer(const uint8_t *buf, size_t buf_size, const char *out_dir) {
    size_t off = 0;
    char path_buf[1024];
    g_hardlink_count = 0;

    while (off + sizeof(struct cpio_newc_header) <= buf_size) {
        const struct cpio_newc_header *hdr = (const struct cpio_newc_header *)(buf + off);

        if (memcmp(hdr->c_magic, CPIO_MAGIC_NEWC, 6) != 0 &&
            memcmp(hdr->c_magic, CPIO_MAGIC_CRC, 6) != 0) {
            fprintf(stderr, "Помилка: Невірний magic header за зсувом %zu\n", off);
            return -1;
        }

        uint32_t ino      = parse_hex8(hdr->c_ino);
        uint32_t mode     = parse_hex8(hdr->c_mode);
        uint32_t filesize = parse_hex8(hdr->c_filesize);
        uint32_t namesize = parse_hex8(hdr->c_namesize);

        off += sizeof(struct cpio_newc_header);

        if (off + namesize > buf_size) {
            fprintf(stderr, "Помилка: Заголовок виходить за межі буфера\n");
            return -1;
        }

        const char *name = (const char *)(buf + off);
        if (namesize == 0 || name[namesize - 1] != '\0') {
            fprintf(stderr, "Помилка: Імена файлів мають завершуватися NUL\n");
            return -1;
        }

        /* Перевірка маркера кінця архіву */
        if (strcmp(name, CPIO_TRAILER) == 0) {
            printf("Успішно знайдено маркер " CPIO_TRAILER ". Завершення розпакування.\n");
            return 0;
        }

        off += namesize;
        off += align4(sizeof(struct cpio_newc_header) + namesize);

        if (off + filesize > buf_size) {
            fprintf(stderr, "Помилка: Дані файлу виходять за межі буфера\n");
            return -1;
        }

        const uint8_t *data = buf + off;

        /* Формування повного шляху призначення */
        snprintf(path_buf, sizeof(path_buf), "%s/%s", out_dir, name);

        /* Пропуск поточного каталогу "." */
        if (strcmp(name, ".") != 0) {
            extract_node(path_buf, ino, mode, data, filesize);
        }

        off += filesize;
        off += align4(filesize);
    }
    return 0;
}
