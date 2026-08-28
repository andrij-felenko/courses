#define _GNU_SOURCE
#include <sys/mman.h>
#include <sys/prctl.h>
#include <string.h>
#include <unistd.h>

/* Безпечний розподіл та блокування конфіденційного буфера в RAM */
void* allocate_secure_buffer(size_t size) {
    /* Виділення пам'яті безпосередньо через анонімний mmap */
    void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE, 
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (ptr == MAP_FAILED) return NULL;

    /* Блокування сторінки проти вивантаження в swap */
    if (mlock(ptr, size) != 0) {
        munmap(ptr, size);
        return NULL;
    }

    /* Заборона включення буфера в дамп пам'яті при аварійному завершенні */
    if (madvise(ptr, size, MADV_DONTDUMP) != 0) {
        munlock(ptr, size);
        munmap(ptr, size);
        return NULL;
    }

    /* Заборона трасування процесу через ptrace сторонніми процесами */
    prctl(PR_SET_DUMPABLE, 0);

    return ptr;
}

/* Гарантоване зачищення та звільнення пам'яті */
void free_secure_buffer(void *ptr, size_t size) {
    if (ptr == NULL || size == 0) return;

    /* Занулення з асемблерним бар'єром пам'яті проти Dead Store Elimination */
    volatile unsigned char *p = (volatile unsigned char *)ptr;
    for (size_t i = 0; i < size; ++i) {
        p[i] = 0;
    }
    __asm__ __volatile__("" : : "r"(ptr) : "memory");

    munlock(ptr, size);
    munmap(ptr, size);
}
