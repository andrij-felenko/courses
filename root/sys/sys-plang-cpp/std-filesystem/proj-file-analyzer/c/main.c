// POSIX C: Рекурсивний розбір каталогу
#include <sys/stat.h>
#include <dirent.h>
#include <stdio.h>
#include <string.h>

void scan_posix_dir(const char* dir_path) {
    DIR* dir = opendir(dir_path);
    if (!dir) return; // Ручне керування ресурсом!

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
            continue;

        char full_path[1024];
        snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, entry->d_name);

        struct stat st;
        if (lstat(full_path, &st) == 0) {
            if (S_ISDIR(st.st_mode)) {
                scan_posix_dir(full_path); // Небезпека переповнення стеку
            } else if (S_ISREG(st.st_mode)) {
                printf("File: %s, Size: %lld\n", full_path, (long long)st.st_size);
            }
        }
    }
    closedir(dir); // Обов'язкове звільнення дескриптора!
}
