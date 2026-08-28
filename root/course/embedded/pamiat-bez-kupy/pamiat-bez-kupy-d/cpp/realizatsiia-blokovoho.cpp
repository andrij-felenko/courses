#include <cstdint>
#include <cstddef>
#include <memory>
#include <new>
#include <span>
#include <concepts>
#include <algorithm>

/* --- C++20 ТИПОБЕЗПЕЧНИЙ БЛОКОВИЙ ПУЛ З RAII --- */

template <typename T, std::size_t N>
class FixedPool {
public:
    static_assert(sizeof(T) >= sizeof(void*), "Розмір типу повинен вміщувати вказівник");
    static_assert(alignof(T) >= alignof(void*), "Вирівнювання типу повинно відповідати покажчику");

    FixedPool() noexcept {
        reset();
    }

    FixedPool(const FixedPool&) = delete;
    FixedPool& operator=(const FixedPool&) = delete;

    /* Виділення сирої пам'яті та виклик конструктора на місці (Placement new) */
    template <typename... Args>
    [[nodiscard]] T* construct(Args&&... args) noexcept {
        void* mem = allocate_raw();
        if (!mem) {
            return nullptr;
        }
        return ::new (mem) T(std::forward<Args>(args)...);
    }

    /* Виклик деструктора та повернення блоку в пул */
    void destroy(T* ptr) noexcept {
        if (!ptr) return;
        ptr->~T();
        deallocate_raw(ptr);
    }

    /* Розумний вказівник RAII, який автоматично повертає об'єкт у пул */
    struct Deleter {
        FixedPool* pool;
        void operator()(T* ptr) const noexcept {
            if (pool) pool->destroy(ptr);
        }
    };
    using UniquePtr = std::unique_ptr<T, Deleter>;

    template <typename... Args>
    [[nodiscard]] UniquePtr make_unique(Args&&... args) noexcept {
        T* obj = construct(std::forward<Args>(args)...);
        return UniquePtr(obj, Deleter{this});
    }

    [[nodiscard]] std::size_t available() const noexcept { return free_count_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return N; }
    [[nodiscard]] std::size_t min_available() const noexcept { return min_free_count_; }

private:
    struct Node {
        Node* next;
    };

    alignas(T) std::byte storage_[N * sizeof(T)];
    Node* free_list_{nullptr};
    std::size_t free_count_{N};
    std::size_t min_free_count_{N};

    void reset() noexcept {
        free_list_ = nullptr;
        free_count_ = N;
        min_free_count_ = N;
        for (std::size_t i = 0; i < N; ++i) {
            auto* node = reinterpret_cast<Node*>(&storage_[i * sizeof(T)]);
            node->next = free_list_;
            free_list_ = node;
        }
    }

    void* allocate_raw() noexcept {
        if (!free_list_) return nullptr;
        Node* node = free_list_;
        free_list_ = node->next;
        --free_count_;
        min_free_count_ = std::min(min_free_count_, free_count_);
        return static_cast<void*>(node);
    }

    void deallocate_raw(void* ptr) noexcept {
        auto* p = static_cast<std::byte*>(ptr);
        auto* start = &storage_[0];
        auto* end = &storage_[N * sizeof(T)];

        if (p < start || p >= end) return;
        if ((static_cast<std::size_t>(p - start) % sizeof(T)) != 0) return;

        auto* node = reinterpret_cast<Node*>(ptr);
        node->next = free_list_;
        free_list_ = node;
        ++free_count_;
    }
};

/* --- C++20 ЛІНІЙНА АРЕНА З АВТОМАТИЧНИМ ОБЛАСТНИМ КОНТРОЛЕМ (RAII Scope) --- */

template <std::size_t Capacity>
class MemoryArena {
public:
    MemoryArena() noexcept = default;
    MemoryArena(const MemoryArena&) = delete;
    MemoryArena& operator=(const MemoryArena&) = delete;

    /* Виділення пам'яті під один об'єкт або масив */
    template <typename T, typename... Args>
    [[nodiscard]] T* create(Args&&... args) noexcept {
        void* mem = alloc_aligned(sizeof(T), alignof(T));
        if (!mem) return nullptr;
        return ::new (mem) T(std::forward<Args>(args)...);
    }

    template <typename T>
    [[nodiscard]] std::span<T> create_span(std::size_t count) noexcept {
        void* mem = alloc_aligned(sizeof(T) * count, alignof(T));
        if (!mem) return {};
        T* array = reinterpret_cast<T*>(mem);
        for (std::size_t i = 0; i < count; ++i) {
            ::new (static_cast<void*>(&array[i])) T();
        }
        return std::span<T>(array, count);
    }

    /* RAII-охорона області: автоматично відкочує арену до попереднього стану при виході зі скоупу */
    class Scope {
    public:
        explicit Scope(MemoryArena& arena) noexcept
            : arena_(arena), saved_offset_(arena.offset_) {}
        ~Scope() noexcept {
            arena_.offset_ = saved_offset_;
        }
        Scope(const Scope&) = delete;
        Scope& operator=(const Scope&) = delete;
    private:
        MemoryArena& arena_;
        std::size_t saved_offset_;
    };

    [[nodiscard]] Scope make_scope() noexcept {
        return Scope(*this);
    }

    void reset() noexcept { offset_ = 0; }
    [[nodiscard]] std::size_t used_bytes() const noexcept { return offset_; }
    [[nodiscard]] std::size_t peak_bytes() const noexcept { return peak_offset_; }
    [[nodiscard]] std::size_t remaining_bytes() const noexcept { return Capacity - offset_; }

private:
    alignas(std::max_align_t) std::byte buffer_[Capacity];
    std::size_t offset_{0};
    std::size_t peak_offset_{0};

    void* alloc_aligned(std::size_t size, std::size_t alignment) noexcept {
        auto current = reinterpret_cast<std::uintptr_t>(&buffer_[offset_]);
        std::uintptr_t aligned = (current + (alignment - 1)) & ~(alignment - 1);
        std::size_t padding = aligned - current;

        if (offset_ + padding + size > Capacity) {
            return nullptr;
        }

        offset_ += padding + size;
        peak_offset_ = std::max(peak_offset_, offset_);
        return reinterpret_cast<void*>(aligned);
    }
};
