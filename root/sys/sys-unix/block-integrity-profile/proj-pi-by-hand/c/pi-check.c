/* pi-check.c — порахувати захисну інформацію самотужки й звірити з носієм.
 *   cc -O2 -Wall -Wextra -std=gnu11 -o pi-check pi-check.c
 *   sudo ./pi-check -s 2099200 /dev/nvme0n1 100 5
 *        ./pi-check -I -b 4096 dump.bin 0 5
 *
 *  -I         шлях — файл-образ із записами по (блок + службові) байтів
 *  -b <Б>     розмір логічного блока (типово питаємо в ядра)
 *  -m <Б>     службових байтів на блок (типово 8)
 *  -s <сект>  початок розділу так, як його дає /sys/class/block/<part>/start,
 *             тобто в секторах по 512 Б незалежно від розміру блока
 *  -F         захист у ПЕРШИХ восьми байтах службових (DPS біт 3), а не в останніх
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <getopt.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <linux/nvme_ioctl.h>

/* — сюди йдуть crc_bit, tab_init, crc_tab, struct pi_tuple, be16, be32, nvme_read — */

static int img_read(int fd, uint64_t rec, unsigned bs, unsigned ms,
                    uint8_t *data, uint8_t *meta)
{
    off_t off = (off_t)rec * (bs + ms);          /* запис = блок + службові байти */

    if (pread(fd, data, bs, off) != (ssize_t)bs) { perror("pread даних"); return -1; }
    if (pread(fd, meta, ms, off + bs) != (ssize_t)ms) { perror("pread тегів"); return -1; }
    return 0;
}

int main(int argc, char **argv)
{
    unsigned bs = 0, ms = 8, count = 1;
    uint64_t part_sect = 0;
    int is_img = 0, pi_first = 0, opt;

    while ((opt = getopt(argc, argv, "Ib:m:s:F")) != -1)
        switch (opt) {
        case 'I': is_img = 1; break;
        case 'b': bs = (unsigned)strtoul(optarg, NULL, 0); break;
        case 'm': ms = (unsigned)strtoul(optarg, NULL, 0); break;
        case 's': part_sect = strtoull(optarg, NULL, 0); break;
        case 'F': pi_first = 1; break;
        default:  return 2;
        }

    if (argc - optind < 2) {
        fprintf(stderr, "вжиток: pi-check [-I] [-b блок] [-m службових] "
                        "[-s зсув-розділу] [-F] <шлях> <LBA> [кількість]\n");
        return 2;
    }
    const char *path = argv[optind];
    uint64_t lba0 = strtoull(argv[optind + 1], NULL, 0);
    if (argc - optind > 2) count = (unsigned)strtoul(argv[optind + 2], NULL, 0);

    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror(path); return 1; }

    uint32_t nsid = 0;
    if (!is_img) {
        int id = ioctl(fd, NVME_IOCTL_ID);        /* заразом і перевірка, що це NVMe */
        if (id < 0) { perror("NVME_IOCTL_ID"); return 1; }
        nsid = (uint32_t)id;
        int sz = 0;
        if (!bs && ioctl(fd, BLKSSZGET, &sz) == 0) bs = (unsigned)sz;
    }
    if (!bs) bs = 4096;
    if (ms < sizeof(struct pi_tuple) || ms > 4096) {
        fprintf(stderr, "службових байтів на блок має бути від 8 до 4096\n");
        return 1;
    }

    /* зсув розділу sysfs дає в секторах по 512 Б — переводимо в логічні блоки */
    uint64_t part_lba = part_sect / (bs / 512);

    uint8_t *data, *meta;                         /* вирівняне — щоб ядро не копіювало */
    if (posix_memalign((void **)&data, 4096, bs)
        || posix_memalign((void **)&meta, 4096, 4096)) {
        fprintf(stderr, "не вистачило пам'яті\n");
        return 1;
    }

    tab_init();
    static const uint8_t probe[] = "123456789";
    printf("самоперевірка CRC-16/0x8BB7 над \"123456789\": %04x побітово, %04x таблицею"
           " (взірець d0db)\n", crc_bit(probe, 9), crc_tab(probe, 9));
    printf("блок %u Б, службових %u Б, зсув розділу %llu блоків\n",
           bs, ms, (unsigned long long)part_lba);
    puts("колонки: LBA · guard з носія · guard порахований · app · ref з носія · ref очікуваний");

    int bad = 0;
    for (unsigned i = 0; i < count; i++) {
        uint64_t lba = part_lba + lba0 + i;

        if (is_img ? img_read(fd, lba0 + i, bs, ms, data, meta)
                   : nvme_read(fd, nsid, lba, data, bs, meta, ms))
            { bad = 1; continue; }

        const struct pi_tuple *t = (const struct pi_tuple *)
                (pi_first ? meta : meta + ms - sizeof(struct pi_tuple));

        uint16_t g_dev = be16(t->guard), g_our = crc_tab(data, bs);
        uint16_t app   = be16(t->app);
        uint32_t r_dev = be32(t->ref), r_our = (uint32_t)lba;
        const char *verdict = "ок";

        if (app == 0xffff) {                         /* стандарт: перевірок для блока нема */
            verdict = "перевірку вимкнено (app=ffff)";
        } else if (g_dev != g_our || r_dev != r_our) {
            bad = 1;
            if (g_dev != g_our && r_dev != r_our) verdict = "✖ вартовий і посилальний";
            else if (g_dev != g_our) verdict = "✖ вартовий: дані не ті, що накривав тег";
            else                     verdict = "✖ посилальний: блок не з цієї адреси";
        }

        printf("%10llu   %04x   %04x   %04x   %08x %08x   %s\n",
               (unsigned long long)lba, g_dev, g_our, app, r_dev, r_our, verdict);
    }
    return bad;
}
