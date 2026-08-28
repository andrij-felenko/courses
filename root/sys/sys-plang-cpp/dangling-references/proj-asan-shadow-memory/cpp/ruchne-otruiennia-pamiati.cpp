#include <iostream>
#include <cstddef>
#include <vector>
#include <sanitizer/asan_interface.h>

template <size_t TotalBytes = 1024>
class CustomArena {
    alignas(std::max_align_t) std::byte storage_[TotalBytes];
    size_t offset_{0};

public:
    CustomArena() {
        // Позначаємо всю пам'ять як заблоковану
        ASAN_POISON_MEMORY_REGION(storage_, TotalBytes);
    }

    ~CustomArena() {
        // Очищаємо перед знищенням
        ASAN_UNPOISON_MEMORY_REGION(storage_, TotalBytes);
    }

    void* allocate(size_t bytes) {
        size_t aligned = (bytes + alignof(std::max_align_t) - 1) & ~(alignof(std::max_align_t) - 1);
        if (offset_ + aligned > TotalBytes) return nullptr;
        void* ptr = &storage_[offset_];
        offset_ += aligned;
        // Відкриваємо доступ лише для алокованого блоку
        ASAN_UNPOISON_MEMORY_REGION(ptr, bytes);
        return ptr;
    }

    void reset() {
        offset_ = 0;
        // При скиданні знову блокуємо весь масив
        ASAN_POISON_MEMORY_REGION(storage_, TotalBytes);
    }
};

int main() {
    CustomArena<512> arena;

    int* num = static_cast<int*>(arena.allocate(sizeof(int)));
    *num = 42;

    arena.reset(); // Скидання арени

    // Помилка: ASan перехопить Use-After-Free навіть у кастомній арені
    std::cout << "Число: " << *num << '\n';

    return 0;
}
