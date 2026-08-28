#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <endian.h>
#include <sys/types.h>
#include <sys/stat.h>

#define LUKS2_MAGIC       "LUKS\xba\xbe"
#define LUKS2_MAGIC_L     6
#define LUKS2_HDR_SIZE    4096
#define DEFAULT_HDR_SIZE  (4 * 1024 * 1024)

struct luks2_hdr_disk {
    char     magic[LUKS2_MAGIC_L];
    uint16_t version;
    uint64_t hdr_size;
    uint64_t seqid;
    char     label[48];
    char     csum_alg[32];
    uint8_t  salt[64];
    char     uuid[44];
    char     subsystem[48];
    uint64_t hdr_offset;
    uint8_t  _padding[184];
    uint8_t  csum[64];
    uint8_t  _pad_to_4k[3584];
} __attribute__((packed));

static int parse_luks2_header(int fd, off_t offset, const char *name, struct luks2_hdr_disk *out_hdr) {
    if (lseek(fd, offset, SEEK_SET) == (off_t)-1) {
        perror("Помилка lseek при позиціонуванні");
        return -1;
    }

    ssize_t rd = read(fd, out_hdr, sizeof(struct luks2_hdr_disk));
    if (rd != sizeof(struct luks2_hdr_disk)) {
        fprintf(stderr, "[%s] Помилка зчитування 4096 байтів дескриптора\n", name);
        return -1;
    }

    if (memcmp(out_hdr->magic, LUKS2_MAGIC, LUKS2_MAGIC_L) != 0) {
        fprintf(stderr, "[%s] Сигнатура magic не збігається з еталоном LUKS2\n", name);
        return -1;
    }

    uint16_t ver = be16toh(out_hdr->version);
    uint64_t hdr_sz = be64toh(out_hdr->hdr_size);
    uint64_t seq = be64toh(out_hdr->seqid);
    uint64_t off = be64toh(out_hdr->hdr_offset);

    printf("=== %s (Зсув: 0x%lx) ===\n", name, (unsigned long)offset);
    printf("  Версія формату:      %u\n", ver);
    printf("  Розмір метаданих:    %lu байтів (%lu МіБ)\n", (unsigned long)hdr_sz, (unsigned long)(hdr_sz / (1024 * 1024)));
    printf("  Номер транзакції:    %lu (seqid)\n", (unsigned long)seq);
    printf("  Мітка (Label):       %.48s\n", out_hdr->label[0] ? out_hdr->label : "<пусто>");
    printf("  Підсистема:          %.48s\n", out_hdr->subsystem[0] ? out_hdr->subsystem : "<пусто>");
    printf("  UUID тому:           %.44s\n", out_hdr->uuid);
    printf("  Алгоритм суми:       %.32s\n", out_hdr->csum_alg);
    printf("  Записаний зсув:      0x%lx\n", (unsigned long)off);

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <пристрій_або_файл_образу>\n", argv[0]);
        return 1;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити цільовий пристрій");
        return 1;
    }

    struct luks2_hdr_disk primary_hdr, secondary_hdr;
    int p_ok = parse_luks2_header(fd, 0, "Первинний заголовок", &primary_hdr);

    uint64_t sec_offset = DEFAULT_HDR_SIZE;
    if (p_ok == 0) {
        sec_offset = be64toh(primary_hdr.hdr_size);
    }

    int s_ok = parse_luks2_header(fd, (off_t)sec_offset, "Вторинний заголовок", &secondary_hdr);

    if (p_ok != 0 && s_ok != 0) {
        fprintf(stderr, "Критична помилка: на носії відсутні дійсні заголовки LUKS2.\n");
        close(fd);
        return 1;
    }

    uint64_t p_seq = p_ok == 0 ? be64toh(primary_hdr.seqid) : 0;
    uint64_t s_seq = s_ok == 0 ? be64toh(secondary_hdr.seqid) : 0;

    printf("\n--- Арбітраж стану заголовків ---\n");
    if (p_ok == 0 && s_ok == 0) {
        if (p_seq >= s_seq) {
            printf("Активним є ПЕРВИННИЙ заголовок (seqid = %lu >= %lu)\n", (unsigned long)p_seq, (unsigned long)s_seq);
        } else {
            printf("Активним є ВТОРИННИЙ заголовок (seqid = %lu > %lu)\n", (unsigned long)s_seq, (unsigned long)p_seq);
        }
    } else if (p_ok == 0) {
        printf("Вторинний заголовок пошкоджено. Активним є ПЕРВИННИЙ (seqid = %lu)\n", (unsigned long)p_seq);
    } else {
        printf("Первинний заголовок пошкоджено. Активним є ВТОРИННИЙ (seqid = %lu)\n", (unsigned long)s_seq);
    }

    close(fd);
    return 0;
}
