#include <atomic>
#include <cstdint>
#include <type_traits>

template <typename T>
class SeqLock {
    static_assert(std::is_trivially_copyable_v<T>, "Тип T мусить бути тривіально копійованим");

public:
    constexpr SeqLock() noexcept : sequence_(0), data_{} {}

    void write(const T& new_data) noexcept {
        const std::uint64_t current_seq = sequence_.load(std::memory_order_relaxed);

        // Перехід у непарний стан із release-семантикою
        sequence_.store(current_seq + 1, std::memory_order_release);

        // Копіювання полів монолітного об'єкта
        data_ = new_data;

        // Перехід у парний стан із release-семантикою
        sequence_.store(current_seq + 2, std::memory_order_release);
    }

    bool try_read(T& out_data) const noexcept {
        // Зчитування початкової версії з acquire-семантикою
        const std::uint64_t v1 = sequence_.load(std::memory_order_acquire);

        if (v1 & 1ULL) {
            return false; // Запис у процесі
        }

        // Копіювання даних у локальну змінну
        out_data = data_;

        // Атомний бар'єр запобігає перевпорядкуванню читання полів після v2
        std::atomic_thread_fence(std::memory_order_acquire);

        const std::uint64_t v2 = sequence_.load(std::memory_order_relaxed);

        return (v1 == v2);
    }

private:
    alignas(64) mutable std::atomic<std::uint64_t> sequence_;
    T data_;
};
