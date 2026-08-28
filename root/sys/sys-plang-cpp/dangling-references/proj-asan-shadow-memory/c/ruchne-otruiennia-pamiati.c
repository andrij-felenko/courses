#include <stdio.h>
#include <stdlib.h>
#include <sanitizer/asan_interface.h>

typedef struct {
    char buffer[1024];
    size_t offset;
} SimpleArena;

void arena_init(SimpleArena* a) {
    a->offset = 0;
    // Спочатку вся пам'ять арени отруєна
    ASAN_POISON_MEMORY_REGION(a->buffer, sizeof(a->buffer));
}

void* arena_alloc(SimpleArena* a, size_t size) {
    if (a->offset + size > sizeof(a->buffer)) return NULL;
    void* ptr = &a->buffer[a->offset];
    a->offset += size;
    // Відкриваємо доступ лише до виділеного діапазону
    ASAN_UNPOISON_MEMORY_REGION(ptr, size);
    return ptr;
}

void arena_reset(SimpleArena* a) {
    a->offset = 0;
    // Знову отруюємо всю пам'ять арени при скиданні
    ASAN_POISON_MEMORY_REGION(a->buffer, sizeof(a->buffer));
}

int main(void) {
    SimpleArena arena;
    arena_init(&arena);

    int* val = (int*)arena_alloc(&arena, sizeof(int));
    *val = 100;

    arena_reset(&arena); // Логічне звільнення всієї арени

    // Спроба звернення після reset викличе миттєву помилку ASan!
    printf("Значення: %d\n", *val);

    return 0;
}
