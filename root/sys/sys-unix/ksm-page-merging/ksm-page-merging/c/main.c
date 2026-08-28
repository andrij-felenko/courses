#include <sys/mman.h>
#include <stdio.h>
#include <unistd.h>

int main(void) {
    size_t size = 100 * 1024 * 1024; // 100 МіБ

    void *addr = mmap(NULL, size, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) return 1;

    // Дозволяємо KSM сканувати та зливати цю ділянку
    if (madvise(addr, size, MADV_MERGEABLE) == 0) {
        printf("KSM дозволено для ділянки %p\n", addr);
    }
    return 0;
}
