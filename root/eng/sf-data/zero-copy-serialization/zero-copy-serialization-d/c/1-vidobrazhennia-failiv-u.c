#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>

const uint8_t *map_binary_file(const char *path, size_t *out_size) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return NULL;

    struct stat st;
    if (fstat(fd, &st) < 0) {
        close(fd);
        return NULL;
    }

    void *data = mmap(NULL, st.st_size, PROT_READ, MAP_SHARED, fd, 0);
    close(fd); /* Дескриптор можна закрити після mmap */

    if (data == MAP_FAILED) return NULL;
    *out_size = (size_t)st.st_size;
    return (const uint8_t *)data;
}
