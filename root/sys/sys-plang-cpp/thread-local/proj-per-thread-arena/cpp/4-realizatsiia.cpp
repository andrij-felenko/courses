#include <iostream>
#include <vector>
#include <memory>
#include <cstddef>
#include <cstdint>
#include <new>
#include <span>
#include <thread>

class ThreadLocalArena {
public:
    static constexpr std::size_t DefaultChunkSize = 64 * 1024; // 64 KB

    explicit ThreadLocalArena(std::size_t initial_capacity = DefaultChunkSize)
        : capacity_(initial_capacity), offset_(0) {
        buffer_ = static_cast<std::byte*>(::operator new(capacity_, std::align_val_t{64}));
    }

    ~ThreadLocalArena() noexcept {
        release_all();
    }

    // Заборона копіювання та переміщення між потоками
    ThreadLocalArena(const ThreadLocalArena&) = delete;
    ThreadLocalArena& operator=(const ThreadLocalArena&) = delete;

    template <typename T, typename... Args>
    [[nodiscard]] T* create(Args&&... args) {
        void* memory = allocate(sizeof(T), alignof(T));
        return ::new (memory) T(std::forward<Args>(args)...);
    }

    [[nodiscard]] void* allocate(std::size_t bytes, std::size_t alignment) {
        std::size_t current_addr = reinterpret_cast<std::size_t>(buffer_ + offset_);
        std::size_t aligned_addr = (current_addr + (alignment - 1)) & ~(alignment - 1);
        std::size_t padding = aligned_addr - current_addr;
        std::size_t needed = bytes + padding;

        if (offset_ + needed > capacity_) {
            grow(needed);
            return allocate(bytes, alignment);
        }

        offset_ += needed;
        return reinterpret_cast<void*>(aligned_addr);
    }

    void reset() noexcept {
        // Миттєве скидання: деструктори тривіальних об'єктів викликати не потрібно
        offset_ = 0;
        // Звільняємо додаткові блоки, залишаючи лише базовий для повторного використання
        while (!overflow_chunks_.empty()) {
            ::operator delete(overflow_chunks_.back().first, std::align_val_t{64});
            overflow_chunks_.pop_back();
        }
    }

    [[nodiscard]] std::size_t bytes_allocated() const noexcept {
        return offset_;
    }

private:
    void grow(std::size_t min_needed) {
        // Зберігаємо поточний заповнений блок
        overflow_chunks_.emplace_back(buffer_, capacity_);

        // Подвоюємо місткість нового блоку
        capacity_ = std::max(capacity_ * 2, min_needed + DefaultChunkSize);
        buffer_ = static_cast<std::byte*>(::operator new(capacity_, std::align_val_t{64}));
        offset_ = 0;
    }

    void release_all() noexcept {
        if (buffer_) {
            ::operator delete(buffer_, std::align_val_t{64});
            buffer_ = nullptr;
        }
        for (auto& [ptr, cap] : overflow_chunks_) {
            ::operator delete(ptr, std::align_val_t{64});
        }
        overflow_chunks_.clear();
    }

    std::byte* buffer_{nullptr};
    std::size_t capacity_{0};
    std::size_t offset_{0};
    std::vector<std::pair<std::byte*, std::size_t>> overflow_chunks_{};
};

// Глобальна потоково-ізольована арена. Кожен потік отримує свій незалежний екземпляр!
inline thread_local ThreadLocalArena g_per_thread_arena{};
