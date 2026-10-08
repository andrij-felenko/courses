#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define MIN_SAFE_HEAP_BYTES 8192

bool check_system_memory(int free_heap_bytes) {
    if (free_heap_bytes < MIN_SAFE_HEAP_BYTES) {
        // Повідомляємо про недостатність пам'яті для створення сокета
        printf("Помилка: вільна пам'ять (%d B) нижче порогу (%d B)\n", 
               free_heap_bytes, MIN_SAFE_HEAP_BYTES);
        return false;
    }
    return true;
}
