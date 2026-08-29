// Акустичний детектор подій для Cortex-M: контракт модуля.
//
// Детектор — звичайний об'єкт зі станом усередині, без жодної глобальної
// змінної: на чипі з двома мікрофонами (наприклад, для грубого визначення
// напрямку на джерело) заводять два незалежні примірники, і вони нічого
// між собою не ділять.
#pragma once

#include <cstdint>
#include <optional>
#include <span>
#include <string_view>

#include "acoustic/dscnn.hpp"
#include "acoustic/spectrum.hpp"

namespace acoustic {

enum class EventClass : std::uint8_t {
    Background = 0,
    GlassBreak = 1,
    Gunshot    = 2,
    AlarmSiren = 3
};

struct Detection {
    EventClass event{EventClass::Background};
    float      confidence{0.0f};
};

[[nodiscard]] std::string_view name(EventClass event) noexcept;

class Detector {
public:
    Detector() noexcept { reset(); }

    void reset() noexcept;

    // Один напівбуфер DMA — рівно kFrameSamples відліків. Довжину перевіряє
    // компілятор: span має сталу довжину, тож окремого аргументу з розміром
    // (і можливості передати не той) просто немає.
    //
    // Викликати із задачі, не з переривання: усередині і FFT, і згортка.
    void push(std::span<const std::int16_t, kFrameSamples> frame) noexcept;

    // Готовий результат, якщо він є. Поки детектор набирає кадри або поки
    // в матриці лише фон — порожньо.
    [[nodiscard]] std::optional<Detection> poll() noexcept;

private:
    // Фільтр постійної складової: y[n] = x[n] − x[n−1] + 0.995·y[n−1].
    // Мікрофонний тракт завжди має зсув нуля — від нього енергія кадру росте
    // на порожньому місці, а перший коефіцієнт спектра затуляє сусідні
    // мел-смуги. Стан тримається в Q8, інакше округлення саме створює той
    // зсув, який ми прибираємо.
    class DcBlocker {
    public:
        [[nodiscard]] std::int16_t operator()(std::int16_t sample) noexcept;
        void reset() noexcept { xPrev_ = 0; yPrev_ = 0; }

    private:
        std::int32_t xPrev_{0};
        std::int32_t yPrev_{0};
    };

    [[nodiscard]] static std::uint32_t frameEnergy(
        std::span<const std::int16_t, kFrameSamples> frame) noexcept;

    DcBlocker    dc_{};
    MelFrontend  frontend_{};
    Classifier   classifier_{};
    FeatureMatrix features_{};

    std::uint32_t noiseFloor_{0};
    std::uint16_t primerFrames_{0};   // кадри на початкове калібрування фону
    std::uint16_t refractory_{0};     // пауза після інференсу
    std::size_t   framesRecorded_{0};
    bool          capturing_{false};

    std::optional<Detection> pending_{};
};

}  // namespace acoustic
