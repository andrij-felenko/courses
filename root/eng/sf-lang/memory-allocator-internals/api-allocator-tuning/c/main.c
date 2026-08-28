#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>

void print_allocator_state(const char* checkpoint_label) {
    struct mallinfo2 info = mallinfo2();
    printf("[%s]\n", checkpoint_label);
    printf("  Купа (arena):        %8zu КіБ\n", info.arena / 1024);
    printf("  Блоки mmap (hblkhd): %8zu КіБ\n", info.hblkhd / 1024);
    printf("  Зайнято (uordblks):  %8zu КіБ\n", info.uordblks / 1024);
    printf("  Резерв (fordblks):   %8zu КіБ\n", info.fordblks / 1024);
}

int main(void) {
    // 1. Обмежуємо максимальну кількість арен двома
    mallopt(M_ARENA_MAX, 2);

    print_allocator_state("Початковий стан");

    // 2. Інтенсивне виділення 1000 блоків по 16 КіБ (сумарно 16 МіБ)
    void* buffers[1000];
    for (int i = 0; i < 1000; i++) {
        buffers[i] = malloc(16 * 1024);
    }
    print_allocator_state("Після виділення 16 МіБ");

    // 3. Звільнення всіх блоків
    for (int i = 0; i < 1000; i++) {
        free(buffers[i]);
    }
    print_allocator_state("Після free() (пам'ять у внутрішньому резерві)");

    // 4. Примусовий тримінг пам'яті назад ядру операційної системи
    int trimmed = malloc_trim(0);
    printf("Результат malloc_trim: %s\n", trimmed ? "успішно" : "без змін");

    print_allocator_state("Після malloc_trim()");

    return 0;
}
