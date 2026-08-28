#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

#define EXT4_SUPERBLOCK_OFFSET 1024
#define EXT4_MAGIC             0xEF53
#define XFS_MAGIC              0x58465342 /* ASCII 'XFSB' */
#define BTRFS_MAGIC_OFFSET     65536
#define BTRFS_MAGIC_STR        "_BHRfS_M"

/* Спрощена структура заголовка первинного суперблоку Ext4 */
struct ext4_sb_header {
    uint32_t s_inodes_count;
    uint32_t s_blocks_count_lo;
    uint32_t s_r_blocks_count_lo;
    uint32_t s_free_blocks_count_lo;
    uint32_t s_free_inodes_count;
    uint32_t s_first_data_block;
    uint32_t s_log_block_size;
    uint32_t s_log_cluster_size;
    uint32_t s_blocks_per_group;
    uint32_t s_clusters_per_group;
    uint32_t s_inodes_per_group;
    uint32_t s_mtime;
    uint32_t s_wtime;
    uint16_t s_mnt_count;
    uint16_t s_max_mnt_count;
    uint16_t s_magic;
    uint16_t s_state;
    uint16_t s_errors;
    uint16_t s_minor_rev_level;
    uint32_t s_lastcheck;
    uint32_t s_checkinterval;
    uint32_t s_creator_os;
    uint32_t s_rev_level;
    uint16_t s_def_resuid;
    uint16_t s_def_resgid;
    uint32_t s_first_ino;
    uint16_t s_inode_size;
    uint16_t s_block_group_nr;
    uint32_t s_feature_compat;
    uint32_t s_feature_incompat;
    uint32_t s_feature_ro_compat;
    uint8_t  s_uuid[16];
} __attribute__((packed));

static void check_device_holders(const char *dev_path) {
    const char *base = strrchr(dev_path, '/');
    if (!base) return;
    base++; /* Пропускаємо '/' */

    char sys_path[512];
    snprintf(sys_path, sizeof(sys_path), "/sys/class/block/%s/holders", base);

    DIR *d = opendir(sys_path);
    if (!d) return;

    struct dirent *dir;
    printf("[!] Знайдено активні холдери ядра у %s:\n", sys_path);
    while ((dir = readdir(d)) != NULL) {
        if (dir->d_name[0] != '.') {
            printf("    -> Захоплено блоковим драйвером: /dev/%s\n", dir->d_name);
        }
    }
    closedir(d);
}

static int is_power_of(int n, int base) {
    if (n <= 0) return 0;
    while (n % base == 0) n /= base;
    return n == 1;
}

static int has_backup_superblock(int group) {
    if (group == 0 || group == 1) return 1;
    return is_power_of(group, 3) || is_power_of(group, 5) || is_power_of(group, 7);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_блокового_пристрою>\n", argv[0]);
        return 1;
    }

    const char *dev_path = argv[1];
    printf("[*] Аналіз блокового пристрою: %s\n", dev_path);

    /* Крок 1: Перевірка ексклюзивного блокування */
    int fd = open(dev_path, O_RDONLY | O_EXCL);
    if (fd < 0) {
        if (errno == EBUSY) {
            printf("[-] EBUSY: Пристрій захоплено ексклюзивно іншим драйвером або процесом!\n");
            check_device_holders(dev_path);
            printf("[*] Спроба повторного відкриття без O_EXCL у режимі читання...\n");
            fd = open(dev_path, O_RDONLY);
        }
        if (fd < 0) {
            perror("[-] Критична помилка відкриття пристрою");
            return 1;
        }
    } else {
        printf("[+] Блоковий пристрій вільний (O_EXCL успішно захоплено)\n");
    }

    uint64_t dev_size = 0;
    if (ioctl(fd, BLKGETSIZE64, &dev_size) == 0) {
        printf("[+] Розмір пристрою: %lu байтів (%.2f ГіБ)\n", dev_size, dev_size / (1024.0 * 1024.0 * 1024.0));
    }

    /* Крок 2: Зчитування та перевірка Ext4 */
    struct ext4_sb_header ext4_sb;
    ssize_t rd = pread(fd, &ext4_sb, sizeof(ext4_sb), EXT4_SUPERBLOCK_OFFSET);
    if (rd == sizeof(ext4_sb)) {
        if (ext4_sb.s_magic == EXT4_MAGIC) {
            uint32_t block_size = 1024 << ext4_sb.s_log_block_size;
            printf("[+] Виявлено файлову систему Ext2/3/4:\n");
            printf("    - Magic: 0x%04X (Валідний)\n", ext4_sb.s_magic);
            printf("    - Розмір блоку: %u байтів\n", block_size);
            printf("    - Блоків у групі: %u\n", ext4_sb.s_blocks_per_group);
            printf("    - Стан ФС: 0x%04X (%s)\n", ext4_sb.s_state,
                   (ext4_sb.s_state & 0x0001) ? "Clean/Valid" : "Dirty/Errors");
            printf("    - Incompat flags: 0x%08X\n", ext4_sb.s_feature_incompat);
            if (ext4_sb.s_feature_incompat & 0x0004) {
                printf("    - [!] Прапорець відновлення NEEDS_RECOVERY активний (брудний журнал)!\n");
            }

            printf("\n[*] Розрахунок резервних суперблоків Ext4 (Sparse Superblock):\n");
            int found_backups = 0;
            for (int g = 1; g < 100 && found_backups < 5; g++) {
                if (has_backup_superblock(g)) {
                    uint64_t sb_block = (uint64_t)g * ext4_sb.s_blocks_per_group;
                    if (block_size == 1024) sb_block++; /* Зсув для блоку 1K */
                    uint64_t byte_offset = sb_block * block_size;

                    struct ext4_sb_header backup_sb;
                    if (pread(fd, &backup_sb, sizeof(backup_sb), byte_offset) == sizeof(backup_sb)) {
                        if (backup_sb.s_magic == EXT4_MAGIC) {
                            printf("    -> Група %2d: Блок %-8lu (Зміщення: %-12lu B) | Magic: 0x%04X [OK]\n",
                                   g, sb_block, byte_offset, backup_sb.s_magic);
                            found_backups++;
                        }
                    }
                }
            }
            close(fd);
            return 0;
        }
    }

    /* Крок 3: Перевірка сигнатури XFS */
    uint32_t xfs_magic = 0;
    if (pread(fd, &xfs_magic, sizeof(xfs_magic), 0) == sizeof(xfs_magic)) {
        if (xfs_magic == XFS_MAGIC) {
            printf("[+] Виявлено файлову систему XFS (Magic 'XFSB' за зміщенням 0)\n");
            close(fd);
            return 0;
        }
    }

    /* Крок 4: Перевірка сигнатури Btrfs */
    char btrfs_sig[9] = {0};
    if (pread(fd, btrfs_sig, 8, BTRFS_MAGIC_OFFSET + 0x40) == 8) {
        if (memcmp(btrfs_sig, BTRFS_MAGIC_STR, 8) == 0) {
            printf("[+] Виявлено файлову систему Btrfs (Magic '%s' за зміщенням 64 КіБ + 0x40)\n", btrfs_sig);
            close(fd);
            return 0;
        }
    }

    printf("[-] Не вдалося знайти жодного відомого суперблоку (Ext4/XFS/Btrfs).\n");
    printf("[-] Первинні сектори можуть бути пошкодженими, затертими або розділ має зміщений оффсет.\n");

    close(fd);
    return 2;
}
