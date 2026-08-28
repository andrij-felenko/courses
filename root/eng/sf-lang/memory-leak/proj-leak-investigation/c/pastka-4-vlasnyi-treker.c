#include <stdio.h>
#include <stdlib.h>

typedef struct AllocRecord {
    void *ptr;
    size_t size;
    const char *file;
    int line;
} AllocRecord;

#define MAX_TRACKED_ALLOCS 64
static AllocRecord g_alloc_table[MAX_TRACKED_ALLOCS];
static size_t g_alloc_count = 0;

void *debug_malloc(size_t size, const char *file, int line) {
    void *ptr = malloc(size);
    if (ptr && g_alloc_count < MAX_TRACKED_ALLOCS) {
        g_alloc_table[g_alloc_count++] = (AllocRecord){ ptr, size, file, line };
    }
    return ptr;
}

void debug_free(void *ptr) {
    if (!ptr) return;
    for (size_t i = 0; i < g_alloc_count; ++i) {
        if (g_alloc_table[i].ptr == ptr) {
            g_alloc_table[i] = g_alloc_table[--g_alloc_count];
            break;
        }
    }
    free(ptr);
}

void check_leaks_on_exit(void) {
    if (g_alloc_count == 0) {
        printf("[Аудит] Витоків пам'яті не виявлено.\n");
        return;
    }
    printf("[Аудит ПОМИЛКА] Знайдено %zu незвільнених виділень:\n", g_alloc_count);
    for (size_t i = 0; i < g_alloc_count; ++i) {
        printf("  - %zu байтів за адресою %p у %s:%d\n",
               g_alloc_table[i].size, g_alloc_table[i].ptr,
               g_alloc_table[i].file, g_alloc_table[i].line);
    }
}

#define malloc(s) debug_malloc(s, __FILE__, __LINE__)
#define free(p) debug_free(p)

int main(void) {
    int *p1 = (int *)malloc(64);
    int *p2 = (int *)malloc(128);
    free(p1);
    /* p2 навмисно не звільняється */
    check_leaks_on_exit();
    free(p2);
    return 0;
}
