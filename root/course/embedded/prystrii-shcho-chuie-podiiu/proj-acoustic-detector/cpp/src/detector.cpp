#include "acoustic/detector.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <iterator>

namespace acoustic {
namespace {

// Полюс фільтра постійної складової, 0.995 у Q15.
constexpr std::int32_t kDcPoleQ15 = 32604;

// Скільки кадрів на старті йде лише на калібрування фону (32 × 16 мс ≈ 0.5 с).
constexpr std::uint16_t kNoisePrimerFrames = 32;

// Поріг спрацювання: утричі над фоном плюс постійна добавка, яка не дає
// детектору зриватися в цілковитій тиші, коли фон падає до одиниць.
constexpr std::uint32_t kVadFactor = 3;
constexpr std::uint32_t kVadMargin = 64;

// Пауза після інференсу, щоб хвіст тієї самої події не запустив другий
// набір кадрів (16 × 16 мс ≈ 0.25 с).
constexpr std::uint16_t kRefractoryFrames = 16;

// Найімовірніший клас і його ймовірність за softmax. Це єдина операція з
// рухомою комою в усьому конвеєрі, і виконується вона раз на 40 кадрів
// (640 мс) — у кадровий бюджет 16 мс вона не входить.
[[nodiscard]] Detection classify(const std::array<float, kNumClasses> &logits) noexcept
{
    const auto best = std::max_element(logits.begin(), logits.end());

    float sum = 0.0f;
    for (const float logit : logits) {
        sum += std::exp(logit - *best);
    }

    return Detection{
        static_cast<EventClass>(std::distance(logits.begin(), best)),
        1.0f / sum   // exp(0) / sum для найбільшого логіта
    };
}

}  // namespace

std::int16_t Detector::DcBlocker::operator()(std::int16_t sample) noexcept
{
    const std::int32_t x = sample;
    const std::int32_t y = ((x - xPrev_) << 8) + ((yPrev_ * kDcPoleQ15) >> 15);

    xPrev_ = x;
    yPrev_ = y;

    return static_cast<std::int16_t>(std::clamp(y >> 8, -32768, 32767));
}

void Detector::reset() noexcept
{
    dc_.reset();
    frontend_.reset();

    for (auto &row : features_) {
        row.fill(0);
    }

    noiseFloor_     = kVadMargin;
    primerFrames_   = kNoisePrimerFrames;
    refractory_     = 0;
    framesRecorded_ = 0;
    capturing_      = false;
    pending_.reset();
}

// Середня потужність кадру. Кожен доданок стиснуто на 8 бітів, тож сума
// 256 квадратів гарантовано лишається в uint32 навіть на повній шкалі.
std::uint32_t Detector::frameEnergy(std::span<const std::int16_t, kFrameSamples> frame) noexcept
{
    std::uint32_t sum = 0;
    for (const std::int16_t sample : frame) {
        const std::int32_t value = sample;
        sum += static_cast<std::uint32_t>((value * value) >> 8);
    }
    return sum / static_cast<std::uint32_t>(frame.size());
}

void Detector::push(std::span<const std::int16_t, kFrameSamples> frame) noexcept
{
    std::array<std::int16_t, kFrameSamples> clean{};
    std::ranges::transform(frame, clean.begin(), [this](std::int16_t s) { return dc_(s); });

    const std::uint32_t energy = frameEnergy(clean);

    if (refractory_ > 0) {
        --refractory_;
        return;
    }

    if (!capturing_) {
        // Ковзне експоненційне середнє фону: (31·фон + енергія) / 32. Стала
        // часу близько півсекунди — кондиціонер чи дощ детектор «забуде»,
        // а удар на 50–200 мс поріг підняти не встигне.
        noiseFloor_ = ((noiseFloor_ * 31) + energy) >> 5;

        if (primerFrames_ > 0) {
            --primerFrames_;
            return;
        }

        if (energy <= noiseFloor_ * kVadFactor + kVadMargin) {
            return;   // тиша: ядро може засинати до наступного кадру
        }

        // Подія почалася — набираємо рівно 40 кадрів, скільки б вона не
        // тривала насправді. Хвіст і луна теж несуть ознаки класу.
        capturing_ = true;
        framesRecorded_ = 0;
    }

    frontend_.process(clean, features_[framesRecorded_]);
    ++framesRecorded_;

    if (framesRecorded_ < kNumFrames) {
        return;
    }

    pending_ = classify(classifier_(features_));

    capturing_      = false;
    framesRecorded_ = 0;
    refractory_     = kRefractoryFrames;
}

std::optional<Detection> Detector::poll() noexcept
{
    if (!pending_.has_value()) {
        return std::nullopt;
    }

    const Detection result = *pending_;
    pending_.reset();

    if (result.event == EventClass::Background) {
        return std::nullopt;   // спрацював VAD, але мережа не впізнала події
    }
    return result;
}

std::string_view name(EventClass event) noexcept
{
    using enum EventClass;

    switch (event) {
    case GlassBreak: return "скло";
    case Gunshot:    return "постріл";
    case AlarmSiren: return "сирена";
    case Background: return "фон";
    }
    return "?";
}

}  // namespace acoustic
