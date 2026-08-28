#include <cstddef>
#include <array>
#include <iterator>
#include <type_traits>
#include <stdexcept>
#include <iostream>
#include <concepts>

template<typename T, std::size_t Capacity>
class StaticRingBuffer {
public:
    static_assert(Capacity > 0, "Місткість буфера повинна бути більшою за нуль!");

    using value_type = T;
    using size_type = std::size_t;

    constexpr StaticRingBuffer() noexcept = default;

    // Конструктор 1: із фіксованого масиву
    constexpr explicit StaticRingBuffer(const T (&arr)[Capacity]) {
        for (std::size_t i = 0; i < Capacity; ++i) {
            push_back(arr[i]);
        }
    }

    // Конструктор 2: із пари ітераторів
    template<std::input_iterator Iter>
    constexpr StaticRingBuffer(Iter first, Iter last) {
        while (first != last && m_size < Capacity) {
            push_back(*first);
            ++first;
        }
    }

    // Конструктор 3: зі списку ініціалізації
    constexpr explicit StaticRingBuffer(std::initializer_list<T> list) {
        if (list.size() > Capacity) {
            throw std::out_of_range("Розмір списку ініціалізації перевищує місткість буфера");
        }
        for (const auto& item : list) {
            push_back(item);
        }
    }

    constexpr bool push_back(const T& val) {
        if (m_size >= Capacity) {
            return false; // Буфер заповнений
        }
        m_data[(m_head + m_size) % Capacity] = val;
        ++m_size;
        return true;
    }

    constexpr bool pop_front(T& out_val) {
        if (m_size == 0) {
            return false; // Буфер порожній
        }
        out_val = m_data[m_head];
        m_head = (m_head + 1) % Capacity;
        --m_size;
        return true;
    }

    [[nodiscard]] constexpr size_type size() const noexcept { return m_size; }
    [[nodiscard]] constexpr size_type capacity() const noexcept { return Capacity; }
    [[nodiscard]] constexpr bool empty() const noexcept { return m_size == 0; }
    [[nodiscard]] constexpr bool full() const noexcept { return m_size == Capacity; }

    [[nodiscard]] constexpr const T& operator[](size_type idx) const {
        if (idx >= m_size) {
            throw std::out_of_range("Індекс виходить за межі заповненого буфера");
        }
        return m_data[(m_head + idx) % Capacity];
    }

private:
    std::array<T, Capacity> m_data{};
    std::size_t m_head = 0;
    std::size_t m_size = 0;
};

// -----------------------------------------------------------------------------
// Керівні правила виведення (Deduction Guides)
// -----------------------------------------------------------------------------

// Правило 1: Виведення типу T та точного розміру N із C-масиву за посиланням
template<typename T, std::size_t N>
StaticRingBuffer(const T (&)[N]) -> StaticRingBuffer<std::decay_t<T>, N>;

// Правило 2: Виведення типу елемента з ітераторів (місткість за замовчуванням = 64)
template<std::input_iterator Iter>
StaticRingBuffer(Iter, Iter) 
    -> StaticRingBuffer<typename std::iterator_traits<Iter>::value_type, 64>;

// Правило 3: Виведення зі списку ініціалізації (місткість за замовчуванням = 32)
template<typename T>
StaticRingBuffer(std::initializer_list<T>) -> StaticRingBuffer<T, 32>;
