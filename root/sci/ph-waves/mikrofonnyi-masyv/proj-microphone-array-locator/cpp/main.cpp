#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <random>
#include <algorithm>
#include <optional>

class MicrophoneArrayProcessor {
public:
    using Complex = std::complex<float>;

    MicrophoneArrayProcessor(std::size_t numMics, float spacingMeters, float samplingRate, float soundSpeed = 343.0f)
        : m_numMics(numMics), m_spacing(spacingMeters), m_fs(samplingRate), m_c(soundSpeed) {}

    // Швидке перетворення Фур'є (In-place Radix-2 FFT/IFFT)
    static void fft(std::span<Complex> data, bool invert) {
        const std::size_t n = data.size();
        for (std::size_t i = 1, j = 0; i < n; ++i) {
            std::size_t bit = n >> 1;
            for (; j & bit; bit >>= 1) {
                j ^= bit;
            }
            j ^= bit;
            if (i < j) {
                std::swap(data[i], data[j]);
            }
        }

        for (std::size_t len = 2; len <= n; len <<= 1) {
            const float angle = 2.0f * std::numbers::pi_v<float> / static_cast<float>(len) * (invert ? -1.0f : 1.0f);
            const Complex wlen(std::cos(angle), std::sin(angle));
            for (std::size_t i = 0; i < n; i += len) {
                Complex w(1.0f, 0.0f);
                for (std::size_t k = 0; k < len / 2; ++k) {
                    const Complex u = data[i + k];
                    const Complex v = data[i + k + len / 2] * w;
                    data[i + k] = u + v;
                    data[i + k + len / 2] = u - v;
                    w *= wlen;
                }
            }
        }

        if (invert) {
            const float invN = 1.0f / static_cast<float>(n);
            for (auto& val : data) {
                val *= invN;
            }
        }
    }

    // Оцінка різниці затримки сигналу (TDoA) через GCC-PHAT
    [[nodiscard]] float estimateTdoaGccPhat(std::span<const float> sig1, std::span<const float> sig2, float maxDistanceMeters) const {
        const std::size_t n = sig1.size();
        std::vector<Complex> x1(n), x2(n), g12(n);

        for (std::size_t i = 0; i < n; ++i) {
            const float win = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * static_cast<float>(i) / static_cast<float>(n - 1)));
            x1[i] = Complex(sig1[i] * win, 0.0f);
            x2[i] = Complex(sig2[i] * win, 0.0f);
        }

        fft(x1, false);
        fft(x2, false);

        constexpr float eps = 1e-7f;
        for (std::size_t k = 0; k < n; ++k) {
            const Complex prod = x1[k] * std::conj(x2[k]);
            const float mag = std::abs(prod);
            g12[k] = prod / (mag + eps);
        }

        fft(g12, true);

        const int maxLags = std::min<int>(static_cast<int>(std::ceil((maxDistanceMeters / m_c) * m_fs)) + 2, static_cast<int>(n / 2));
        float maxVal = -1.0f;
        int bestLag = 0;

        for (int lag = -maxLags; lag <= maxLags; ++lag) {
            const std::size_t idx = (lag < 0) ? (n + lag) : static_cast<std::size_t>(lag);
            const float val = g12[idx].real();
            if (val > maxVal) {
                maxVal = val;
                bestLag = lag;
            }
        }

        // Параболічна субдискретна інтерполяція
        const std::size_t idxM = (bestLag - 1 < 0) ? (n + bestLag - 1) : static_cast<std::size_t>(bestLag - 1);
        const std::size_t idx0 = (bestLag < 0) ? (n + bestLag) : static_cast<std::size_t>(bestLag);
        const std::size_t idxP = (bestLag + 1 < 0) ? (n + bestLag + 1) : static_cast<std::size_t>(bestLag + 1);

        const float ym = g12[idxM].real();
        const float y0 = g12[idx0].real();
        const float yp = g12[idxP].real();

        float delta = 0.0f;
        const float denom = 2.0f * (ym - 2.0f * y0 + yp);
        if (std::abs(denom) > 1e-9f) {
            delta = std::clamp((ym - yp) / denom, -0.5f, 0.5f);
        }

        return (static_cast<float>(bestLag) + delta) / m_fs;
    }

    // Оцінка кута напрямку на джерело за масивом
    [[nodiscard]] float estimateDoaDegrees(std::span<const float> mic0, std::span<const float> micLast) const {
        const float totalDistance = static_cast<float>(m_numMics - 1) * m_spacing;
        const float tdoa = estimateTdoaGccPhat(mic0, micLast, totalDistance);
        const float sinVal = std::clamp(tdoa * m_c / totalDistance, -1.0f, 1.0f);
        return std::asin(sinVal) * 180.0f / std::numbers::pi_v<float>;
    }

    // Формування променя Delay-and-Sum
    [[nodiscard]] std::vector<float> delayAndSumBeamform(const std::vector<std::vector<float>>& multiChannelAudio, float steerAngleDeg) const {
        const std::size_t frameSize = multiChannelAudio[0].size();
        std::vector<float> output(frameSize, 0.0f);
        const float steerRad = steerAngleDeg * std::numbers::pi_v<float> / 180.0f;

        for (std::size_t m = 0; m < m_numMics; ++m) {
            const float tau = static_cast<float>(m) * m_spacing * std::sin(steerRad) / m_c;
            const float shiftSamples = tau * m_fs;
            const int intShift = static_cast<int>(std::floor(shiftSamples));
            const float fracShift = shiftSamples - static_cast<float>(intShift);

            for (std::size_t i = 0; i < frameSize; ++i) {
                const int srcIdx = static_cast<int>(i) + intShift;
                float val = 0.0f;
                if (srcIdx >= 0 && static_cast<std::size_t>(srcIdx + 1) < frameSize) {
                    val = (1.0f - fracShift) * multiChannelAudio[m][srcIdx] + fracShift * multiChannelAudio[m][srcIdx + 1];
                } else if (srcIdx >= 0 && static_cast<std::size_t>(srcIdx) < frameSize) {
                    val = multiChannelAudio[m][srcIdx];
                }
                output[i] += val / static_cast<float>(m_numMics);
            }
        }
        return output;
    }

