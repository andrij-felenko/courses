#include <cstddef>
#include <new>

// Приклад: низькорівневий системний алокатор пам'яті
class SystemMemoryArena {
public:
    [[nodiscard]] void* allocate_aligned(std::size_t bytes, std::size_t alignment) {
        // Документоване придушення для лінтера Clang-Tidy
        // NOLINTNEXTLINE(cppcoreguidelines-owning-memory): Арена керує пулом самостійно
        void* raw_memory = ::operator new(bytes, std::align_val_t{alignment});
        return raw_memory;
    }

    void deallocate(void* ptr) noexcept {
        // MSVC C++ Core Check анотація
        [[gsl::suppress("cppcoreguidelines-owning-memory", 
          justification = "Звільнення сирого блоку пам'яті внутрішньої арени")]]
        ::operator delete(ptr);
    }
};
