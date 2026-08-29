// Інференс квантованої INT8-мережі DS-CNN над матрицею мел-ознак.
//
//   вхід 40×32×1  → conv 3×3, крок 2, 4 канали, ReLU   → 20×16×4
//                 → depthwise 3×3, крок 2, ReLU        → 10×8×4
//                 → pointwise 1×1, 4→8, ReLU           → 10×8×8
//                 → depthwise 3×3, крок 1, ReLU        → 10×8×8
//                 → pointwise 1×1, 8→8, ReLU           → 10×8×8
//                 → global average pool                → 8
//                 → fully connected 8→4                → 4 логіти
//
// Роздільна згортка (depthwise + pointwise) дає те саме, що звичайна 3×3,
// але множень у неї вдев'ятеро менше при тій самій кількості каналів —
// саме тому вона й дожила до мікроконтролерів.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

#include "acoustic/spectrum.hpp"

namespace acoustic {

inline constexpr std::size_t kNumFrames  = 40;   // 640 мс звуку
inline constexpr std::size_t kNumClasses = 4;

using FeatureMatrix = std::array<std::array<std::int8_t, kMelBins>, kNumFrames>;

// Параметри переквантування шару: множник у Q31 і правий зсув. Разом вони
// кодують дробовий масштаб M = multiplier · 2⁻³¹ · 2⁻ˢʰⁱᶠᵗ, на який множиться
// int32-акумулятор, щоб повернутися в int8.
struct Requant {
    std::int32_t multiplier;
    std::uint8_t shift;
};

// Форма карти ознак відома на етапі компіляції, тому розміри — параметри
// шаблона, а не аргументи функцій: індексна арифметика згортається в
// константи, а невідповідність шарів стає помилкою збірки, а не мовчазним
// зсувом у пам'яті.
template <typename T, std::size_t H, std::size_t W, std::size_t C>
class TensorView {
public:
    static constexpr std::size_t height   = H;
    static constexpr std::size_t width    = W;
    static constexpr std::size_t channels = C;
    static constexpr std::size_t size     = H * W * C;

    explicit constexpr TensorView(std::span<T> storage) noexcept
        : data_{storage.first(size)} {}

    [[nodiscard]] constexpr T &at(std::size_t y, std::size_t x, std::size_t c) const noexcept
    {
        return data_[(y * W + x) * C + c];
    }

    [[nodiscard]] constexpr std::span<T> flat() const noexcept { return data_; }

private:
    std::span<T> data_;
};

class Classifier {
public:
    // Розквантовані логіти чотирьох класів.
    [[nodiscard]] std::array<float, kNumClasses> operator()(const FeatureMatrix &features) noexcept;

private:
    // Дві робочі карти: більша тримає вихід першої згортки (1280 байтів),
    // менша — усе після другого кроку по часу й частоті (640). Шари
    // перекидають дані з однієї в іншу, тож третьої не треба.
    std::array<std::int8_t, 20 * 16 * 4> wide_{};
    std::array<std::int8_t, 10 * 8 * 8>  narrow_{};
};

// Вивантаження навченої моделі — model_weights.cpp.
namespace model {

extern const std::array<std::int8_t, 36> kConv1Weights;    // [oc][ky][kx]
extern const std::array<std::int32_t, 4> kConv1Bias;
extern const Requant kConv1Requant;

extern const std::array<std::int8_t, 36> kDepthwise1Weights;  // [c][ky][kx]
extern const std::array<std::int32_t, 4> kDepthwise1Bias;
extern const Requant kDepthwise1Requant;

extern const std::array<std::int8_t, 32> kPointwise1Weights;  // [oc][ic]
extern const std::array<std::int32_t, 8> kPointwise1Bias;
extern const Requant kPointwise1Requant;

extern const std::array<std::int8_t, 72> kDepthwise2Weights;
extern const std::array<std::int32_t, 8> kDepthwise2Bias;
extern const Requant kDepthwise2Requant;

extern const std::array<std::int8_t, 64> kPointwise2Weights;
extern const std::array<std::int32_t, 8> kPointwise2Bias;
extern const Requant kPointwise2Requant;

extern const std::array<std::int8_t, 32> kDenseWeights;       // [oc][i]
extern const std::array<std::int32_t, 4> kDenseBias;
extern const float kOutputScale;

}  // namespace model

}  // namespace acoustic
