#include <new>
#include <cstdlib>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <utility>

class MemoryTracker {
public:
    struct Stats {
        std::size_t total_allocated_bytes = 0;
        std::size_t total_freed_bytes = 0;
        std::size_t current_active_bytes = 0;
        std::size_t peak_bytes = 0;
        std::size_t total_allocations_count = 0;
        std::size_t total_deallocations_count = 0;
        std::size_t mismatch_errors_count = 0;
        std::size_t corruption_errors_count = 0;
    };

    struct Header {
        std::size_t requested_size;
        std::size_t alignment;
        uint32_t magic_signature;
        bool is_array;
    };

    static constexpr uint32_t MAGIC_HEADER = 0xDEADBEEF;
    static constexpr uint64_t MAGIC_CANARY = 0xCAFEBABEDEADBEEFULL;
    static constexpr uint8_t PATTERN_UNINITIALIZED = 0xCC; // Маркер свіжої пам'яті
    static constexpr uint8_t PATTERN_FREED = 0xDD;         // Маркер мертвої пам'яті (Dead)

    static void* allocate(std::size_t size, std::size_t alignment, bool is_array) {
        if (size == 0) size = 1;

        if (alignment < alignof(std::max_align_t)) {
            alignment = alignof(std::max_align_t);
        }

        std::size_t header_size = sizeof(Header);
        if (header_size % alignment != 0) {
            header_size += alignment - (header_size % alignment);
        }

        // Виділяємо місце під заголовок + дані + хвостову канарку
        std::size_t total_size = header_size + size + sizeof(uint64_t);

        void* raw_ptr = nullptr;
#if defined(_MSC_VER)
        raw_ptr = _aligned_malloc(total_size, alignment);
#else
        if (posix_memalign(&raw_ptr, alignment, total_size) != 0) {
            raw_ptr = nullptr;
        }
#endif

        if (!raw_ptr) {
            if (auto handler = std::get_new_handler()) {
                handler();
                return allocate(size, alignment, is_array);
            }
            throw std::bad_alloc();
        }

        char* user_ptr = static_cast<char*>(raw_ptr) + header_size;
        Header* header = reinterpret_cast<Header*>(user_ptr - sizeof(Header));
        header->requested_size = size;
        header->alignment = alignment;
        header->magic_signature = MAGIC_HEADER;
        header->is_array = is_array;

        // Дебаг-заповнення пам'яті для виявлення читання неініціалізованих полів
        std::memset(user_ptr, PATTERN_UNINITIALIZED, size);

        // Запис хвостової канарки безпосередньо після корисного навантаження
        uint64_t* tail_canary = reinterpret_cast<uint64_t*>(user_ptr + size);
        *tail_canary = MAGIC_CANARY;

        total_allocations_.fetch_add(1, std::memory_order_relaxed);
        total_allocated_bytes_.fetch_add(size, std::memory_order_relaxed);
        
        std::size_t current = current_active_bytes_.fetch_add(size, std::memory_order_relaxed) + size;
        
        std::size_t prev_peak = peak_bytes_.load(std::memory_order_relaxed);
        while (current > prev_peak && 
               !peak_bytes_.compare_exchange_weak(prev_peak, current, std::memory_order_relaxed)) {
        }

        return user_ptr;
    }

    static void deallocate(void* user_ptr, std::size_t expected_size, std::size_t expected_align, bool is_array) noexcept {
        if (!user_ptr) return;

        Header* header = reinterpret_cast<Header*>(static_cast<char*>(user_ptr) - sizeof(Header));
        
        if (header->magic_signature != MAGIC_HEADER) {
            std::fprintf(stderr, "[ПОМИЛКА ТРЕКЕРА] Спроба звільнити невідомий або вже звільнений покажчик: %p\n", user_ptr);
            mismatch_errors_.fetch_add(1, std::memory_order_relaxed);
            return;
        }

        // Перевірка цілісності хвостової канарки
        uint64_t* tail_canary = reinterpret_cast<uint64_t*>(static_cast<char*>(user_ptr) + header->requested_size);
        if (*tail_canary != MAGIC_CANARY) {
            std::fprintf(stderr, "[ПОМИЛКА ТРЕКЕРА] Виявлено пошкодження пам'яті (Buffer Overrun) за адресою %p!\n", user_ptr);
            corruption_errors_.fetch_add(1, std::memory_order_relaxed);
        }

        if (header->is_array != is_array) {
            std::fprintf(stderr, "[ПОМИЛКА ТРЕКЕРА] Невідповідність операторів: виділено як %s, але звільнено як %s за адресою %p!\n",
                         header->is_array ? "new[]" : "new", is_array ? "delete[]" : "delete", user_ptr);
            mismatch_errors_.fetch_add(1, std::memory_order_relaxed);
        }

        if (expected_size != 0 && expected_size != header->requested_size) {
            std::fprintf(stderr, "[ПОМИЛКА ТРЕКЕРА] Sized delete не відповідає дійсності: очікувалось %zu B, виділено %zu B!\n",
                         expected_size, header->requested_size);
            mismatch_errors_.fetch_add(1, std::memory_order_relaxed);
        }

        std::size_t freed_size = header->requested_size;
        std::size_t align = header->alignment;
        std::size_t header_size = sizeof(Header);
        if (header_size % align != 0) {
            header_size += align - (header_size % align);
        }

        void* raw_ptr = static_cast<char*>(user_ptr) - header_size;

        // Знищення сигнатури
        header->magic_signature = 0x00000000;

        // Отруєння пам'яті перед звільненням (Use-After-Free Poisoning)
        std::memset(user_ptr, PATTERN_FREED, freed_size);

        total_deallocations_.fetch_add(1, std::memory_order_relaxed);
        total_freed_bytes_.fetch_add(freed_size, std::memory_order_relaxed);
        current_active_bytes_.fetch_sub(freed_size, std::memory_order_relaxed);

#if defined(_MSC_VER)
        _aligned_free(raw_ptr);
#else
        std::free(raw_ptr);
#endif
    }

