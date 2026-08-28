#include <array>
#include <cstdint>
#include <cmath>

// Структура для зберігання попередньо розрахованих коефіцієнтів
struct SineLUT {
    std::array<int16_t, 256> values{};

    // Конструктор виконує дискретизацію синусоїди
    constexpr SineLUT() noexcept {
        // Простий поліноміальний розрахунок або ряд Тейлора для синуса
        for (size_t i = 0; i < 256; ++i) {
            // Нормалізований кут від 0 до 2*pi у фіксованій точці
            double rad = (double(i) / 256.0) * 6.283185307179586;
            
            // Наближення Тейлора: x - x^3/6 + x^5/120 - x^7/5040
            double x = rad;
            while (x > 3.141592653589793) x -= 6.283185307179586;
            while (x < -3.141592653589793) x += 6.283185307179586;
            
            double x2 = x * x;
            double sin_approx = x * (1.0 - x2 / 6.0 * (1.0 - x2 / 20.0 * (1.0 - x2 / 42.0)));
            
            // Масштабування до діапазону int16_t [-32767, 32767]
            values[i] = static_cast<int16_t>(sin_approx * 32767.0);
        }
    }
};

// Глобальна незмінна таблиця
inline constexpr SineLUT SINE_TABLE{};

// Функція доступу з константним часом O(1)
constexpr int16_t fast_sin(uint8_t phase) noexcept {
    return SINE_TABLE.values[phase];
}
