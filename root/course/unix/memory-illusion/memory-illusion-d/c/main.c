#include <sys/mman.h>
#include <stdio.h>

int main(void) {
    size_t size = 10ULL * 1024 * 1024 * 1024; // 10 ГіБ
    char *buf = mmap(NULL, size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf == MAP_FAILED) {
        perror("mmap");
        return 1;
    }
    // Фізичної пам'яті виділено: 0 байтів
    buf[0] = 'A'; // Тут виникає #PF: виділяється рівно 4 КіБ
    return 0;
}
