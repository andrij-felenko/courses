#include <atomic>
#include <cstdint>
#include <type_traits>

template <typename T>
class SeqLock {
    static_assert(std::is_trivially_copyable_v<T>, "T must be trivially copyable");

public:
    SeqLock() noexcept : sequence_(0), data_{} {}

    void write(const T& new_data) noexcept {
        // Перехід у непарний стан (2k + 1)
        const std::uint64_t seq = sequence_.load(std::memory_order_relaxed);
        sequence_.store(seq + 1, std::memory_order_release);

        // Запис даних
        data_ = new_data;

        // Перехід у парний стан (2k + 2)
        sequence_.store(seq + 2, std::memory_order_release);
    }

    T read() const noexcept {
        T result;
        std::uint64_t v1{0};
        std::uint64_t v2{0};

        do {
            v1 = sequence_.load(std::memory_order_acquire);
            if (v1 & 1ULL) {
                continue; // Письменник активний
            }

            result = data_;

            v2 = sequence_.load(std::memory_order_acquire);
        } while (v1 != v2);

        return result;
    }

private:
    alignas(64) mutable std::atomic<std::uint64_t> sequence_;
    T data_;
};
