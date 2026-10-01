#ifndef RING_BUFFER_HPP
#define RING_BUFFER_HPP

#include <cstddef>
#include <cstdint>

// Шаблонний клас статичного кільцевого буфера FIFO для вбудованих систем.
// Утилізує фіксований масив без застосування динамічної пам'яті (Heap).
template <typename T, std::size_t Capacity>
class RingBuffer {
public:
    RingBuffer() : m_head(0), m_tail(0), m_size(0) {}

    // Додає елемент у буфер. Повертає false, якщо буфер переповнений.
    bool push(const T& item) {
        if (isFull()) {
            return false;
        }
        m_buffer[m_head] = item;
        m_head = (m_head + 1) % Capacity;
        ++m_size;
        return true;
    }

    // Зчитує та видаляє перший елемент із буфера.
    bool pop(T& item) {
        if (isEmpty()) {
            return false;
        }
        item = m_buffer[m_tail];
        m_tail = (m_tail + 1) % Capacity;
        --m_size;
        return true;
    }

    // Переглядає перший елемент без видалення.
    bool peek(T& item) const {
        if (isEmpty()) {
            return false;
        }
        item = m_buffer[m_tail];
        return true;
    }

    // Перевіряє, чи порожній буфер.
    bool isEmpty() const {
        return m_size == 0;
    }

    // Перевіряє, чи заповнений буфер.
    bool isFull() const {
        return m_size == Capacity;
    }

    // Повертає поточну кількість елементів у буфері.
    std::size_t size() const {
        return m_size;
    }

    // Повертає максимально доступну ємність буфера.
    constexpr std::size_t capacity() const {
        return Capacity;
    }

    // Очищає вміст буфера.
    void clear() {
        m_head = 0;
        m_tail = 0;
        m_size = 0;
    }

private:
    T m_buffer[Capacity];
    std::size_t m_head;
    std::size_t m_tail;
    std::size_t m_size;
};

#endif // RING_BUFFER_HPP
