#include "acoustic/dscnn.hpp"

#include <algorithm>

namespace acoustic {
namespace {

// Множення з насиченням і округленням, старша половина результату (Q31).
// Це те саме, що робить інструкція SMMULR на Cortex-M і що робить gemmlowp
// у tflite-micro: модель, переквантовану тут, можна прогнати там і навпаки.
constexpr std::int32_t satRoundDoublingHighMul(std::int32_t a, std::int32_t b) noexcept
{
    if (a == INT32_MIN && b == INT32_MIN) {
        return INT32_MAX;
    }

    const std::int64_t product = static_cast<std::int64_t>(a) * b;
    const std::int64_t nudge = (product >= 0) ? (1 << 30) : (1 - (1 << 30));

    return static_cast<std::int32_t>((product + nudge) / (std::int64_t{1} << 31));
}

// Правий зсув з округленням до найближчого; половини — від нуля.
constexpr std::int32_t roundingShiftRight(std::int32_t x, std::uint8_t shift) noexcept
{
    if (shift == 0) {
        return x;
    }

    const std::int32_t mask = (std::int32_t{1} << shift) - 1;
    const std::int32_t remainder = x & mask;
    const std::int32_t threshold = (mask >> 1) + ((x < 0) ? 1 : 0);

    return (x >> shift) + ((remainder > threshold) ? 1 : 0);
}

// Акумулятор int32 → активація int8 із ReLU. Нульова точка активацій нульова
// (симетричне квантування), тому ReLU — це просто нижня межа 0, а доповнення
// нулями на краях згортки не вносить зсуву: нуль у квантованій шкалі означає
// рівно нуль.
constexpr std::int8_t requantiseRelu(std::int32_t accumulator, Requant rq) noexcept
{
    const std::int32_t value =
        roundingShiftRight(satRoundDoublingHighMul(accumulator, rq.multiplier), rq.shift);
    return static_cast<std::int8_t>(std::clamp(value, 0, 127));
}

// Перший шар: звичайна згортка 3×3 з кроком 2, один вхідний канал
// (матриця ознак), доповнення нулями по краях.
template <typename Out>
void convolve3x3(const FeatureMatrix &features, Out out,
                 std::span<const std::int8_t> weights,
                 std::span<const std::int32_t> bias, Requant rq) noexcept
{
    constexpr int stride = static_cast<int>(kNumFrames / Out::height);

    for (std::size_t oy = 0; oy < Out::height; ++oy) {
        for (std::size_t ox = 0; ox < Out::width; ++ox) {
            for (std::size_t oc = 0; oc < Out::channels; ++oc) {
                std::int32_t accumulator = bias[oc];

                for (int ky = 0; ky < 3; ++ky) {
                    const int iy = static_cast<int>(oy) * stride - 1 + ky;
                    if (iy < 0 || iy >= static_cast<int>(kNumFrames)) {
                        continue;
                    }
                    for (int kx = 0; kx < 3; ++kx) {
                        const int ix = static_cast<int>(ox) * stride - 1 + kx;
                        if (ix < 0 || ix >= static_cast<int>(kMelBins)) {
                            continue;
                        }
                        accumulator += weights[oc * 9 + ky * 3 + kx] *
                                       features[static_cast<std::size_t>(iy)]
                                               [static_cast<std::size_t>(ix)];
                    }
                }

                out.at(oy, ox, oc) = requantiseRelu(accumulator, rq);
            }
        }
    }
}

// Глибинна згортка 3×3: кожен канал згортається своїм ядром і ні з ким
// не змішується. Крок виводиться зі співвідношення розмірів карт, тому
// переплутати шари неможливо — не збереться.
template <typename In, typename Out>
void depthwise3x3(In in, Out out, std::span<const std::int8_t> weights,
                  std::span<const std::int32_t> bias, Requant rq) noexcept
{
    static_assert(In::channels == Out::channels, "глибинна згортка не міняє каналів");
    constexpr int stride = static_cast<int>(In::height / Out::height);

    for (std::size_t oy = 0; oy < Out::height; ++oy) {
        for (std::size_t ox = 0; ox < Out::width; ++ox) {
            for (std::size_t c = 0; c < Out::channels; ++c) {
                std::int32_t accumulator = bias[c];

                for (int ky = 0; ky < 3; ++ky) {
                    const int iy = static_cast<int>(oy) * stride - 1 + ky;
                    if (iy < 0 || iy >= static_cast<int>(In::height)) {
                        continue;
                    }
                    for (int kx = 0; kx < 3; ++kx) {
                        const int ix = static_cast<int>(ox) * stride - 1 + kx;
                        if (ix < 0 || ix >= static_cast<int>(In::width)) {
                            continue;
                        }
                        accumulator += weights[c * 9 + ky * 3 + kx] *
                                       in.at(static_cast<std::size_t>(iy),
                                             static_cast<std::size_t>(ix), c);
                    }
                }

                out.at(oy, ox, c) = requantiseRelu(accumulator, rq);
            }
        }
    }
}

// Точкова згортка 1×1: у кожній точці карти маленьке матричне множення,
// яке й перемішує канали між собою.
template <typename In, typename Out>
void pointwise(In in, Out out, std::span<const std::int8_t> weights,
               std::span<const std::int32_t> bias, Requant rq) noexcept
{
    static_assert(In::height == Out::height && In::width == Out::width,
                  "згортка 1×1 не міняє розміру карти");

    for (std::size_t y = 0; y < Out::height; ++y) {
        for (std::size_t x = 0; x < Out::width; ++x) {
            for (std::size_t oc = 0; oc < Out::channels; ++oc) {
                std::int32_t accumulator = bias[oc];

                for (std::size_t ic = 0; ic < In::channels; ++ic) {
                    accumulator += weights[oc * In::channels + ic] * in.at(y, x, ic);
                }

                out.at(y, x, oc) = requantiseRelu(accumulator, rq);
            }
        }
    }
}

// Усереднення по всій карті: 80 точок стискаються у вектор із восьми чисел.
// Саме тут мережа перестає залежати від того, у якій частині
// 640-мілісекундного вікна стався звук.
template <typename In>
std::array<std::int8_t, In::channels> globalAveragePool(In in) noexcept
{
    constexpr std::size_t points = In::height * In::width;
    std::array<std::int8_t, In::channels> pooled{};

    for (std::size_t c = 0; c < In::channels; ++c) {
        std::int32_t sum = 0;
        for (std::size_t y = 0; y < In::height; ++y) {
            for (std::size_t x = 0; x < In::width; ++x) {
                sum += in.at(y, x, c);
            }
        }
        pooled[c] = static_cast<std::int8_t>((sum + static_cast<std::int32_t>(points) / 2) /
                                             static_cast<std::int32_t>(points));
    }
    return pooled;
}

}  // namespace

std::array<float, kNumClasses> Classifier::operator()(const FeatureMatrix &features) noexcept
{
    using Wide   = TensorView<std::int8_t, 20, 16, 4>;
    using Narrow = TensorView<std::int8_t, 10, 8, 4>;
    using Deep   = TensorView<std::int8_t, 10, 8, 8>;

    convolve3x3(features, Wide{wide_}, model::kConv1Weights, model::kConv1Bias,
                model::kConv1Requant);

    depthwise3x3(Wide{wide_}, Narrow{narrow_}, model::kDepthwise1Weights,
                 model::kDepthwise1Bias, model::kDepthwise1Requant);
    pointwise(Narrow{narrow_}, Deep{wide_}, model::kPointwise1Weights,
              model::kPointwise1Bias, model::kPointwise1Requant);

    depthwise3x3(Deep{wide_}, Deep{narrow_}, model::kDepthwise2Weights,
                 model::kDepthwise2Bias, model::kDepthwise2Requant);
    pointwise(Deep{narrow_}, Deep{wide_}, model::kPointwise2Weights,
              model::kPointwise2Bias, model::kPointwise2Requant);

    const auto pooled = globalAveragePool(Deep{wide_});

    // Останній шар лишається в int32: розквантовуємо один раз, уже логіти.
    std::array<float, kNumClasses> logits{};
    for (std::size_t oc = 0; oc < kNumClasses; ++oc) {
        std::int32_t accumulator = model::kDenseBias[oc];
        for (std::size_t i = 0; i < pooled.size(); ++i) {
            accumulator += model::kDenseWeights[oc * pooled.size() + i] * pooled[i];
        }
        logits[oc] = static_cast<float>(accumulator) * model::kOutputScale;
    }
    return logits;
}

}  // namespace acoustic
