// servo.hpp — імпульс RC-серво апаратним Timer1 (вивід OC1A, ніжка PB1).
//
// Формувати 1…2 мс програмою не можна: будь-яке переривання зсуне фронт
// на десятки мікросекунд, і вал смикатиметься від самого джитера.
// Порівнювач таймера ставить фронт із точністю 0.5 мкс.

#pragma once

#include <algorithm>
#include <cstdint>

namespace gimbal {

// Окремий тип, а не голий uint16_t: у сирих числах градуси й мікросекунди
// перемішуються надто легко, а ціна помилки — вал в упорі.
struct Microseconds {
    std::uint16_t value{0};
};

class RcServo {
public:
    static constexpr Microseconds kMin{1000};
    static constexpr Microseconds kMid{1500};
    static constexpr Microseconds kMax{2000};

    void begin() noexcept;

    // Значення затискається до безпечного ходу 1000…2000 мкс.
    void write(Microseconds pulse) noexcept;

private:
    static constexpr std::uint16_t kTicksPerUs = 2;      // 16 МГц / 8
    static constexpr std::uint16_t kFrameUs    = 20000;  // 50 Гц
};

}  // namespace gimbal
