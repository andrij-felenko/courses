# ⚙️ Сканер суперблоків: пряме зчитування геометрії, валідація магічних чисел та пошук холдерів

Коли утиліта `mount(8)` повертає загальну помилку `wrong fs type, bad option, bad superblock` або `target is busy`, стандартні системні утиліти простору користувача не дають відповіді на головні діагностичні питання: чи фізично пошкоджено первинний сектор носія, чи розділ утримується іншим драйвером ядра, чи магічне число взагалі відсутнє на диску. Цей проект реалізує спеціалізовану діагностичну утиліту `sb-inspect`, яка напряму взаємодіє з блоковим рівнем та ядром Linux для виявлення справжньої причини збою.

## Архітектура та принцип роботи діагностичного сканера

Утиліта `sb-inspect` розв'язує три ключові інженерні завдання під час діагностики немонтованого накопичувача:

1. **Тестування ексклюзивного блокування ядра (`O_EXCL`):** Спроба відкрити блоковий пристрій із прапорцем `O_EXCL`. У ядрі Linux операція `open(path, O_EXCL)` над блоковим пристроєм активує механізм `bd_open_exclusive`. Якщо пристрій уже захоплений іншим драйвером (наприклад, підсистемою LVM, модулем шифрування dm-crypt чи програмним RAID mdadm), виклик негайно завершується з помилкою `EBUSY`. У цьому випадку утиліта звертається до підсистеми `sysfs` (`/sys/class/block/*/holders/`), щоб виявити точне ім'я драйвера-блокувальника.
2. **Пряме зчитування первинних суперблоків у обхід VFS:** Зчитування байтів безпосередньо з фізичних зміщень основних файлових систем (Ext4 — зміщення 1024 байти, XFS — зміщення 0 байтів, Btrfs — зміщення 64 КіБ) через системний виклик `pread()`. Це дозволяє перевірити цілісність дискових констант навіть тоді, коли ядро відмовляється монтувати том через несумісні опції чи пошкоджений журнал.
3. **Обчислення та валідація резервних суперблоків Ext4:** Якщо первинний суперблок пошкоджено, сканер аналізує геометрію блокових груп за правилом розріджених суперблоків (*Sparse Superblock*) і перевіряє цілісність дублікатів у групах 1, 3, 5, 7, 9 для подальшого відновлення через команду `e2fsck -b <block_number>`.

### Математична модель розріджених суперблоків Ext4

У файловій системі Ext4 за замовчуванням увімкнено прапорець `sparse_super`. Замість збереження копії суперблоку в кожній без винятку групі блоків (що марно витрачало б дисковий простір на томах із тисячами груп), резервні суперблоки записуються лише в Групі 0, Групі 1 та в групах, чий порядковий номер є степенем чисел 3, 5 або 7:

```
Групи, що містять резервний суперблок Ext4:
├── Група 0:  Основний суперблок (зміщення 1024 байти від початку розділу)
├── Група 1:  Степінь 3⁰ (Блок 32 768 при розмірі блоку 4 КіБ)
├── Група 3:  Степінь 3¹ (Блок 98 304)
├── Група 5:  Степінь 5¹ (Блок 163 840)
├── Група 7:  Степінь 7¹ (Блок 229 376)
├── Група 9:  Степінь 3² (Блок 294 912)
├── Група 25: Степінь 5² (Блок 819 200)
├── Група 27: Степінь 3³ (Блок 884 736)
└── Група 49: Степінь 7² (Блок 1 605 632)
```

Номер цільового блоку для довільної групи `G` при стандартному розмірі блоку 4096 байтів обчислюється за формулою:

```
TargetBlock(G) = G · blocks_per_group

Фізичне зміщення на носії у байтах:
ByteOffset(G) = TargetBlock(G) · block_size
```

