#include "gp2y0a21.hpp"
#include <algorithm>
#include <array>

// Таблиця пошуку (LUT) для далекоміра Sharp GP2Y0A21YK0F.
// Паритет значень: (АЦП 10-біт [0..1023], Відстань у см [10..80]).
// Оскільки вихідна напруга сенсора зменшується зі зростанням відстані,
// значення АЦП відсортовані за спаданням.
const LutEntry SharpGP2Y0A21::LUT[SharpGP2Y0A21::LUT_SIZE] = {
    {520, 10.0f}, // 10 см (~2.54 В)
    {390, 15.0f}, // 15 см (~1.90 В)
    {305, 20.0f}, // 20 см (~1.49 В)
    {215, 30.0f}, // 30 см (~1.05 В)
    {165, 40.0f}, // 40 см (~0.80 В)
    {135, 50.0f}, // 50 см (~0.66 В)
    {115, 60.0f}, // 60 см (~0.56 В)
    {98,  70.0f}, // 70 см (~0.48 В)
    {85,  80.0f}  // 80 см (~0.42 В)
};

SharpGP2Y0A21::SharpGP2Y0A21(IAdcChannel& adcChannel)
    : adcChannel_(adcChannel) {}

void SharpGP2Y0A21::sample() {
    uint16_t raw = adcChannel_.readRaw();
    buffer_.push(raw);
}

void SharpGP2Y0A21::addSample(uint16_t adcRaw) {
    buffer_.push(adcRaw);
}

void SharpGP2Y0A21::reset() {
    buffer_.clear();
}

bool SharpGP2Y0A21::getMedianAdc(uint16_t& outMedian) const {
    const std::size_t count = buffer_.size();
    if (count < BUFFER_SIZE) {
        return false;
    }

    std::array<uint16_t, BUFFER_SIZE> samples{};
    buffer_.copyTo(samples.data());

    // Медіанне сортування масиву вибірок
    std::sort(samples.begin(), samples.begin() + count);

    // Оскільки BUFFER_SIZE = 5, центральний елемент [2] є медіаною
    outMedian = samples[count / 2];
    return true;
}

float SharpGP2Y0A21::interpolateDistance(uint16_t adcRaw) {
    // Крайовий випадок: якщо значення АЦП більше або дорівнює максимальному (10 см)
    if (adcRaw >= LUT[0].adcValue) {
        const float t = static_cast<float>(LUT[0].adcValue - adcRaw) /
                        static_cast<float>(LUT[0].adcValue - LUT[1].adcValue);
        return LUT[0].distanceCm + t * (LUT[1].distanceCm - LUT[0].distanceCm);
    }

    // Крайовий випадок: якщо значення АЦП менше або дорівнює мінімальному (80 см)
    if (adcRaw <= LUT[LUT_SIZE - 1].adcValue) {
        const std::size_t i = LUT_SIZE - 2;
        const float t = static_cast<float>(LUT[i].adcValue - adcRaw) /
                        static_cast<float>(LUT[i].adcValue - LUT[i + 1].adcValue);
        return LUT[i].distanceCm + t * (LUT[i + 1].distanceCm - LUT[i]);
    }

    // Кусково-лінійна інтерполяція між двома сусідніми точками LUT
    for (std::size_t i = 0; i < LUT_SIZE - 1; ++i) {
        if (adcRaw <= LUT[i].adcValue && adcRaw >= LUT[i + 1].adcValue) {
            const float t = static_cast<float>(LUT[i].adcValue - adcRaw) /
                            static_cast<float>(LUT[i].adcValue - LUT[i + 1].adcValue);
            return LUT[i].distanceCm + t * (LUT[i + 1].distanceCm - LUT[i].distanceCm);
        }
    }

    return MAX_DISTANCE_CM;
}

MeasurementResult SharpGP2Y0A21::getDistance() {
    uint16_t medianAdc = 0;
    if (!getMedianAdc(medianAdc)) {
        return {0.0f, DistanceStatus::InsufficientSamples};
    }

    float distance = interpolateDistance(medianAdc);

    if (distance < MIN_DISTANCE_CM) {
        return {distance, DistanceStatus::OutOfBoundsTooClose};
    }
    if (distance > MAX_DISTANCE_CM) {
        return {distance, DistanceStatus::OutOfBoundsTooFar};
    }

    return {distance, DistanceStatus::OK};
}
