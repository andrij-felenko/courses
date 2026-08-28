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
