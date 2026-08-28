#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int fd;
    uint8_t *mapped_bits;
    size_t file_size;
} bloom_mmap_t;

bloom_mmap_t *bloom_mmap_init(const char *filepath, size_t expected_size) {
    int fd = open(filepath, O_RDWR | O_CREAT, 0644);
    if (fd < 0) return NULL;
    
    /* Встановлення розміру файлу */
    ftruncate(fd, expected_size);
    
    uint8_t *bits = (uint8_t *)mmap(NULL, expected_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (bits == MAP_FAILED) {
        close(fd);
        return NULL;
    }

    bloom_mmap_t *res = (bloom_mmap_t *)malloc(sizeof(bloom_mmap_t));
    res->fd = fd;
    res->mapped_bits = bits;
    res->file_size = expected_size;
    return res;
}
