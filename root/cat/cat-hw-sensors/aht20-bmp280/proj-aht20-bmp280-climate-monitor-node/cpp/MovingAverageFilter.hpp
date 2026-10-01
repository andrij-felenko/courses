#pragma once

#include <array>
#include <cstddef>
#include <type_traits>

/**
 * @brief Шаблонний C++ клас цифрового фільтра ковзного усереднення на основі кільцевого буфера.
 * 
 * @tparam T Числовий тип вимірювальних даних (float, double тощо)
 * @tparam WindowSize Кількість вибірок у вікні усереднення
 */
template <typename T, std::size_t WindowSize>
class MovingAverageFilter {
    static_assert(WindowSize > 0, "Розмір вікна усереднення має бути більшим за 0");
    static_assert(std::is_floating_point_v<T> || std::is_integral_v<T>,
                  "Тип даних фільтра повинен бути числовим");

public:
    MovingAverageFilter() = default;

    /**
     * @brief Додає нову вибірку до кільцевого буфера та оновлює накопичену суму.
     * @param sample Нове виміряне значення
     */
    void addSample(T sample) {
        if (count_ == WindowSize) {
            sum_ -= buffer_[head_];
        } else {
            ++count_;
        }

        buffer_[head_] = sample;
        sum_ += sample;
        head_ = (head_ + 1) % WindowSize;
    }

    /**
     * @brief Обчислює поточне згладжене середнє значення.
     * @return Згладжене значення або T{0}, якщо буфер порожній.
     */
    T getAverage() const {
        if (count_ == 0) {
            return T{0};
        }
        return static_cast<T>(sum_ / static_cast<T>(count_));
    }

    /**
     * @brief Скидає стан фільтра та очищує накопичувальний буфер.
     */
    void reset() {
        buffer_.fill(T{0});
        head_ = 0;
        count_ = 0;
        sum_ = T{0};
    }

    /**
     * @brief Повертає кількість накопичених вибірок.
     */
    std::size_t getCount() const { return count_; }

    /**
     * @brief Перевіряє, чи заповнений буфер повністю.
     */
    bool isFull() const { return count_ == WindowSize; }

    /**
     * @brief Перевіряє, чи порожній буфер.
     */
    bool isEmpty() const { return count_ == 0; }

private:
    std::array<T, WindowSize> buffer_{};
    std::size_t head_{0};
    std::size_t count_{0};
    T sum_{T{0}};
};
