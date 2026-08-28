// У C++ ручне керування пам'яттю для шляхів та списків імен замінюють стандартом C++17/20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <unordered_map>
#include <memory>
#include <system_error>
#include <dirent.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

constexpr uintmax_t BLOCK_UNIT = 512;
constexpr size_t SPARSE_TOP = 5;

inline int fstatat_retry(int dfd, const char *name, struct stat *st, int flags) {
    int r;
    do { r = ::fstatat(dfd, name, st, flags); } while (r != 0 && errno == EINTR);
    return r;
}

inline int openat_retry(int dfd, const char *name, int flags) {
    int fd;
    do { fd = ::openat(dfd, name, flags); } while (fd < 0 && errno == EINTR);
    return fd;
}

// Замість ручних struct pathbuf та struct namelist у C++ використовують std::string та std::vector<std::string>:
// Додавання елементів до шляху стає розширенням рядка std::string, а список імен у каталозі сортується через std::sort.
