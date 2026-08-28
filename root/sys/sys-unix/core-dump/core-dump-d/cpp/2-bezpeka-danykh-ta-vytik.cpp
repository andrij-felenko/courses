#include <sys/mman.h>
#include <iostream>
#include <vector>

void protect_sensitive_memory() {
    size_t size = 4096; // 1 сторінка пам'яті
    void* secret_buffer = mmap(nullptr, size, PROT_READ | PROT_WRITE, 
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    
    if (secret_buffer != MAP_FAILED) {
        // Вказуємо ядру НЕ включати цю область у core dump
        madvise(secret_buffer, size, MADV_DONTDUMP);
        
        // Записуємо чутливі дані (наприклад, приватний ключ)
        // ...
        
        munmap(secret_buffer, size);
    }
}
