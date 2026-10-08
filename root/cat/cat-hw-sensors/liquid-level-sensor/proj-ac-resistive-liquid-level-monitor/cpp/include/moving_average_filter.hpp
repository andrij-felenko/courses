#pragma once

#include <vector>
#include <cstddef>
#include <numeric>
#include <algorithm>
#include <stdexcept>

/**
 * @brief Клас цифрового фільтра ковзного середнього (Moving Average Filter).
 * 
 * Призначений для обробки та згладжування аналогових сигналів від давача рівня рідини.
 * Використовує кільцевий буфер фіксованого розміру для ефективного додавання нових
 * відліків та обчислення середнього значення без перенаправлення масиву.
 */
class MovingAverageFilter {
public:
    /**
     * @brief Конструктор фільтра ковзного середнього.
     * @param windowSize Розмір вікна фільтрації (кількість відліків).
     */
    explicit MovingAverageFilter(std::size_t windowSize = 10)
        : capacity_(windowSize > 0 ? windowSize : 1),
          head_(0),
          count_(0),
          sum_(0.0) {
        buffer_.resize(capacity_, 0.0f);
    }

    /**
     * @brief Додати новий аналоговий відлік до фільтра.
     * @param sample Нове виміряне значення напруги або рівня.
     */
    void addSample(float sample) {
        if (count_ < capacity_) {
            // Заповнення буфера на початковому етапі
            buffer_[head_] = sample;
            sum_ += sample;
            count_++;
        } else {
            // Оновлення кільцевого буфера: віднімаємо найстаріший елемент, додаємо новий
            sum_ -= buffer_[head_];
            buffer_[head_] = sample;
            sum_ += sample;
        }

        // Перехід до наступного індексу за модулем розміру буфера
        head_ = (head_ + 1) % capacity_;
    }

    /**
     * @brief Отримати поточне згладжене середнє значення.
     * @return Поточне ковзне середнє значення або 0.0f, якщо буфер порожній.
     */
    float getAverage() const {
        if (count_ == 0) {
            return 0.0f;
        }
        return static_cast<float>(sum_ / count_);
    }

    /**
     * @brief Очистити буфер та скинути внутрішні значення.
     */
    void reset() {
        std::fill(buffer_.begin(), buffer_.end(), 0.0f);
        head_ = 0;
        count_ = 0;
        sum_ = 0.0;
    }

    /**
     * @brief Перевірити, чи заповнено вікно фільтрації повністю.
     * @return true, якщо кількість відліків дорівнює ємності буфера.
     */
    bool isFull() const {
        return count_ == capacity_;
    }

    /**
     * @brief Отримати поточну кількість накопичених відліків.
     */
    std::size_t count() const {
        return count_;
    }

    /**
     * @brief Отримати ємність (розмір вікна) фільтра.
     */
    std::size_t capacity() const {
        return capacity_;
    }

private:
    std::vector<float> buffer_;  ///< Кільцевий буфер для зберігання відліків
    std::size_t capacity_;       ///< Максимальний розмір вікна
    std::size_t head_;           ///< Індекс для вставки наступного елемента
    std::size_t count_;          ///< Поточна кількість відліків у буфері
    double sum_;                 ///< Накопичена сума відліків у поточному вікні
};
