/* gptdump.c — перелік розділів GPT із сирого пристрою або файлу-образу.
   Складання: cc -O2 -Wall -Wextra -o gptdump gptdump.c
   Запуск:    sudo ./gptdump /dev/sda        ./gptdump disk.img [розмір-сектора] */
#define _FILE_OFFSET_BITS 64     /* інакше на 32-бітній збірці зсув понад 2 ГіБ не читається */
#define _DEFAULT_SOURCE
#include <endian.h>
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mount.h>          /* BLKSSZGET, BLKGETSIZE64 */
#include <sys/stat.h>
#include <unistd.h>

struct gpt_header {              /* рівно 92 байти на диску */
    char     signature[8];       /*  0  "EFI PART"                     */
    uint32_t revision;           /*  8                                 */
    uint32_t header_size;        /* 12  скільки байтів накриває сума   */
    uint32_t header_crc32;       /* 16  на час рахунку — нулі          */
    uint32_t reserved;           /* 20                                 */
    uint64_t my_lba;             /* 24  де лежить сам заголовок        */
    uint64_t alternate_lba;      /* 32  де лежить його копія           */
    uint64_t first_usable_lba;   /* 40                                 */
    uint64_t last_usable_lba;    /* 48                                 */
    uint8_t  disk_guid[16];      /* 56                                 */
    uint64_t entry_lba;          /* 72  сектор, з якого йде масив      */
    uint32_t num_entries;        /* 80                                 */
    uint32_t entry_size;         /* 84                                 */
    uint32_t array_crc32;        /* 88                                 */
} __attribute__((packed));
_Static_assert(sizeof(struct gpt_header) == 92, "без packed вийде 96");

struct gpt_entry {               /* рівно 128 байтів */
    uint8_t  type_guid[16];
    uint8_t  part_guid[16];
    uint64_t first_lba;
    uint64_t last_lba;           /* ВКЛЮЧНО */
    uint64_t attrs;
    uint8_t  name[72];           /* UTF-16LE, 36 знаків */
} __attribute__((packed));
_Static_assert(sizeof(struct gpt_entry) == 128, "запис мусить бути 128 байтів");

/* CRC32 з UEFI — той самий, що в Ethernet і zlib */
static uint32_t crc32_le(const void *buf, size_t len)
{
    const uint8_t *p = buf;
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= p[i];
        for (int k = 0; k < 8; k++)
            crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}

/* pread має право віддати менше, ніж просили, — дочитуємо */
static int read_exact(int fd, void *buf, size_t len, uint64_t off)
{
    uint8_t *p = buf;
    while (len) {
        ssize_t n = pread(fd, p, len, (off_t)off);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        if (n == 0) { errno = EIO; return -1; }        /* пристрій коротший, ніж обіцяв */
        p += n; off += (uint64_t)n; len -= (size_t)n;
    }
    return 0;
}

/* Логічний сектор і місткість: у пристрою питаємо ядро, у файлу беремо розмір */
static void geometry(int fd, uint32_t *ss, uint64_t *bytes)
{
    struct stat st;
    int lss = 0;
    *ss = 512; *bytes = 0;
    if (fstat(fd, &st) != 0) return;
    if (S_ISBLK(st.st_mode)) {
        if (ioctl(fd, BLKSSZGET, &lss) == 0 && lss > 0) *ss = (uint32_t)lss;
        if (ioctl(fd, BLKGETSIZE64, bytes) != 0) *bytes = 0;
    } else {
        *bytes = (uint64_t)st.st_size;
    }
}

/* Перші три поля GUID записані від молодшого байта, останні два — просто масив */
static void guid_str(const uint8_t *g, char *out)
{
    snprintf(out, 37, "%02X%02X%02X%02X-%02X%02X-%02X%02X-%02X%02X-%02X%02X%02X%02X%02X%02X",
             g[3], g[2], g[1], g[0], g[5], g[4], g[7], g[6],
             g[8], g[9], g[10], g[11], g[12], g[13], g[14], g[15]);
}

static void name_utf8(const uint8_t *src, char *dst, size_t cap)
{
    size_t o = 0;
    for (int i = 0; i < 36 && o + 4 < cap; i++) {
        uint32_t c = (uint32_t)src[2 * i] | ((uint32_t)src[2 * i + 1] << 8);
        if (c == 0) break;                                   /* назва скінчилася */
        if (c >= 0xD800 && c < 0xDC00 && i + 1 < 36) {        /* сурогатна пара */
            uint32_t lo = (uint32_t)src[2 * i + 2] | ((uint32_t)src[2 * i + 3] << 8);
            if (lo >= 0xDC00 && lo < 0xE000) {
                c = 0x10000 + ((c - 0xD800) << 10) + (lo - 0xDC00);
                i++;
            }
        }
        if (c < 0x80) {
            dst[o++] = (char)c;
        } else if (c < 0x800) {
            dst[o++] = (char)(0xC0 | (c >> 6));
            dst[o++] = (char)(0x80 | (c & 0x3F));
        } else if (c < 0x10000) {
            dst[o++] = (char)(0xE0 | (c >> 12));
            dst[o++] = (char)(0x80 | ((c >> 6) & 0x3F));
            dst[o++] = (char)(0x80 | (c & 0x3F));
        } else {
            dst[o++] = (char)(0xF0 | (c >> 18));
            dst[o++] = (char)(0x80 | ((c >> 12) & 0x3F));
            dst[o++] = (char)(0x80 | ((c >> 6) & 0x3F));
            dst[o++] = (char)(0x80 | (c & 0x3F));
        }
    }
    dst[o] = '\0';
}

