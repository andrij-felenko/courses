#define _GNU_SOURCE
#include <iostream>
#include <iomanip>
#include <string_view>
#include <system_error>
#include <ctime>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>

namespace {

void print_ts(std::string_view label, long long sec, unsigned nsec)
{
    std::time_t t = static_cast<std::time_t>(sec);
    std::tm tm{};
    ::localtime_r(&t, &tm);
    char buf[64];
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &tm);
    std::cout << std::left << std::setw(12) << label << " " << buf << "." 
              << std::setfill('0') << std::setw(9) << nsec << std::setfill(' ') << "\n";
}

} // namespace

int main(int argc, char **argv)
{
    if (argc != 2) {
        std::cerr << "вжиток: " << argv[0] << " ШЛЯХ\n";
        return 2;
    }

    struct statx sx{};
    constexpr unsigned mask = STATX_BASIC_STATS | STATX_BTIME | STATX_MNT_ID;

    if (::statx(AT_FDCWD, argv[1], AT_SYMLINK_NOFOLLOW, mask, &sx) != 0) {
        if (errno != ENOSYS) {
            std::cerr << "statx(" << argv[1] << "): " << std::system_category().message(errno) << "\n";
            return 1;
        }
        struct stat st{};
        if (::fstatat(AT_FDCWD, argv[1], &st, AT_SYMLINK_NOFOLLOW) != 0) {
            std::cerr << "fstatat(" << argv[1] << "): " << std::system_category().message(errno) << "\n";
            return 1;
        }
        std::cout << std::left << std::setw(12) << "пристрій" << " " << major(st.st_dev) << ":" << minor(st.st_dev) << "\n";
        std::cout << std::left << std::setw(12) << "inode" << " " << st.st_ino << "\n";
        std::cout << std::left << std::setw(12) << "імен" << " " << st.st_nlink << "\n";
        std::cout << std::left << std::setw(12) << "розмір" << " " << st.st_size << "\n";
        std::cout << std::left << std::setw(12) << "зайнято" << " " << (st.st_blocks * 512) << "\n";
        return 0;
    }

    std::cout << std::left << std::setw(12) << "пристрій" << " " << sx.stx_dev_major << ":" << sx.stx_dev_minor << "\n";

    if (sx.stx_mask & STATX_INO)
        std::cout << std::left << std::setw(12) << "inode" << " " << sx.stx_ino << "\n";
    if (sx.stx_mask & STATX_NLINK)
        std::cout << std::left << std::setw(12) << "імен" << " " << sx.stx_nlink << "\n";
    if (sx.stx_mask & STATX_TYPE)
        std::cout << std::left << std::setw(12) << "тип" << " "
                  << (S_ISREG(sx.stx_mode) ? "звичайний файл" :
                      S_ISDIR(sx.stx_mode) ? "каталог" :
                      S_ISLNK(sx.stx_mode) ? "символьне посилання" : "інший") << "\n";
    if (sx.stx_mask & STATX_MODE)
        std::cout << std::left << std::setw(12) << "права" << " " << std::oct << (sx.stx_mode & 07777) << std::dec << "\n";
    if (sx.stx_mask & STATX_SIZE)
        std::cout << std::left << std::setw(12) << "розмір" << " " << sx.stx_size << "\n";
    if (sx.stx_mask & STATX_BLOCKS)
        std::cout << std::left << std::setw(12) << "зайнято" << " " << (sx.stx_blocks * 512) << " (" << sx.stx_blocks << " × 512)\n";
    if (sx.stx_mask & STATX_MTIME)
        print_ts("змінено", sx.stx_mtime.tv_sec, sx.stx_mtime.tv_nsec);

    if (sx.stx_mask & STATX_BTIME)
        print_ts("створено", sx.stx_btime.tv_sec, sx.stx_btime.tv_nsec);
    else
        std::cout << std::left << std::setw(12) << "створено" << " ця файлова система часу створення не тримає\n";

    if (sx.stx_mask & STATX_MNT_ID)
        std::cout << std::left << std::setw(12) << "монтування" << " " << sx.stx_mnt_id << "\n";

    return 0;
}
