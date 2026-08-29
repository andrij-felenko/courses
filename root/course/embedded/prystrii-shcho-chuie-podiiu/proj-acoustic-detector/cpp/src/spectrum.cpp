#include "acoustic/spectrum.hpp"

#include <algorithm>
#include <bit>

namespace acoustic {
namespace {

// Коефіцієнт преакценту 0.95 у Q15: підіймає верх спектра, який в ударному
// й мовному звуці на 6 дБ/октаву тихіший за низ.
constexpr std::int32_t kPreEmphasisQ15 = 31130;

// Зсув, що переводить log2 потужності у шкалу int8_t.
// Одиниця ознаки = чверть октави за потужністю ≈ 0.75 дБ.
constexpr std::int32_t kLogOffsetQ2 = 64;

constexpr std::int16_t sinQ15(std::size_t index) noexcept
{
    index &= (kFftSize - 1);

    if (index <= kFftSize / 4) {
        return kSinQ15Quarter[index];
    }
    if (index <= kFftSize / 2) {
        return kSinQ15Quarter[kFftSize / 2 - index];
    }
    if (index <= 3 * kFftSize / 4) {
        return static_cast<std::int16_t>(-kSinQ15Quarter[index - kFftSize / 2]);
    }
    return static_cast<std::int16_t>(-kSinQ15Quarter[kFftSize - index]);
}

constexpr std::int16_t cosQ15(std::size_t index) noexcept
{
    return sinQ15(index + kFftSize / 4);
}

// log2(v) у Q8: ціла частина — позиція старшого одиничного біта, дробова —
// лінійна апроксимація log2(1+x) ≈ x за мантисою. Похибка не перевищує
// 0.086 біта (≈ 0.26 дБ) — на порядок менша за крок квантування ознаки.
constexpr std::int32_t log2Q8(std::uint64_t value) noexcept
{
    if (value == 0) {
        return 0;
    }

    const int msb = 63 - std::countl_zero(value);
    const std::uint32_t fraction =
        (msb >= 8) ? static_cast<std::uint32_t>((value >> (msb - 8)) & 0xFFu)
                   : static_cast<std::uint32_t>((value << (8 - msb)) & 0xFFu);

    return (static_cast<std::int32_t>(msb) << 8) + static_cast<std::int32_t>(fraction);
}

constexpr std::uint32_t power(std::int16_t re, std::int16_t im) noexcept
{
    const std::int32_t r = re;
    const std::int32_t i = im;
    return static_cast<std::uint32_t>(r * r) + static_cast<std::uint32_t>(i * i);
}

}  // namespace

void fft(std::span<std::int16_t, kFftSize> re, std::span<std::int16_t, kFftSize> im) noexcept
{
    // Перестановка за оберненим порядком бітів — для 512 точок це 9 бітів.
    for (std::size_t i = 1, j = 0; i < kFftSize; ++i) {
        std::size_t bit = kFftSize >> 1;
        for (; (j & bit) != 0; bit >>= 1) {
            j ^= bit;
        }
        j |= bit;

        if (i < j) {
            std::swap(re[i], re[j]);
            std::swap(im[i], im[j]);
        }
    }

    for (std::size_t len = 2; len <= kFftSize; len <<= 1) {
        const std::size_t half = len >> 1;
        const std::size_t step = kFftSize / len;

        for (std::size_t base = 0; base < kFftSize; base += len) {
            for (std::size_t k = 0; k < half; ++k) {
                const std::size_t twiddle = k * step;
                const std::int32_t wr = cosQ15(twiddle);
                const std::int32_t wi = -static_cast<std::int32_t>(sinQ15(twiddle));

                const std::size_t a = base + k;
                const std::size_t b = a + half;

                const std::int32_t tr = (wr * re[b] - wi * im[b]) >> 15;
                const std::int32_t ti = (wr * im[b] + wi * re[b]) >> 15;
                const std::int32_t ur = re[a];
                const std::int32_t ui = im[a];

                re[a] = static_cast<std::int16_t>((ur + tr) >> 1);
                im[a] = static_cast<std::int16_t>((ui + ti) >> 1);
                re[b] = static_cast<std::int16_t>((ur - tr) >> 1);
                im[b] = static_cast<std::int16_t>((ui - ti) >> 1);
            }
        }
    }
}

void MelFrontend::process(std::span<const std::int16_t, kFrameSamples> frame,
                          std::span<std::int8_t, kMelBins> out) noexcept
{
    // 1. Преакцент і вікно; хвіст FFT добиваємо нулями.
    for (std::size_t i = 0; i < kFrameSamples; ++i) {
        std::int32_t pre = static_cast<std::int32_t>(frame[i]) -
                           ((static_cast<std::int32_t>(previous_) * kPreEmphasisQ15) >> 15);
        previous_ = frame[i];
        pre = std::clamp(pre, -32768, 32767);

        re_[i] = static_cast<std::int16_t>((pre * kHammingQ15[i]) >> 15);
        im_[i] = 0;
    }
    std::fill(re_.begin() + kFrameSamples, re_.end(), std::int16_t{0});
    std::fill(im_.begin() + kFrameSamples, im_.end(), std::int16_t{0});

    // 2. Спектр. Далі потрібна лише перша половина: сигнал дійсний,
    //    другу половину дзеркалить симетрія.
    fft(re_, im_);

    // 3. Трикутні мел-смуги по квадрату модуля.
    for (std::size_t m = 0; m < kMelBins; ++m) {
        const std::size_t low  = kMelEdges[m];
        const std::size_t peak = kMelEdges[m + 1];
        const std::size_t high = kMelEdges[m + 2];

        std::uint64_t accumulator = 0;

        for (std::size_t b = low; b < peak; ++b) {
            const auto weight = static_cast<std::uint32_t>(((b - low) << 15) / (peak - low));
            accumulator += (static_cast<std::uint64_t>(power(re_[b], im_[b])) * weight) >> 15;
        }
        for (std::size_t b = peak; b < high; ++b) {
            const auto weight = static_cast<std::uint32_t>(((high - b) << 15) / (high - peak));
            accumulator += (static_cast<std::uint64_t>(power(re_[b], im_[b])) * weight) >> 15;
        }

        // 4. Логарифм і квантування. Порожня смуга — тиша нижче молодшого
        //    біта, який лишився після поділів у FFT, — осідає на дно шкали.
        const std::int32_t quantised =
            (accumulator == 0) ? -128 : ((log2Q8(accumulator) >> 6) - kLogOffsetQ2);

        out[m] = static_cast<std::int8_t>(std::clamp(quantised, -128, 127));
    }
}

}  // namespace acoustic