/* Заголовок із сектора lba, перевірений цілком. 0 — не сходиться. */
static int read_header(int fd, uint64_t lba, uint32_t ss, struct gpt_header *out)
{
    uint8_t *sect = malloc(ss);
    int ok = 0;
    if (!sect) return 0;
    if (read_exact(fd, sect, ss, lba * (uint64_t)ss) == 0) {
        const struct gpt_header *h = (const struct gpt_header *)sect;
        uint32_t hsize = le32toh(h->header_size);
        if (memcmp(h->signature, "EFI PART", 8) == 0 &&
            hsize >= sizeof(*h) && hsize <= ss &&
            le64toh(h->my_lba) == lba) {
            uint32_t want = le32toh(h->header_crc32);
            memset(sect + offsetof(struct gpt_header, header_crc32), 0, 4);
            if (crc32_le(sect, hsize) == want) {
                memcpy(out, sect, sizeof(*out));
                ok = 1;
            }
        }
    }
    free(sect);
    return ok;
}

int main(int argc, char **argv)
{
    static const uint8_t zero[16] = { 0 };
    struct gpt_header h;
    const char *src = "основна";
    uint32_t ss, n, esz;
    uint64_t bytes, last;
    uint8_t *arr;
    size_t pt;
    char g[37], name[3 * 36 + 1];
    int fd;

    if (argc < 2) {
        fprintf(stderr, "вжиток: %s <пристрій|образ> [розмір-сектора]\n", argv[0]);
        return 2;
    }
    if ((fd = open(argv[1], O_RDONLY)) < 0) { perror(argv[1]); return 1; }

    geometry(fd, &ss, &bytes);
    if (argc > 2) ss = (uint32_t)strtoul(argv[2], NULL, 10);
    if (ss < 512 || bytes < 3 * (uint64_t)ss) {
        fprintf(stderr, "неправдоподібна геометрія: сектор %" PRIu32 ", місткість %" PRIu64 "\n",
                ss, bytes);
        return 1;
    }
    last = bytes / ss - 1;

    if (!read_header(fd, 1, ss, &h)) {                 /* основна копія не зійшлася */
        src = "РЕЗЕРВНА";
        if (!read_header(fd, last, ss, &h)) {
            fprintf(stderr, "GPT не знайдено: жодна з копій не сходиться\n");
            return 1;
        }
    }

    n = le32toh(h.num_entries);
    esz = le32toh(h.entry_size);
    if (n == 0 || n > 4096 || esz < sizeof(struct gpt_entry) || esz % 128) {
        fprintf(stderr, "неправдоподібний масив: %" PRIu32 " × %" PRIu32 "\n", n, esz);
        return 1;
    }
    pt = (size_t)n * esz;
    if (!(arr = malloc(pt))) { fprintf(stderr, "мало пам'яті\n"); return 1; }
    if (read_exact(fd, arr, pt, le64toh(h.entry_lba) * (uint64_t)ss) != 0) {
        perror("масив записів");
        return 1;
    }
    if (crc32_le(arr, pt) != le32toh(h.array_crc32)) {
        fprintf(stderr, "CRC32 масиву записів не сходиться\n");
        return 1;
    }

    guid_str(h.disk_guid, g);
    printf("сектор %" PRIu32 " Б · останній LBA %" PRIu64 " · копія таблиці: %s\n", ss, last, src);
    printf("диск %s · записів %" PRIu32 " по %" PRIu32 " Б\n\n", g, n, esz);

    for (uint32_t i = 0; i < n; i++) {
        const struct gpt_entry *e = (const struct gpt_entry *)(arr + (size_t)i * esz);
        uint64_t a, b;
        if (memcmp(e->type_guid, zero, 16) == 0) continue;    /* порожній запис */
        a = le64toh(e->first_lba);
        b = le64toh(e->last_lba);
        guid_str(e->type_guid, g);
        name_utf8(e->name, name, sizeof(name));
        printf("%2" PRIu32 " %10" PRIu64 " %10" PRIu64 " %9.1f МіБ  %s  %s\n",
               i + 1, a, b, (double)(b - a + 1) * ss / 1048576.0, g, name);
    }

    free(arr);
    close(fd);
    return 0;
}
