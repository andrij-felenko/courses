#ifndef UART_RING_BUFFER_HPP
#define UART_RING_BUFFER_HPP

#include <cstddef>
#include <cstdint>
#include <array>
#include <string_view>

/**
 * @brief Кільцевий буфер для асинхронного накопичення байтів UART.
 * Використовується в перериваннях RX для безвтратного прийому даних та
 * неблокуючого розбору відповідей AT-інтерпретатора.
 * 
 * @tparam Capacity Розмір буфера у байтах (за замовчуванням 256)
 */
template <size_t Capacity = 256>
class UartRingBuffer {
public:
    UartRingBuffer() = default;

    /**
     * @brief Запис одного байта в буфер (викликається з ISR UART RX).
     * @param byte Прийнятий байт.
     * @return true якщо байт успішно записано, false при переповненні буфера.
     */
    bool push(uint8_t byte) noexcept {
        size_t next_head = (head_ + 1) % Capacity;
        if (next_head == tail_) {
            return false;
        }
        buffer_[head_] = byte;
        head_ = next_head;
        return true;
    }

    /**
     * @brief Зчитування одного байта з буфера.
     * @param byte Посилання для збереження зчитаного байта.
     * @return true якщо байт зчитано, false якщо буфер порожній.
     */
    bool pop(uint8_t& byte) noexcept {
        if (empty()) {
            return false;
        }
        byte = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        return true;
    }

    /**
     * @brief Перевірка, чи порожній буфер.
     */
    bool empty() const noexcept {
        return head_ == tail_;
    }

    /**
     * @brief Отримання кількості доступних для зчитування байтів.
     */
    size_t available() const noexcept {
        if (head_ >= tail_) {
            return head_ - tail_;
        }
        return Capacity - (tail_ - head_);
    }

    /**
     * @brief Очищення вмісту буфера.
     */
    void clear() noexcept {
        head_ = 0;
        tail_ = 0;
    }

    /**
     * @brief Пошук збігу підрядка std::string_view у буфері без його очищення.
     * @param target Шуканий рядок (наприклад, "OK\r\n" або "ERROR\r\n").
     * @return true якщо target знайдено в поточному вмісті буфера.
     */
    bool find(std::string_view target) const noexcept {
        size_t avail = available();
        if (target.empty() || avail < target.size()) {
            return false;
        }

        for (size_t i = 0; i <= avail - target.size(); ++i) {
            bool match = true;
            for (size_t j = 0; j < target.size(); ++j) {
                size_t idx = (tail_ + i + j) % Capacity;
                if (buffer_[idx] != static_cast<uint8_t>(target[j])) {
                    match = false;
                    break;
                }
            }
            if (match) {
                return true;
            }
        }
        return false;
    }

    /**
     * @brief Копіювання накопиченого вмісту буфера у лінійний буфер без вилучення байтів.
     * @param dest Вказівник на цільовий масив.
     * @param max_len Максимальний розмір цільового масиву.
     * @return Кількість скопійованих байтів.
     */
    size_t peek_bytes(char* dest, size_t max_len) const noexcept {
        if (!dest || max_len == 0) {
            return 0;
        }

        size_t avail = available();
        size_t to_copy = (avail < max_len) ? avail : max_len;

        for (size_t i = 0; i < to_copy; ++i) {
            size_t idx = (tail_ + i) % Capacity;
            dest[i] = static_cast<char>(buffer_[idx]);
        }

        return to_copy;
    }

private:
    std::array<uint8_t, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};

#endif // UART_RING_BUFFER_HPP
