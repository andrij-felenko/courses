#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define EROFS_SUPER_MAGIC  0xE0F5E1E2
#define EROFS_SUPER_OFFSET 1024

#pragma pack(push, 1)
struct erofs_super_block_raw {
    uint32_t magic;
    uint32_t checksum;
    uint32_t feature_compat;
    uint8_t  blkszbits;
    uint8_t  sb_extslots;
    uint16_t root_nid;
    uint64_t inos;
    uint64_t build_time;
    uint32_t build_time_nsec;
    uint32_t blocks;
    uint32_t meta_blkaddr;
    uint32_t xattr_blkaddr;
    uint8_t  uuid[16];
    uint8_t  volume_name[16];
    uint32_t feature_incompat;
};
#pragma pack(pop)

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <path_to_erofs_img>\n", argv[0]);
        return 1;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити файл образу EROFS");
        return 1;
    }

    if (lseek(fd, EROFS_SUPER_OFFSET, SEEK_SET) != EROFS_SUPER_OFFSET) {
        perror("Помилка позиціонування lseek");
        close(fd);
        return 1;
    }

    struct erofs_super_block_raw sb;
    ssize_t res = read(fd, &sb, sizeof(sb));
    if (res != (ssize_t)sizeof(sb)) {
        perror("Помилка зчитування суперблоку");
        close(fd);
        return 1;
    }

    close(fd);

    if (sb.magic != EROFS_SUPER_MAGIC) {
        fprintf(stderr, "Помилка: некоректна сигнатура EROFS (0x%X != 0x%X)\n",
                sb.magic, EROFS_SUPER_MAGIC);
        return 1;
    }

    uint32_t block_size = 1U << sb.blkszbits;
    uint64_t total_bytes = (uint64_t)sb.blocks * block_size;
    uint64_t root_nid_offset = (uint64_t)sb.meta_blkaddr * block_size + (uint64_t)sb.root_nid * 32;

    printf("=== Метадані EROFS Суперблоку (C) ===\n");
    printf("Сигнатура Magic     : 0x%X (Успішно)\n", sb.magic);
    printf("Розмір блоку        : %u байт (blkszbits: %u)\n", block_size, sb.blkszbits);
    printf("Загалом блоків      : %u (%llu байт)\n", sb.blocks, (unsigned long long)total_bytes);
    printf("Адреса метаданих    : блок %u (зсув %llu B)\n",
           sb.meta_blkaddr, (unsigned long long)sb.meta_blkaddr * block_size);
    printf("Кореневий NID       : %u (зсув кореневого inode: %llu B)\n",
           sb.root_nid, (unsigned long long)root_nid_offset);
    printf("Прапорці incompat   : 0x%X\n", sb.feature_incompat);

    return 0;
}
