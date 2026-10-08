#ifndef GP2Y0A21_HPP
#define GP2Y0A21_HPP

#include "adc_interface.hpp"
#include <cstdint>
#include <cstddef>
#include <array>

/**
 * @brief Перелік статусів результату вимірювання відстані.
 */
enum class DistanceStatus {
    OK,                   ///< Вимірювання успішне, відстань у межах 10–80 см
    OutOfBoundsTooClose,  ///< Об'єкт занадто близько (< 10 см)
    OutOfBoundsTooFar,    ///< Об'єкт занадто далеко (> 80 см)
    InsufficientSamples   ///< Недостатньо вибірок у буфері для фільтрації
};

/**
 * @brief Структура результату вимірювання відстані та відповідного статусу.
 */
struct MeasurementResult {
    float distanceCm;
    DistanceStatus status;
};

/**
 * @brief Элемент таблиці пошуку (LUT) для лінеаризації характеристики сенсора.
 */
struct LutEntry {
    uint16_t adcValue;  ///< Сире значення АЦП
    float distanceCm;   ///< Відповідна відстань у см
};

/**
 * @brief Шаблонний кільцевий буфер фіксованого розміру без динамічного виділення пам'яті.
 * 
 * @tparam T Тип даних елементів
 * @tparam Capacity Максимальна кількість елементів у буфері
 */
template <typename T, std::size_t Capacity>
class RingBuffer {
public:
    RingBuffer() : head_(0), count_(0) {}

    /**
     * @brief Додає новий елемент у буфер (перезаписує найстаріший при переповненні).
     */
    void push(T item) {
        data_[head_] = item;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            count_++;
        }
    }

    /**
     * @brief Очищує вміст буфера.
     */
    void clear() {
        head_ = 0;
        count_ = 0;
    }

    [[nodiscard]] bool isFull() const {
        return count_ == Capacity;
    }

    [[nodiscard]] std::size_t size() const {
        return count_;
    }

    [[nodiscard]] constexpr std::size_t capacity() const {
        return Capacity;
    }

    /**
     * @brief Копіює елементи з кільцевого буфера в масив-приймач від найстарішого до найновішого.
     * @param dest Вказівник на масив призначення розміром щонайменше size().
     */
    void copyTo(T* dest) const {
        if (count_ == 0) {
            return;
        }
        std::size_t start = (count_ < Capacity) ? 0 : head_;
        for (std::size_t i = 0; i < count_; ++i) {
            dest[i] = data_[(start + i) % Capacity];
        }
    }

private:
    std::array<T, Capacity> data_{};
    std::size_t head_;
    std::size_t count_;
};

/**
 * @brief Драйвер аналогового ІЧ-далекоміра Sharp GP2Y0A21YK0F.
 */
class SharpGP2Y0A21 {
public:
    static constexpr std::size_t BUFFER_SIZE = 5;
    static constexpr float MIN_DISTANCE_CM = 10.0f;
    static constexpr float MAX_DISTANCE_CM = 80.0f;

    explicit SharpGP2Y0A21(IAdcChannel& adcChannel);

    /**
     * @brief Зчитує нову вибірку з АЦП та додає її до кільцевого буфера.
     */
    void sample();

    /**
     * @brief Додає передане значення АЦП до буфера.
     */
    void addSample(uint16_t adcRaw);

    /**
     * @brief Обчислює відфільтроване значення відстані на основі медіанної фільтрації.
     * @return Результат вимірювання (відстань та статус)
     */
    MeasurementResult getDistance();

    /**
     * @brief Скидає вміст кільцевого буфера.
     */
    void reset();

    /**
     * @brief Медіанна фільтрація вибірок із буфера.
     * @param outMedian Вихідне значення медіани АЦП
     * @return true якщо фільтрація успішна (буфер повний), інакше false
     */
    bool getMedianAdc(uint16_t& outMedian) const;

    /**
     * @brief Перетворення відфільтрованого значення АЦП у відстань за таблицею LUT та інтерполяцією.
     * @param adcRaw Значення АЦП
     * @return Розрахована відстань у см
     */
    static float interpolateDistance(uint16_t adcRaw);

private:
    IAdcChannel& adcChannel_;
    RingBuffer<uint16_t, BUFFER_SIZE> buffer_;

    static constexpr std::size_t LUT_SIZE = 9;
    static const LutEntry LUT[LUT_SIZE];
};

#endif // GP2Y0A21_HPP