Якщо розмір блоку файлової системи становить 1024 байти (`s_log_block_size = 0`), нульовий блок повністю віддається під завантажувальну область x86/MBR, тому перший блок даних має номер 1, а формула набуває вигляду: `TargetBlock(G) = (G · blocks_per_group) + 1`.

## Реалізація інструмента `sb-inspect`

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <expected>
#include <format>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

namespace fs = std::filesystem;

constexpr uint64_t Ext4SuperblockOffset = 1024;
constexpr uint16_t Ext4Magic = 0xEF53;
constexpr uint32_t XfsMagic = 0x58465342;
constexpr uint64_t BtrfsMagicOffset = 65536;
constexpr std::string_view BtrfsMagicStr = "_BHRfS_M";

struct [[gnu::packed]] Ext4SuperblockHeader {
    uint32_t inodes_count;
    uint32_t blocks_count_lo;
    uint32_t r_blocks_count_lo;
    uint32_t free_blocks_count_lo;
    uint32_t free_inodes_count;
    uint32_t first_data_block;
    uint32_t log_block_size;
    uint32_t log_cluster_size;
    uint32_t blocks_per_group;
    uint32_t clusters_per_group;
    uint32_t inodes_per_group;
    uint32_t mtime;
    uint32_t wtime;
    uint16_t mnt_count;
    uint16_t max_mnt_count;
    uint16_t magic;
    uint16_t state;
    uint16_t errors;
    uint16_t minor_rev_level;
    uint32_t lastcheck;
    uint32_t checkinterval;
    uint32_t creator_os;
    uint32_t rev_level;
    uint16_t def_resuid;
    uint16_t def_resgid;
    uint32_t first_ino;
    uint16_t inode_size;
    uint16_t block_group_nr;
    uint32_t feature_compat;
    uint32_t feature_incompat;
    uint32_t feature_ro_compat;
    uint8_t  uuid[16];
};

class FileDescriptor {
    int fd_ = -1;
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

static void printDeviceHolders(const fs::path& devPath) {
    const auto devName = devPath.filename().string();
    const fs::path holdersPath = fs::path("/sys/class/block") / devName / "holders";

    if (fs::exists(holdersPath) && fs::is_directory(holdersPath)) {
        std::cout << std::format("[!] Знайдено активні холдери ядра у {}:\n", holdersPath.string());
        for (const auto& entry : fs::directory_iterator(holdersPath)) {
            std::cout << std::format("    -> Захоплено блоковим драйвером: /dev/{}\n", entry.path().filename().string());
        }
    }
}

static constexpr bool isPowerOf(int n, int base) noexcept {
    if (n <= 0) return false;
    while (n % base == 0) n /= base;
    return n == 1;
}

static constexpr bool hasBackupSuperblock(int group) noexcept {
    if (group == 0 || group == 1) return true;
    return isPowerOf(group, 3) || isPowerOf(group, 5) || isPowerOf(group, 7);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << std::format("Використання: {} <шлях_до_блокового_пристрою>\n", argv[0]);
        return 1;
    }

    const fs::path devPath(argv[1]);
    std::cout << std::format("[*] Аналіз блокового пристрою: {}\n", devPath.string());

    /* Спроба відкриття з O_EXCL */
    int rawFd = ::open(devPath.c_str(), O_RDONLY | O_EXCL);
    if (rawFd < 0) {
        if (errno == EBUSY) {
            std::cout << "[-] EBUSY: Пристрій захоплено ексклюзивно іншим драйвером або процесом!\n";
            printDeviceHolders(devPath);
            std::cout << "[*] Спроба повторного відкриття без O_EXCL у режимі читання...\n";
            rawFd = ::open(devPath.c_str(), O_RDONLY);
        }
        if (rawFd < 0) {
            std::cerr << std::format("[-] Критична помилка відкриття пристрою: {}\n", std::strerror(errno));
            return 1;
        }
    } else {
        std::cout << "[+] Блоковий пристрій вільний (O_EXCL успішно захоплено)\n";
    }

