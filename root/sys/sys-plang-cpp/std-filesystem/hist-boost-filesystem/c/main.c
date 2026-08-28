// POSIX C: Отримання розміру файлу та часу модифікації
#include <sys/stat.h>
#include <stdio.h>

long long get_posix_file_size(const char* path) {
    struct stat st;
    if (stat(path, &st) == 0) {
        return (long long)st.st_size;
    }
    return -1;
}
