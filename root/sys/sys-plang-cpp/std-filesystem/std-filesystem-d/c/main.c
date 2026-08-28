// POSIX C: Перевірка існування файлу та створення каталогу
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

int ensure_directory_posix(const char* path) {
    struct stat st;
    if (stat(path, &st) != 0) {
        return mkdir(path, 0755); // POSIX вимагає маску прав
    }
    return S_ISDIR(st.st_mode) ? 0 : -1;
}