    FileDescriptor dev(rawFd);

    uint64_t devSize = 0;
    if (::ioctl(dev.get(), BLKGETSIZE64, &devSize) == 0) {
        std::cout << std::format("[+] Розмір пристрою: {} байтів ({:.2f} ГіБ)\n",
                                 devSize, devSize / (1024.0 * 1024.0 * 1024.0));
    }

    /* Зчитування Ext4 */
    Ext4SuperblockHeader ext4Sb{};
    if (::pread(dev.get(), &ext4Sb, sizeof(ext4Sb), Ext4SuperblockOffset) == sizeof(ext4Sb)) {
        if (ext4Sb.magic == Ext4Magic) {
            const uint32_t blockSize = 1024u << ext4Sb.log_block_size;
            std::cout << std::format("[+] Виявлено файлову систему Ext2/3/4:\n");
            std::cout << std::format("    - Magic: 0x{:04X} (Валідний)\n", ext4Sb.magic);
            std::cout << std::format("    - Розмір блоку: {} байтів\n", blockSize);
            std::cout << std::format("    - Блоків у групі: {}\n", ext4Sb.blocks_per_group);
            std::cout << std::format("    - Стан ФС: 0x{:04X} ({})\n", ext4Sb.state,
                                     (ext4Sb.state & 0x0001) ? "Clean/Valid" : "Dirty/Errors");
            std::cout << std::format("    - Incompat flags: 0x{:08X}\n", ext4Sb.feature_incompat);
            if (ext4Sb.feature_incompat & 0x0004) {
                std::cout << "    - [!] Прапорець відновлення NEEDS_RECOVERY активний (брудний журнал)!\n";
            }

            std::cout << "\n[*] Розрахунок резервних суперблоків Ext4 (Sparse Superblock):\n";
            int foundBackups = 0;
            for (int g = 1; g < 100 && foundBackups < 5; ++g) {
                if (hasBackupSuperblock(g)) {
                    uint64_t sbBlock = static_cast<uint64_t>(g) * ext4Sb.blocks_per_group;
                    if (blockSize == 1024) sbBlock++;
                    const uint64_t byteOffset = sbBlock * blockSize;

                    Ext4SuperblockHeader backupSb{};
                    if (::pread(dev.get(), &backupSb, sizeof(backupSb), byteOffset) == sizeof(backupSb)) {
                        if (backupSb.magic == Ext4Magic) {
                            std::cout << std::format("    -> Група {:2}: Блок {:<8} (Зміщення: {:<12} B) | Magic: 0x{:04X} [OK]\n",
                                                     g, sbBlock, byteOffset, backupSb.magic);
                            foundBackups++;
                        }
                    }
                }
            }
            return 0;
        }
    }

    /* Зчитування XFS */
    uint32_t xfsMagic = 0;
    if (::pread(dev.get(), &xfsMagic, sizeof(xfsMagic), 0) == sizeof(xfsMagic)) {
        if (xfsMagic == XfsMagic) {
            std::cout << "[+] Виявлено файлову систему XFS (Magic 'XFSB' за зміщенням 0)\n";
            return 0;
        }
    }

    /* Зчитування Btrfs */
    char btrfsSig[9] = {0};
    if (::pread(dev.get(), btrfsSig, 8, BtrfsMagicOffset + 0x40) == 8) {
        if (std::string_view(btrfsSig, 8) == BtrfsMagicStr) {
            std::cout << std::format("[+] Виявлено файлову систему Btrfs (Magic '{}' за зміщенням 64 КіБ + 0x40)\n", btrfsSig);
            return 0;
        }
    }