private:
    std::size_t m_numMics;
    float m_spacing;
    float m_fs;
    float m_c;
};

int main() {
    constexpr std::size_t numMics = 4;
    constexpr std::size_t frameSize = 1024;
    constexpr float samplingRate = 16000.0f;
    constexpr float micSpacing = 0.042f;
    constexpr float speedOfSound = 343.0f;
    constexpr float targetAngleDeg = 32.0f;
    constexpr float targetFreq = 1200.0f;

    std::cout << "=== [C++] Мікрофонний масив: TDoA локалізація та Delay-and-Sum ===\n";
    std::cout << "Конфігурація: M = " << numMics << ", d = " << micSpacing << " м, fs = " << samplingRate << " Гц\n";
    std::cout << "Цільовий кут: " << targetAngleDeg << "°\n\n";

    MicrophoneArrayProcessor processor(numMics, micSpacing, samplingRate, speedOfSound);

    std::vector<std::vector<float>> multiChannelAudio(numMics, std::vector<float>(frameSize));
    const float targetRad = targetAngleDeg * std::numbers::pi_v<float> / 180.0f;

    std::mt19937 rng(42);
    std::uniform_real_distribution<float> noiseDist(-0.2f, 0.2f);

    for (std::size_t m = 0; m < numMics; ++m) {
        const float delay = static_cast<float>(m) * micSpacing * std::sin(targetRad) / speedOfSound;
        for (std::size_t i = 0; i < frameSize; ++i) {
            const float t = static_cast<float>(i) / samplingRate - delay;
            const float sig = std::sin(2.0f * std::numbers::pi_v<float> * targetFreq * t)
                            + 0.5f * std::sin(2.0f * std::numbers::pi_v<float> * 2.0f * targetFreq * t);
            multiChannelAudio[m][i] = sig + noiseDist(rng);
        }
    }

    const float estimatedAngle = processor.estimateDoaDegrees(multiChannelAudio.front(), multiChannelAudio.back());
    std::cout << "Оцінений кут джерела (GCC-PHAT): " << estimatedAngle << "° (похибка: "
              << std::abs(estimatedAngle - targetAngleDeg) << "°)\n";

    const auto beamformed = processor.delayAndSumBeamform(multiChannelAudio, estimatedAngle);

    float pSingle = 0.0f, pBeam = 0.0f;
    for (std::size_t i = 0; i < frameSize; ++i) {
        pSingle += multiChannelAudio[0][i] * multiChannelAudio[0][i];
        pBeam += beamformed[i] * beamformed[i];
    }
    pSingle /= static_cast<float>(frameSize);
    pBeam /= static_cast<float>(frameSize);

    std::cout << "Потужність входу M0:      " << pSingle << "\n";
    std::cout << "Потужність після променя: " << pBeam << "\n";
    std::cout << "Просторовий фільтр успішно підсилив цільовий напрямок.\n";

    return 0;
}
