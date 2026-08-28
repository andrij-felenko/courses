#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <limits.h>
#include <assert.h>

static void trigger_null_dereference(void) {
    volatile int *ptr = NULL;
    *ptr = 42;
}

static void trigger_rodata_write(void) {
    const char *ro_str = "Read-only literal string";
    char *writable = (char *)ro_str;
    writable[0] = 'W';
}

static void trigger_mmap_truncate(void) {
    char filename[] = "/tmp/crash_mmap_XXXXXX";
    int fd = mkstemp(filename);
    if (fd < 0) return;

    size_t page_size = 4096;
    if (ftruncate(fd, page_size) != 0) {
        close(fd);
        unlink(filename);
        return;
    }

    char *mapped = mmap(NULL, page_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (mapped == MAP_FAILED) {
        close(fd);
        unlink(filename);
        return;
    }

    mapped[0] = 'A';
    /* Усікаємо файл до 0 байтів, залишаючи сторінку у VMA */
    if (ftruncate(fd, 0) != 0) {
        /* Ігноруємо помилку усічення */
    }

    /* Читання сторінки викликає Page Fault, ядро не знаходить блоку -> SIGBUS */
    volatile char val = mapped[128];
    (void)val;

    munmap(mapped, page_size);
    close(fd);
    unlink(filename);
}

static void trigger_unaligned_access(void) {
#if defined(__x86_64__) || defined(_M_X64)
    /* Вирівняне читання SSE інструкцією movdqa на невирівняну адресу */
    char buffer[64];
    char *unaligned_ptr = buffer + 1; /* Зсув на 1 байт порушує кратність 16 */
    __asm__ volatile (
        "movdqa (%0), %%xmm0"
        :
        : "r" (unaligned_ptr)
        : "xmm0"
    );
#else
    volatile char buffer[16];
    volatile long *ptr = (volatile long *)(buffer + 1);
    *ptr = 0xDEADBEEF;
#endif
}

static void trigger_abort_assert(void) {
    int invariant = 0;
    assert(invariant == 1);
}

static void trigger_divide_by_zero(int mode) {
    if (mode == 0) {
        volatile int zero = 0;
        volatile int result = 100 / zero;
        (void)result;
    } else {
        volatile int min_val = INT_MIN;
        volatile int divisor = -1;
        volatile int result = min_val / divisor;
        (void)result;
    }
}

static void trigger_use_after_free(void) {
    char *chunk = (char *)malloc(128);
    if (!chunk) return;
    strcpy(chunk, "Active memory chunk");
    free(chunk);
    /* Запис у звільнений блок пам'яті */
    chunk[0] = 'X';
    printf("Read after free: %s\n", chunk);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <1-7>\n", argv[0]);
        fprintf(stderr, " 1: SIGSEGV (NULL dereference)\n");
        fprintf(stderr, " 2: SIGSEGV (Write to .rodata)\n");
        fprintf(stderr, " 3: SIGBUS  (mmap truncate)\n");
        fprintf(stderr, " 4: SIGBUS  (unaligned SSE load)\n");
        fprintf(stderr, " 5: SIGABRT (assert failure)\n");
        fprintf(stderr, " 6: SIGFPE  (divide by zero / overflow)\n");
        fprintf(stderr, " 7: Use-After-Free\n");
        return 1;
    }

    int choice = atoi(argv[1]);
    switch (choice) {
        case 1: trigger_null_dereference(); break;
        case 2: trigger_rodata_write(); break;
        case 3: trigger_mmap_truncate(); break;
        case 4: trigger_unaligned_access(); break;
        case 5: trigger_abort_assert(); break;
        case 6: trigger_divide_by_zero(0); break;
        case 7: trigger_use_after_free(); break;
        default:
            fprintf(stderr, "Невідомий сценарій: %d\n", choice);
            return 1;
    }
    return 0;
}