    static Stats get_stats() {
        return Stats{
            total_allocated_bytes_.load(std::memory_order_relaxed),
            total_freed_bytes_.load(std::memory_order_relaxed),
            current_active_bytes_.load(std::memory_order_relaxed),
            peak_bytes_.load(std::memory_order_relaxed),
            total_allocations_count_.load(std::memory_order_relaxed),
            total_deallocations_count_.load(std::memory_order_relaxed),
            mismatch_errors_.load(std::memory_order_relaxed),
            corruption_errors_.load(std::memory_order_relaxed)
        };
    }

    static void print_report() {
        Stats s = get_stats();
        std::printf("\n================ ЗВІТ АУДИТУ ПАМ'ЯТІ ================\n");
        std::printf("  Усього операцій виділення: %zu\n", s.total_allocations_count);
        std::printf("  Усього операцій звільнення: %zu\n", s.total_deallocations_count);
        std::printf("  Сумарно виділено байтів:    %zu B (%.2f KB)\n", s.total_allocated_bytes, s.total_allocated_bytes / 1024.0);
        std::printf("  Сумарно звільнено байтів:   %zu B (%.2f KB)\n", s.total_freed_bytes, s.total_freed_bytes / 1024.0);
        std::printf("  Пікове споживання:          %zu B (%.2f KB)\n", s.peak_bytes, s.peak_bytes / 1024.0);
        std::printf("  Активний залишок (витоки):  %zu B\n", s.current_active_bytes);
        std::printf("  Невідповідностей операторів: %zu\n", s.mismatch_errors_count);
        std::printf("  Виявлених пошкоджень (Overrun): %zu\n", s.corruption_errors_count);
        if (s.current_active_bytes > 0 || s.mismatch_errors_count > 0 || s.corruption_errors_count > 0) {
            std::printf("  [УВАГА] Виявлено дефекти керування пам'яттю!\n");
        } else {
            std::printf("  [УСПІХ] Усі виділені ресурси звільнено повністю (0 витоків, 0 дефектів).\n");
        }
        std::printf("=====================================================\n\n");
    }

private:
    static inline std::atomic<std::size_t> total_allocated_bytes_{0};
    static inline std::atomic<std::size_t> total_freed_bytes_{0};
    static inline std::atomic<std::size_t> current_active_bytes_{0};
    static inline std::atomic<std::size_t> peak_bytes_{0};
    static inline std::atomic<std::size_t> total_allocations_count_{0};
    static inline std::atomic<std::size_t> total_deallocations_count_{0};
    static inline std::atomic<std::size_t> mismatch_errors_{0};
    static inline std::atomic<std::size_t> corruption_errors_{0};
};

// ── Глобальні перевантаження для перехоплення ──────────────────────────────

void* operator new(std::size_t size) {
    return MemoryTracker::allocate(size, alignof(std::max_align_t), false);
}

void* operator new[](std::size_t size) {
    return MemoryTracker::allocate(size, alignof(std::max_align_t), true);
}

void operator delete(void* ptr) noexcept {
    MemoryTracker::deallocate(ptr, 0, alignof(std::max_align_t), false);
}

void operator delete[](void* ptr) noexcept {
    MemoryTracker::deallocate(ptr, 0, alignof(std::max_align_t), true);
}

// C++14 Sized delete
void operator delete(void* ptr, std::size_t size) noexcept {
    MemoryTracker::deallocate(ptr, size, alignof(std::max_align_t), false);
}

void operator delete[](void* ptr, std::size_t size) noexcept {
    MemoryTracker::deallocate(ptr, size, alignof(std::max_align_t), true);
}

// C++17 Aligned new / delete
void* operator new(std::size_t size, std::align_val_t al) {
    return MemoryTracker::allocate(size, static_cast<std::size_t>(al), false);
}

void* operator new[](std::size_t size, std::align_val_t al) {
    return MemoryTracker::allocate(size, static_cast<std::size_t>(al), true);
}

void operator delete(void* ptr, std::align_val_t al) noexcept {
    MemoryTracker::deallocate(ptr, 0, static_cast<std::size_t>(al), false);
}

void operator delete[](void* ptr, std::align_val_t al) noexcept {
    MemoryTracker::deallocate(ptr, 0, static_cast<std::size_t>(al), true);
}

void operator delete(void* ptr, std::size_t size, std::align_val_t al) noexcept {
    MemoryTracker::deallocate(ptr, size, static_cast<std::size_t>(al), false);
}

void operator delete[](void* ptr, std::size_t size, std::align_val_t al) noexcept {
    MemoryTracker::deallocate(ptr, size, static_cast<std::size_t>(al), true);
}
