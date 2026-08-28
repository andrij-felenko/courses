#include <span>
#include <cstddef>
#include <concepts>

template <size_t MinOrder = 4, size_t MaxOrder = 20>
class BuddyMemoryPool {
public:
    static constexpr size_t MinSize = 1ULL << MinOrder;
    static constexpr size_t MaxSize = 1ULL << MaxOrder;

    // Конструктор приймає готовий типізований буфер пам'яті
    explicit BuddyMemoryPool(std::span<std::byte, MaxSize> storage) noexcept;

    ~BuddyMemoryPool() noexcept = default;

    // Заборона копіювання для збереження унікальності стану пулу
    BuddyMemoryPool(const BuddyMemoryPool&) = delete;
    BuddyMemoryPool& operator=(const BuddyMemoryPool&) = delete;

    // Дозволено безпечне переміщення
    BuddyMemoryPool(BuddyMemoryPool&&) noexcept = default;
    BuddyMemoryPool& operator=(BuddyMemoryPool&&) noexcept = default;

    // Виділення повертає span з точним розміром виділеного кванта
    [[nodiscard]] std::span<std::byte> allocate(size_t bytes) noexcept;

    // Звільнення приймає раніше виділений span
    void deallocate(std::span<std::byte> block) noexcept;

    [[nodiscard]] size_t total_capacity() const noexcept { return MaxSize; }
    [[nodiscard]] size_t allocated_size() const noexcept;
    [[nodiscard]] size_t available_size() const noexcept;
};
