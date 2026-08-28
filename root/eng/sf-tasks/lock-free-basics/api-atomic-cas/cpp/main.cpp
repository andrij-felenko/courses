#include <atomic>

template <typename T>
class atomic {
public:
    // Сильний варіант CAS
    bool compare_exchange_strong(
        T& expected,
        T desired,
        std::memory_order success_order,
        std::memory_order failure_order
    ) noexcept;

    bool compare_exchange_strong(
        T& expected,
        T desired,
        std::memory_order order = std::memory_order_seq_cst
    ) noexcept;

    // Слабкий варіант CAS
    bool compare_exchange_weak(
        T& expected,
        T desired,
        std::memory_order success_order,
        std::memory_order failure_order
    ) noexcept;

    bool compare_exchange_weak(
        T& expected,
        T desired,
        std::memory_order order = std::memory_order_seq_cst
    ) noexcept;
};
