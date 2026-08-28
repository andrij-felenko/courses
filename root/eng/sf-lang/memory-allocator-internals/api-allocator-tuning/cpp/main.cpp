#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <malloc.h>

struct MemorySnapshot {
    size_t arena_kb{0};
    size_t mmap_kb{0};
    size_t in_use_kb{0};
    size_t free_cached_kb{0};

    [[nodiscard]] static MemorySnapshot capture() noexcept {
        const auto info = mallinfo2();
        return MemorySnapshot{
            .arena_kb = info.arena / 1024,
            .mmap_kb = info.hblkhd / 1024,
            .in_use_kb = info.uordblks / 1024,
            .free_cached_kb = info.fordblks / 1024
        };
    }
};

std::ostream& operator<<(std::ostream& os, const MemorySnapshot& s) {
    os << "  Купа (arena):        " << s.arena_kb << " КіБ\n"
       << "  Блоки mmap (hblkhd): " << s.mmap_kb << " КіБ\n"
       << "  Зайнято (in_use):    " << s.in_use_kb << " КіБ\n"
       << "  Резерв (free_cache): " << s.free_cached_kb << " КіБ";
    return os;
}

int main() {
    // 1. Конфігурація алокатора
    mallopt(M_ARENA_MAX, 2);

    std::cout << "[Початковий стан]\n" << MemorySnapshot::capture() << "\n\n";

    // 2. Блок виділення пам'яті з використанням RAII
    {
        std::vector<std::unique_ptr<char[]>> buffers;
        buffers.reserve(1000);
        for (size_t i = 0; i < 1000; ++i) {
            buffers.push_back(std::make_unique<char[]>(16 * 1024));
        }
        std::cout << "[Після виділення 16 МіБ]\n" << MemorySnapshot::capture() << "\n\n";
    }

    std::cout << "[Після знищення vector (пам'ять повернуто в списки)]\n"
              << MemorySnapshot::capture() << "\n\n";

    // 3. Примусове скидання сторінок ядру
    const int result = malloc_trim(0);
    std::cout << "Результат malloc_trim: " << (result ? "успішно" : "без змін") << "\n";
    std::cout << "[Після malloc_trim()]\n" << MemorySnapshot::capture() << "\n";

    return 0;
}
