#include <array>
#include <optional>
#include <span>

template <size_t Capacity>
class EventQueue {
public:
    constexpr EventQueue() = default;

    bool post(const Event& ev) noexcept;
    std::optional<Event> pop() noexcept;
    [[nodiscard]] std::optional<Event> peek() const noexcept;
    void clear() noexcept;
    [[nodiscard]] size_t size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    [[nodiscard]] uint32_t drops() const noexcept;

private:
    std::array<Event, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
    volatile size_t count_{0};
    uint32_t overflow_drops_{0};
};