    std::cout << "[-] Не вдалося знайти жодного відомого суперблоку (Ext4/XFS/Btrfs).\n";
    return 2;
}
```
:::

## Покроковий розбір коду та робота з ресурсами

Програма реалізує багаторівневий аналіз диска з детермінованим керуванням дескрипторами:

1. **Керування ресурсами через RAII у версії C++:** Клас `FileDescriptor` гарантує закриття файлового дескриптора при виході з будь-якої гілки виконання, запобігаючи витоку відкритих дескрипторів блокових пристроїв, що могло б додатково заблокувати пристрій у ядрі.
2. **Вимоги до структури `ext4_sb_header`:** Використання атрибута пакування `__attribute__((packed))` або `[[gnu::packed]]` є критично обов'язковим. Без нього компілятор C/C++ автоматично вирівняє 16-бітні поля `s_magic` та `s_state` по 32-бітній або 64-бітній межі, що спотворить зміщення і змусить програму зчитувати сміття замість магічних чисел.
3. **Позиційне читання через `pread()`:** На відміну від комбінації `lseek()` + `read()`, системний виклик `pread()` виконує позиціонування та зчитування атомарно, що дозволяє безпечно виконувати паралельний аналіз різних зміщень одного пристрою з кількох потоків.

## Інженерні пастки та крайові випадки блокового рівня

Під час практичного використання інструментів низькорівневого аналізу носіїв інженер стикається з низкою неочевидних крайових випадків:

1. **Конфлікт `O_EXCL` між ядром та утилітами діагностики:** Якщо блоковий пристрій уже змонтовано або захоплено `device-mapper`, виклик `open(path, O_EXCL)` негайно завершується з помилкою `EBUSY`. Для читання діагностичних секторів утиліта повинна безпечно відкочуватися до звичайного відкриття `O_RDONLY` без прапорця виключності.
2. **Зсув першого блоку при розмірі 1 КіБ:** У файлових системах Ext4 з розміром блоку 1024 байти перший блок даних (`s_first_data_block`) має номер `1`, а не `0` (оскільки блок 0 зайнятий завантажувальною областю MBR). Через це всі номери резервних суперблоків зсуваються рівно на `+1` (наприклад, блок `32769` замість `32768`). Якщо не врахувати цей зсув, утиліта відновлення прочитає дескриптори груп замість суперблоку і завершиться помилкою `e2fsck: Bad magic number in super-block`.
3. **Кешування блокового пристрою в Page Cache:** Якщо диск було змінено іншою утилітою без скидання кешу ядра, виклик `pread()` може повернути застарілі сторінки зі сторінкового кешу блокового пристрою. Для гарантованого читання з фізичного носія утиліта може відкривати дескриптор із прапорцем прямого вводу-виводу `O_DIRECT` з обов'язковим вирівнюванням буфера пам'яті по межі 4096 байтів (`posix_memalign`).
4. **Невідповідність розміру фізичного сектора (512e проти 4Kn):** Сучасні накопичувачі Advanced Format (4Kn) оперують виключно 4-кілобайтними фізичними секторами. Будь-яка спроба виконати пряме позиціонування `pread()` за зміщенням, не кратним 4096 байтам, на диску з `O_DIRECT` поверне системну помилку `EINVAL`.
5. **Ізоляція просторів імен монтування (*Mount Namespaces*):** Якщо процес працює всередині контейнера Docker або Kubernetes, виклик `fuser` або аналіз `/proc/mounts` покаже лише локальні точки монтування контейнера. Для глобальної діагностики стану хоста необхідно звертатися до простору імен ініціалізації через команду `nsenter -t 1 -m`.
6. **Завислі loop-пристрої після аварійного відключення образів:** Якщо файл віртуального диска було змонтовано через `/dev/loopX`, а процес віртуалізації впав, ядро зберігає активне відображення в таблиці `/dev/loop-control`. Спроба безпосередньо змінити або перемонтувати базовий файл поверне помилку `ETXTBSY` або `EBUSY`. Для діагностики таких випадків використовують команду `losetup -a` та звільнення через `losetup -d /dev/loopX`.
