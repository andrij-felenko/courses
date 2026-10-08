#ifndef UART_RING_BUFFER_HPP
#define UART_RING_BUFFER_HPP

#include <array>
#include <cstddef>
#include <cstdint>
#include <atomic>

/**
 * @brief Кільцевий буфер для асинхронного накопичення байтів з послідовного порту UART.
 * 
 * Клас реалізує потокобезпечний буфер типу Single-Producer Single-Consumer (SPSC).
 * Запис (push) виконується з переривання UART (ISR), а зчитування (pop) — 
 * FSM-парсером у головному циклі програми без використання блокуючих операцій.
 * 
 * @tparam Capacity Розмір буфера (мусить бути ступенем двійки).
 */
template <std::size_t Capacity = 256>
class UartRingBuffer {
    static_assert(Capacity > 0, "Розмір буфера мусить бути більшим за 0");
    static_assert((Capacity & (Capacity - 1)) == 0, "Розмір буфера мусить бути ступенем 2");

public:
    UartRingBuffer() : m_head(0), m_tail(0) {}

    /**
     * @brief Записує байт у кільцевий буфер (викликається в ISR переривання UART).
     * @param byte Отриманий байт з апаратного порту.
     * @return true, якщо байт збережено; false, якщо буфер переповнено.
     */
    bool push(uint8_t byte) noexcept {
        const std::size_t currentHead = m_head.load(std::memory_order_relaxed);
        const std::size_t nextHead = (currentHead + 1) & (Capacity - 1);

        if (nextHead == m_tail.load(std::memory_order_acquire)) {
            return false; // Буфер переповнений, новий байт відкидається
        }

        m_buffer[currentHead] = byte;
        m_head.store(nextHead, std::memory_order_release);
        return true;
    }

    /**
     * @brief Вилучає один байт із кільцевого буфера (викликається FSM-парсером).
     * @param byte Посилання на змінну для збереження вилученого байта.
     * @return true, якщо байт вилучено; false, якщо буфер порожній.
     */
    bool pop(uint8_t& byte) noexcept {
        const std::size_t currentTail = m_tail.load(std::memory_order_relaxed);

        if (currentTail == m_head.load(std::memory_order_acquire)) {
            return false; // Буфер порожній
        }

        byte = m_buffer[currentTail];
        m_tail.store((currentTail + 1) & (Capacity - 1), std::memory_order_release);
        return true;
    }

    /**
     * @brief Перевіряє, чи буфер порожній.
     */
    bool isEmpty() const noexcept {
        return m_tail.load(std::memory_order_relaxed) == m_head.load(std::memory_order_relaxed);
    }

    /**
     * @brief Перевіряє, чи буфер заповнений.
     */
    bool isFull() const noexcept {
        const std::size_t nextHead = (m_head.load(std::memory_order_relaxed) + 1) & (Capacity - 1);
        return nextHead == m_tail.load(std::memory_order_relaxed);
    }

    /**
     * @brief Обчислює кількість накопичених байтів, доступних для зчитування.
     */
    std::size_t available() const noexcept {
        const std::size_t head = m_head.load(std::memory_order_relaxed);
        const std::size_t tail = m_tail.load(std::memory_order_relaxed);
        return (head >= tail) ? (head - tail) : (Capacity - tail + head);
    }

    /**
     * @brief Скидає вказівники буфера (очищення при ініціалізації чи помилках).
     */
    void clear() noexcept {
        const std::size_t head = m_head.load(std::memory_order_relaxed);
        m_tail.store(head, std::memory_order_release);
    }

private:
    std::array<uint8_t, Capacity> m_buffer{};
    std::atomic<std::size_t> m_head;
    std::atomic<std::size_t> m_tail;
};

using DefaultUartRingBuffer = UartRingBuffer<256>;

#endif // UART_RING_BUFFER_HPP
