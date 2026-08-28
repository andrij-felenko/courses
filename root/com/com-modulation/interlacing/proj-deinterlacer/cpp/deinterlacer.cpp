// deinterlacer.cpp — адаптивний деінтерлейсер на C++
#include <vector>
#include <cmath>
#include <cstdint>
#include <algorithm>
#include <span>
#include <iostream>

class MotionAdaptiveDeinterlacer {
public:
    static constexpr size_t Width = 640;
    static constexpr size_t Height = 480;
    static constexpr uint8_t MotionThreshold = 15;

    // Обробка поля та побудова прогресивного кадру через std::span (без виділення пам'яті)
    static void process(std::span<const uint8_t> currField,
                        std::span<const uint8_t> prevSameField,
                        bool isOddField,
                        std::span<uint8_t> outFrame) {
        for (size_t y = 0; y < Height; ++y) {
            const bool lineBelongsToField = ((y % 2 == 0) == isOddField);

            for (size_t x = 0; x < Width; ++x) {
                const size_t idx = y * Width + x;

                if (lineBelongsToField) {
                    outFrame[idx] = currField[idx];
                } else {
                    const int diff = std::abs(static_cast<int>(currField[idx]) -
                                              static_cast<int>(prevSameField[idx]));

                    if (diff < MotionThreshold) {
                        // Weave: відновлення зі статичного поля
                        outFrame[idx] = currField[idx];
                    } else {
                        // Bob: інтерполяція за сусідніми непарними/парними рядками
                        const size_t topY = (y > 0) ? (y - 1) : 0;
                        const size_t botY = (y < Height - 1) ? (y + 1) : (Height - 1);
                        const uint16_t avg = (static_cast<uint16_t>(currField[topY * Width + x]) +
                                              static_cast<uint16_t>(currField[botY * Width + x])) / 2;
                        outFrame[idx] = static_cast<uint8_t>(avg);
                    }
                }
            }
        }
    }
};
