#include <atomic>
#include <vector>
#include <optional>
#include <cstddef>
#include <new>

#if defined(__cpp_lib_hardware_interference_size)
    using std::hardware_destructive_interference_size;
#else
    // Стандартний розмір кеш-лінії більшості сучасних CPU
    constexpr std::size_t hardware_destructive_interference_size = 64;
#endif

template <typename T>
class SpscRingBuffer {
public:
    explicit SpscRingBuffer(std::size_t power_of_two_capacity)
        : capacity_(power_of_two_capacity),
          mask_(power_of_two_capacity - 1),
          buffer_(power_of_two_capacity) {
        // Перевірка на степінь двійки
        if (capacity_ < 2 || (capacity_ & mask_) != 0) {
            throw std::invalid_argument("Capacity must be a power of two");
        }
        tail_.store(0, std::memory_order_relaxed);
        head_.store(0, std::memory_order_relaxed);
    }

    bool try_push(T item) {
        const std::size_t current_tail = tail_.load(std::memory_order_relaxed);

        // Використовуємо локальний кеш індексу читання для мінімізації між'ядерного трафіку
        if (current_tail - cached_head_ >= capacity_) {
            cached_head_ = head_.load(std::memory_order_acquire);
            if (current_tail - cached_head_ >= capacity_) {
                return false; // Черга заповнена
            }
        }

        buffer_[current_tail & mask_] = std::move(item);
        // Бар'єр release публікує записаний елемент для споживача
        tail_.store(current_tail + 1, std::memory_order_release);
        return true;
    }

    std::optional<T> try_pop() {
        const std::size_t current_head = head_.load(std::memory_order_relaxed);

        if (current_head == cached_tail_) {
            cached_tail_ = tail_.load(std::memory_order_acquire);
            if (current_head == cached_tail_) {
                return std::nullopt; // Черга порожня
            }
        }

        T item = std::move(buffer_[current_head & mask_]);
        // Бар'єр release звільняє комірку буфера для виробника
        head_.store(current_head + 1, std::memory_order_release);
        return item;
    }

private:
    // Кеш-лінія виробника
    alignas(hardware_destructive_interference_size) std::atomic<std::size_t> tail_{0};
    std::size_t cached_head_{0};

    // Кеш-лінія споживача
    alignas(hardware_destructive_interference_size) std::atomic<std::size_t> head_{0};
    std::size_t cached_tail_{0};

    // Незмінні спільні дані
    const std::size_t capacity_;
    const std::size_t mask_;
    std::vector<T> buffer_;
};
