#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>
#include <string_view>
#include <algorithm>

/**
 * @brief Кільцевий буфер UART для асинхронного накопичення байтів з послідовного порту.
 * 
 * Забезпечує неблокуючий обмін даними між перериванням UART (RX ISR) та
 * вищим рівнем парсингу AT-команд. Використовує атомарні індекси для безпечного
 * однонаправленого обміну Lock-Free (один виробник ISR, один споживач FSM).
 * 
 * @tparam Capacity Розмір буфера у байтах (мусить бути ступенем двійки).
 */
template <size_t Capacity = 2048>
class UartRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two.");

public:
    UartRingBuffer() : head_(0), tail_(0) {}

    /**
     * @brief Додавання одного байта у буфер (викликається в ISR UART).
     * @param byte Вхідний байт із регістру даних UART.
     * @return true якщо байт записано, false якщо буфер переповнено.
     */
    bool push(uint8_t byte) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t next_head = (current_head + 1) & mask_;

        if (next_head == tail_.load(std::memory_order_acquire)) {
            // Переповнення буфера — захист від втрати цілісності індексів
            return false;
        }

        buffer_[current_head] = byte;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    /**
     * @brief Пакетний запис масиву байтів у буфер.
     * @param data Вказівник на дані.
     * @param len Довжина масиву.
     * @return Фактично записана кількість байтів.
     */
    size_t push_bytes(const uint8_t* data, size_t len) noexcept {
        size_t written = 0;
        for (size_t i = 0; i < len; ++i) {
            if (!push(data[i])) {
                break;
            }
            written++;
        }
        return written;
    }

    /**
     * @brief Извлечение одного байта з буфера.
     * @param byte Посилання для збереження прочитаного байта.
     * @return true якщо прочитано успішно.
     */
    bool pop(uint8_t& byte) noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return false;
        }

        byte = buffer_[current_tail];
        tail_.store((current_tail + 1) & mask_, std::memory_order_release);
        return true;
    }

    /**
     * @brief Пакетне вилучення накопичених байтів.
     * @param dest Запитуваний масив для вивантаження.
     * @param max_len Максимальна кількість байтів для зчитання.
     * @return Кількість прочитаних байтів.
     */
    size_t pop_bytes(uint8_t* dest, size_t max_len) noexcept {
        size_t read_bytes = 0;
        size_t current_tail = tail_.load(std::memory_order_relaxed);
        const size_t current_head = head_.load(std::memory_order_acquire);

        while (read_bytes < max_len && current_tail != current_head) {
            dest[read_bytes++] = buffer_[current_tail];
            current_tail = (current_tail + 1) & mask_;
        }

        tail_.store(current_tail, std::memory_order_release);
        return read_bytes;
    }

    /**
     * @brief Перегляд байта за зміщенням від tail без видалення з буфера.
     * @param byte Посилання для збереження результату.
     * @param offset Зміщення від поточного хвоста.
     * @return true якщо за вказаним зміщенням є дані.
     */
    bool peek(uint8_t& byte, size_t offset = 0) const noexcept {
        if (offset >= available()) {
            return false;
        }
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        byte = buffer_[(current_tail + offset) & mask_];
        return true;
    }

    /**
     * @brief Пропуск вказаної кількості байтів.
     * @param len Кількість байтів для пропуску.
     * @return Фактична кількість пропущених байтів.
     */
    size_t skip(size_t len) noexcept {
        const size_t avail = available();
        const size_t to_skip = std::min(len, avail);
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        tail_.store((current_tail + to_skip) & mask_, std::memory_order_release);
        return to_skip;
    }

    /**
     * @brief Отримання обсягу доступних для читання даних у байтах.
     */
    size_t available() const noexcept {
        const size_t h = head_.load(std::memory_order_acquire);
        const size_t t = tail_.load(std::memory_order_relaxed);
        return (h >= t) ? (h - t) : (Capacity - t + h);
    }

    /**
     * @brief Очищення буфера.
     */
    void clear() noexcept {
        head_.store(0, std::memory_order_relaxed);
        tail_.store(0, std::memory_order_release);
    }

    /**
     * @brief Пошук текстового шаблону у буфері без зміни стану елементів.
     * @param pattern Послідовність символів для пошуку (наприклад "+IPD," або "OK\r\n").
     * @return Позиція відносно поточного tail або -1 якщо шаблон не знайдено.
     */
    int find_pattern(std::string_view pattern) const noexcept {
        const size_t avail = available();
        if (pattern.empty() || avail < pattern.size()) {
            return -1;
        }

        const size_t limit = avail - pattern.size();
        for (size_t i = 0; i <= limit; ++i) {
            bool match = true;
            for (size_t j = 0; j < pattern.size(); ++j) {
                uint8_t b = 0;
                peek(b, i + j);
                if (static_cast<char>(b) != pattern[j]) {
                    match = false;
                    break;
                }
            }
            if (match) {
                return static_cast<int>(i);
            }
        }
        return -1;
    }

private:
    std::array<uint8_t, Capacity> buffer_{};
    std::atomic<size_t> head_;
    std::atomic<size_t> tail_;
    static constexpr size_t mask_ = Capacity - 1;
};
