#include <contracts>
#include <cstddef>
#include <concepts>
#include <utility>
#include <new>
#include <type_traits>
#include <optional>

template <typename T, std::size_t Capacity>
    requires (Capacity > 0)
class BoundedRingBuffer {
private:
    // Сире сховище для розміщення об'єктів типу T без виклику конструкторів за замовчуванням
    alignas(alignof(T)) std::byte storage_[Capacity * sizeof(T)];
    std::size_t head_{0};
    std::size_t tail_{0};
    std::size_t size_{0};

    // Допоміжні методи прямого доступу до сирої пам'яті
    [[nodiscard]] T* ptr_at(std::size_t index) noexcept
        pre: index < Capacity
        post(ptr): ptr != nullptr
    {
        return reinterpret_cast<T*>(&storage_[index * sizeof(T)]);
    }

    [[nodiscard]] const T* ptr_at(std::size_t index) const noexcept
        pre: index < Capacity
        post(ptr): ptr != nullptr
    {
        return reinterpret_cast<const T*>(&storage_[index * sizeof(T)]);
    }

public:
    // Конструктор за замовчуванням: створює порожній буфер
    constexpr BoundedRingBuffer() noexcept
        post: empty() && size() == 0 && capacity() == Capacity
    {}

    // Деструктор: знищує всі живі елементи
    ~BoundedRingBuffer() noexcept {
        clear();
    }

    // Заборона копіювання для уникнення прихованих алокацій
    BoundedRingBuffer(const BoundedRingBuffer&) = delete;
    BoundedRingBuffer& operator=(const BoundedRingBuffer&) = delete;

    // Конструктор переміщення
    BoundedRingBuffer(BoundedRingBuffer&& other) noexcept
        post: other.empty() && other.size() == 0
    {
        while (!other.empty()) {
            push(std::move(other.front()));
            other.pop();
        }
    }

    // Інформаційні методи доступу до стану
    [[nodiscard]] constexpr std::size_t size() const noexcept
        post(res): res <= Capacity
    {
        return size_;
    }

    [[nodiscard]] constexpr std::size_t capacity() const noexcept
        post(res): res == Capacity
    {
        return Capacity;
    }

    [[nodiscard]] constexpr bool empty() const noexcept
        post(res): res == (size() == 0)
    {
        return size_ == 0;
    }

    [[nodiscard]] constexpr bool full() const noexcept
        post(res): res == (size() == Capacity)
    {
        return size_ == Capacity;
    }

    // Додавання нового елемента в кінець черги (копіюванням)
    void push(const T& value)
        pre [buffer_not_full]: !full()
        post: !empty() && (size() > 0)
    {
        contract_assert [valid_tail]: tail_ < Capacity;

        ::new (static_cast<void*>(ptr_at(tail_))) T(value);
        tail_ = (tail_ + 1) % Capacity;
        ++size_;

        contract_assert [math_invariant]: (head_ + size_) % Capacity == tail_;
    }

    // Додавання нового елемента в кінець черги (переміщенням)
    void push(T&& value)
        pre [buffer_not_full]: !full()
        post: !empty() && (size() > 0)
    {
        contract_assert [valid_tail]: tail_ < Capacity;

        ::new (static_cast<void*>(ptr_at(tail_))) T(std::move(value));
        tail_ = (tail_ + 1) % Capacity;
        ++size_;

        contract_assert [math_invariant]: (head_ + size_) % Capacity == tail_;
    }

    // Видалення найстарішого елемента черги
    void pop()
        pre [buffer_not_empty]: !empty()
        post: !full()
    {
        contract_assert [valid_head]: head_ < Capacity;

        ptr_at(head_)->~T();
        head_ = (head_ + 1) % Capacity;
        --size_;

        contract_assert [math_invariant]: (head_ + size_) % Capacity == tail_;
    }

    // Доступ до найстарішого елемента
    [[nodiscard]] T& front() noexcept
        pre [buffer_not_empty]: !empty()
    {
        return *ptr_at(head_);
    }

    [[nodiscard]] const T& front() const noexcept
        pre [buffer_not_empty]: !empty()
    {
        return *ptr_at(head_);
    }

    // Доступ до останнього доданого елемента
    [[nodiscard]] T& back() noexcept
        pre [buffer_not_empty]: !empty()
    {
        std::size_t last_idx = (tail_ == 0) ? (Capacity - 1) : (tail_ - 1);
        return *ptr_at(last_idx);
    }

    [[nodiscard]] const T& back() const noexcept
        pre [buffer_not_empty]: !empty()
    {
        std::size_t last_idx = (tail_ == 0) ? (Capacity - 1) : (tail_ - 1);
        return *ptr_at(last_idx);
    }

    // Повне очищення буфера зі знищенням елементів
    void clear() noexcept
        post: empty() && size() == 0
    {
        while (!empty()) {
            pop();
        }
        head_ = 0;
        tail_ = 0;
        size_ = 0;
    }
};
