#ifndef VECTOR_METRICS_HPP
#define VECTOR_METRICS_HPP

#include <span>
#include <vector>
#include <expected>
#include <cstddef>
#include <cstdint>

namespace metrics {

/**
 * @brief Перелічуваний клас помилок векторного API у C++.
 */
enum class Status : int32_t {
    Success            =  0,
    NullPointer        = -1,
    InvalidSize        = -2,
    SizeMismatch       = -3,
    ZeroNorm           = -4,
    UnalignedData      = -5
};

/**
 * @brief Елемент розрідженого вектора (індекс-значення).
 */
struct SparseEntry {
    std::size_t index;
    float value;
};

/**
 * @brief Налаштування обчислення метрик.
 */
struct Options {
    bool use_simd{true};
    bool assume_normalized{false};
    float zero_eps{1e-12f};
};

/**
 * @brief Головний клас-сервіс для обчислення векторних метрик.
 */
class VectorMetrics {
public:
    VectorMetrics() = delete;

    /**
     * @brief Обчислює косинусну відстань між двома щільними векторами.
     * @param u Перший вектор
     * @param v Другий вектор
     * @param opts Додаткові опції обчислення
     * @return std::expected з обчисленою відстанню d_cos або кодом помилки Status
     */
    [[nodiscard]] static std::expected<float, Status> cosineDistance(
        std::span<const float> u,
        std::span<const float> v,
        const Options& opts = Options{}
    ) noexcept;

    /**
     * @brief Пакетне обчислення відстаней від запиту до матриці векторів.
     * @param query Вектор запиту (розмір dim)
     * @param matrix Суцільний масив векторів індексу (розмір num_vectors * dim)
     * @param num_vectors Кількість векторів
     * @param dim Вимірність
     * @param out_dists Буфер для запису результатів (розмір num_vectors)
     * @param opts Опції
     * @return Status::Success або відповідний код помилки
     */
    static Status cosineDistanceBatch(
        std::span<const float> query,
        std::span<const float> matrix,
        std::size_t num_vectors,
        std::size_t dim,
        std::span<float> out_dists,
        const Options& opts = Options{}
    ) noexcept;

    /**
     * @brief Обчислює косинусну відстань між розрідженими векторами.
     */
    [[nodiscard]] static std::expected<float, Status> cosineDistanceSparse(
        std::span<const SparseEntry> u,
        std::span<const SparseEntry> v,
        const Options& opts = Options{}
    ) noexcept;

    /**
     * @brief Нормалізує вектор inplace за нормою L2.
     */
    static Status l2Normalize(
        std::span<float> vector,
        float eps = 1e-12f
    ) noexcept;
};

} // namespace metrics

#endif // VECTOR_METRICS_HPP
