#ifndef RANDOM_PROJECTION_ENGINE_HPP
#define RANDOM_PROJECTION_ENGINE_HPP

#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>
#include <memory>
#include <stdexcept>
#include <string_view>

namespace search::rp {

enum class Distribution {
    Gaussian,          // Щільна гаусова матриця N(0, 1)
    Rademacher,        // Знакова матриця {+1, -1}
    SparseAchlioptas,  // Розріджена матриця Ахіоптаса (66.7% нулів)
    VerySparse         // Дуже розріджена матриця зі щільністю s = √d
};

struct ProjectionConfig {
    size_t orig_dim{0};
    size_t target_dim{0};
    Distribution dist{Distribution::SparseAchlioptas};
    uint64_t seed{1337};
    bool normalize_output{false};
};

class Engine {
public:
    // Конструктор: валідує вхідні параметри та генерує матрицю проєктування
    explicit Engine(const ProjectionConfig& config);
    ~Engine() = default;

    Engine(const Engine&) = delete;
    Engine& operator=(const Engine&) = delete;
    Engine(Engine&&) noexcept = default;
    Engine& operator=(Engine&&) noexcept = default;

    // Проєктування одного вектора через безпечні std::span
    void transform(std::span<const float> input, std::span<float> output) const;

    // Проєктування з поверненням нового динамічного вектора
    [[nodiscard]] std::vector<float> transform(std::span<const float> input) const;

    // Пакетне перетворення масиву векторів у плоскій матриці
    void transform_batch(
        std::span<const float> flat_input_matrix,
        size_t num_vectors,
        std::span<float> flat_output_matrix
    ) const;

    [[nodiscard]] size_t orig_dim() const noexcept { return config_.orig_dim; }
    [[nodiscard]] size_t target_dim() const noexcept { return config_.target_dim; }
    [[nodiscard]] Distribution distribution() const noexcept { return config_.dist; }

private:
    ProjectionConfig config_;
    std::vector<float> matrix_;

    void initialize_matrix();
};

} // namespace search::rp

#endif // RANDOM_PROJECTION_ENGINE_HPP
