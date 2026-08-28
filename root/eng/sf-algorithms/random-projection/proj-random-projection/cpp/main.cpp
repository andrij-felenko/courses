#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <random>
#include <cmath>
#include <chrono>
#include <numeric>
#include <stdexcept>
#include <string_view>

enum class ProjectionType {
    Gaussian,
    SparseAchlioptas
};

class RandomProjector {
public:
    RandomProjector(size_t orig_dim, size_t target_dim,
                    ProjectionType type = ProjectionType::SparseAchlioptas,
                    uint64_t seed = 42)
        : orig_dim_(orig_dim), target_dim_(target_dim), type_(type) {
        
        if (orig_dim == 0 || target_dim == 0) {
            throw std::invalid_argument("Розмірності мають бути строго більшими за нуль");
        }

        matrix_.resize(orig_dim_ * target_dim_);
        generate_matrix(seed);
    }

    // Проєктування одного вектора зі span у span
    void transform(std::span<const float> input, std::span<float> output) const {
        if (input.size() != orig_dim_ || output.size() != target_dim_) {
            throw std::invalid_argument("Невідповідність розмірів вхідного або вихідного вектора");
        }

        for (size_t i = 0; i < target_dim_; ++i) {
            const float* row = &matrix_[i * orig_dim_];
            float sum = 0.0f;
            for (size_t j = 0; j < orig_dim_; ++j) {
                sum += row[j] * input[j];
            }
            output[i] = sum;
        }
    }

    // Проєктування вектора з поверненням нового std::vector
    [[nodiscard]] std::vector<float> transform(std::span<const float> input) const {
        std::vector<float> result(target_dim_);
        transform(input, result);
        return result;
    }

    [[nodiscard]] size_t original_dim() const noexcept { return orig_dim_; }
    [[nodiscard]] size_t target_dim() const noexcept { return target_dim_; }

private:
    size_t orig_dim_;
    size_t target_dim_;
    ProjectionType type_;
    std::vector<float> matrix_;

    void generate_matrix(uint64_t seed) {
        std::mt19937_64 rng(seed);
        const float scale = 1.0f / std::sqrt(static_cast<float>(target_dim_));

        if (type_ == ProjectionType::Gaussian) {
            std::normal_distribution<float> dist(0.0f, 1.0f);
            for (auto& val : matrix_) {
                val = dist(rng) * scale;
            }
        } else if (type_ == ProjectionType::SparseAchlioptas) {
            std::uniform_real_distribution<float> dist(0.0f, 1.0f);
            const float non_zero_val = std::sqrt(3.0f) * scale;

            for (auto& val : matrix_) {
                const float r = dist(rng);
                if (r < 1.0f / 6.0f) {
                    val = non_zero_val;
                } else if (r < 2.0f / 6.0f) {
                    val = -non_zero_val;
                } else {
                    val = 0.0f;
                }
            }
        }
    }
};

// Розрахунок евклідової відстані
[[nodiscard]] float euclidean_distance(std::span<const float> a, std::span<const float> b) {
    float sum = 0.0f;
    for (size_t i = 0; i < a.size(); ++i) {
        const float diff = a[i] - b[i];
        sum += diff * diff;
    }
    return std::sqrt(sum);
}

int main() {
    constexpr size_t num_points = 300;
    constexpr size_t orig_d = 2048;
    constexpr size_t target_k = 128;
    constexpr float eps = 0.20f;

    std::cout << "=== Бенчмарк випадкового проєктування (C++20) ===\n";
    std::cout << "Точок: " << num_points << ", Розмірність d: " << orig_d
              << " -> k: " << target_k << "\n\n";

    // 1. Генерація вхідних даних
    std::mt19937_64 rng(1337);
    std::normal_distribution<float> normal_dist(0.0f, 1.0f);

    std::vector<std::vector<float>> dataset(num_points, std::vector<float>(orig_d));
    for (auto& vec : dataset) {
        for (auto& val : vec) {
            val = normal_dist(rng);
        }
    }

    // 2. Ініціалізація проєктора
    RandomProjector projector(orig_d, target_k, ProjectionType::SparseAchlioptas, 42);

    // 3. Пакетне проєктування
    std::vector<std::vector<float>> projected(num_points, std::vector<float>(target_k));

    const auto start_proj = std::chrono::high_resolution_clock::now();
    for (size_t i = 0; i < num_points; ++i) {
        projector.transform(dataset[i], projected[i]);
    }
    const auto end_proj = std::chrono::high_resolution_clock::now();
    const auto proj_duration = std::chrono::duration_cast<std::chrono::microseconds>(end_proj - start_proj);

    std::cout << "Час проєктування: " << proj_duration.count() / 1000.0 << " мс ("
              << static_cast<double>(proj_duration.count()) / num_points << " мкс/вектор)\n\n";

    // 4. Оцінка точності збереження відстаней
    size_t total_pairs = num_points * (num_points - 1) / 2;
    size_t pairs_within_eps = 0;
    float max_distortion = 0.0f;
    double sum_distortion = 0.0;

    for (size_t i = 0; i < num_points; ++i) {
        for (size_t j = i + 1; j < num_points; ++j) {
            const float orig_dist = euclidean_distance(dataset[i], dataset[j]);
            const float proj_dist = euclidean_distance(projected[i], projected[j]);

            const float ratio = proj_dist / orig_dist;
            const float distortion = std::abs(ratio - 1.0f);

            max_distortion = std::max(max_distortion, distortion);
            sum_distortion += distortion;

            if (std::abs(ratio * ratio - 1.0f) <= eps) {
                ++pairs_within_eps;
            }
        }
    }

    const double mean_distortion = sum_distortion / total_pairs;
    const double success_percentage = 100.0 * pairs_within_eps / total_pairs;

    std::cout << "--- Результати перевірки леми Джонсона — Лінденштрауса ---\n";
    std::cout << "Всього попарних відстаней: " << total_pairs << "\n";
    std::cout << "Середнє відносне спотворення:  " << mean_distortion * 100.0 << "%\n";
    std::cout << "Максимальне спотворення:       " << max_distortion * 100.0 << "%\n";
    std::cout << "Пар у межах похибки (eps = " << eps << "): "
              << success_percentage << "% (" << pairs_within_eps << " / " << total_pairs << ")\n";

    return 0;
}
