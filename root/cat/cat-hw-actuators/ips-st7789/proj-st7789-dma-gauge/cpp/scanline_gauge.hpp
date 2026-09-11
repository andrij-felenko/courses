#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>
#include "lut_trig.hpp"

/// Генератор 16-бітного кольору RGB565 у мережевому порядку байтів (Big-Endian).
/// Контролер ST7789 очікує старший байт першим, тому перестановка байтів
/// виконується на етапі ініціалізації палітри для прямої відправки через SPI DMA.
constexpr uint16_t make_rgb565_be(uint8_t r, uint8_t g, uint8_t b) noexcept {
    const uint16_t native = static_cast<uint16_t>(((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3));
    return static_cast<uint16_t>((native >> 8) | (native << 8));
}

/// Сегмент радіальної мітки циферблата для швидкого сканлайн-відсікання
struct TickSegment {
    int16_t x1, y1;
    int16_t x2, y2;
    uint16_t color;
};

/// Генерація координат 11 основних поділок кругової шкали на етапі компіляції
template <size_t NumTicks = 11>
constexpr auto generate_major_ticks() noexcept {
    std::array<TickSegment, NumTicks> ticks{};
    constexpr int start_deg = 135;
    constexpr int total_span = 270;
    constexpr int32_t R_IN = 94;
    constexpr int32_t R_OUT = 106;
    constexpr int32_t CX = 120;
    constexpr int32_t CY = 120;

    for (size_t i = 0; i < NumTicks; ++i) {
        const int deg = start_deg + static_cast<int>(i * total_span / (NumTicks - 1));
        const auto trig_val = trig::TrigLut::get(deg);

        const int16_t x1 = static_cast<int16_t>(CX + trig::TrigLut::mult_q15(R_IN, trig_val.cos_val));
        const int16_t y1 = static_cast<int16_t>(CY + trig::TrigLut::mult_q15(R_IN, trig_val.sin_val));
        const int16_t x2 = static_cast<int16_t>(CX + trig::TrigLut::mult_q15(R_OUT, trig_val.cos_val));
        const int16_t y2 = static_cast<int16_t>(CY + trig::TrigLut::mult_q15(R_OUT, trig_val.sin_val));

        // Колір мітки відповідно до функціонального сектора шкали
        uint16_t col = make_rgb565_be(240, 240, 240); // Білий сектор норми
        if (deg >= 365) {
            col = make_rgb565_be(255, 60, 60);       // Червоний сектор перевантаження
        }

        ticks[i] = TickSegment{ x1, y1, x2, y2, col };
    }
    return ticks;
}

/// Шаблонний рушій сканлайн-рендерингу кругової шкали циферблата "на льоту".
/// Не використовує динамічну пам'ять; розраховує лише один горизонтальний рядок
/// за виклик, мінімізуючи вимоги до RAM мікроконтролера до розміру двох лінійних буферів.
template <size_t Width = 240, size_t Height = 240>
class ScanlineGauge {
public:
    static constexpr int32_t CENTER_X = static_cast<int32_t>(Width / 2);
    static constexpr int32_t CENTER_Y = static_cast<int32_t>(Height / 2);

    // Геометричні радіуси елементів циферблата
    static constexpr int32_t R_BEZEL_OUT = 118;
    static constexpr int32_t R_BEZEL_IN  = 115;
    static constexpr int32_t R_ARC_OUT    = 108;
    static constexpr int32_t R_ARC_IN     = 98;
    static constexpr int32_t R_NEEDLE     = 86;
    static constexpr int32_t R_HUB_OUT    = 8;
    static constexpr int32_t R_HUB_IN     = 3;

    // Палітра кольорів інтерфейсу
    static constexpr uint16_t COL_BLACK      = make_rgb565_be(0, 0, 0);
    static constexpr uint16_t COL_DIAL_BG    = make_rgb565_be(20, 24, 30);
    static constexpr uint16_t COL_BEZEL      = make_rgb565_be(70, 80, 95);
    static constexpr uint16_t COL_ZONE_NORM  = make_rgb565_be(46, 204, 113); // Зелена зона
    static constexpr uint16_t COL_ZONE_WARN  = make_rgb565_be(241, 196, 15); // Жовта зона
    static constexpr uint16_t COL_ZONE_DANG  = make_rgb565_be(231, 76, 60);  // Червона зона
    static constexpr uint16_t COL_NEEDLE     = make_rgb565_be(255, 50, 50);  // Тіло стрілки
    static constexpr uint16_t COL_NEEDLE_TIP = make_rgb565_be(255, 230, 0);  // Акцентний кінчик
    static constexpr uint16_t COL_HUB_RING   = make_rgb565_be(190, 195, 200);// Металевий ковпачок
    static constexpr uint16_t COL_HUB_PIN    = make_rgb565_be(15, 15, 15);   // Центральна вісь

    /// Скомпільована таблиця міток шкали
    static constexpr auto MAJOR_TICKS = generate_major_ticks<11>();

    /// Підготовка кадру: розрахунок координат кінчика стрілки один раз на кадр
    void prepare_frame(int needle_angle_deg) noexcept {
        const auto trig_val = trig::TrigLut::get(needle_angle_deg);
        tip_x_ = CENTER_X + trig::TrigLut::mult_q15(R_NEEDLE, trig_val.cos_val);
        tip_y_ = CENTER_Y + trig::TrigLut::mult_q15(R_NEEDLE, trig_val.sin_val);

        needle_vec_x_ = tip_x_ - CENTER_X;
        needle_vec_y_ = tip_y_ - CENTER_Y;
        needle_len_sq_ = needle_vec_x_ * needle_vec_x_ + needle_vec_y_ * needle_vec_y_;
        if (needle_len_sq_ == 0) {
            needle_len_sq_ = 1;
        }

        needle_min_y_ = std::min(CENTER_Y, tip_y_) - 3;
        needle_max_y_ = std::max(CENTER_Y, tip_y_) + 3;
    }

    /// Попіксельний сканлайн-рендеринг рядка y безпосередньо у виділений буфер
    void render_scanline(uint16_t y, std::span<uint16_t, Width> line_buffer, int needle_angle_deg) noexcept {
        // Якщо кадр ще не підготовлено під цей кут, оновлюємо параметри
        if (cached_angle_ != needle_angle_deg) {
            prepare_frame(needle_angle_deg);
            cached_angle_ = needle_angle_deg;
        }

        const int32_t py = static_cast<int32_t>(y) - CENTER_Y;
        const int32_t py_sq = py * py;

        // 1. Базовий рендеринг циферблата, зовнішнього обідка та кольорових дуг
        for (int32_t x = 0; x < static_cast<int32_t>(Width); ++x) {
            const int32_t px = x - CENTER_X;
            const int32_t r_sq = px * px + py_sq;

            if (r_sq > R_BEZEL_OUT * R_BEZEL_OUT) {
                // Поза круглим корпусом приладу - чорне тло
                line_buffer[static_cast<size_t>(x)] = COL_BLACK;
            } else if (r_sq >= R_BEZEL_IN * R_BEZEL_IN) {
                // Зовнішній декоративний металевий обідок
                line_buffer[static_cast<size_t>(x)] = COL_BEZEL;
            } else if (r_sq >= R_ARC_IN * R_ARC_IN && r_sq <= R_ARC_OUT * R_ARC_OUT) {
                // Кольорова дуга шкали: нижній виріз 90° (між 45° і 135°) лишається темним
                const bool in_bottom_cutout = (py > 0) && (std::abs(px) < py);
                if (!in_bottom_cutout) {
                    if (px < 0) {
                        line_buffer[static_cast<size_t>(x)] = COL_ZONE_NORM;
                    } else if (py < 0) {
                        line_buffer[static_cast<size_t>(x)] = COL_ZONE_WARN;
                    } else {
                        line_buffer[static_cast<size_t>(x)] = COL_ZONE_DANG;
                    }
                } else {
                    line_buffer[static_cast<size_t>(x)] = COL_DIAL_BG;
                }
            } else {
                // Внутрішнє графітове полотно циферблата
                line_buffer[static_cast<size_t>(x)] = COL_DIAL_BG;
            }
        }

        // 2. Рендеринг основних міток шкали (лінійні відрізки)
        for (const auto& tick : MAJOR_TICKS) {
            const int16_t min_y = std::min(tick.y1, tick.y2);
            const int16_t max_y = std::max(tick.y1, tick.y2);

            if (y >= min_y && y <= max_y) {
                const int32_t dy_tick = tick.y2 - tick.y1;
                int32_t tick_x;
                if (dy_tick != 0) {
                    tick_x = tick.x1 + ((static_cast<int32_t>(y) - tick.y1) * (tick.x2 - tick.x1)) / dy_tick;
                } else {
                    tick_x = (tick.x1 + tick.x2) / 2;
                }

                if (tick_x >= 0 && tick_x < static_cast<int32_t>(Width)) {
                    line_buffer[static_cast<size_t>(tick_x)] = tick.color;
                    if (tick_x + 1 < static_cast<int32_t>(Width)) {
                        line_buffer[static_cast<size_t>(tick_x + 1)] = tick.color;
                    }
                }
            }
        }

        // 3. Рендеринг звуженої стрілки приладу
        if (static_cast<int32_t>(y) >= needle_min_y_ && static_cast<int32_t>(y) <= needle_max_y_) {
            render_needle_scanline(y, line_buffer);
        }

        // 4. Рендеринг центрального металевого ковпачка осі стрілки
        if (std::abs(py) <= R_HUB_OUT) {
            const int32_t hub_span = 8;
            const int32_t x_start = std::max(int32_t{0}, CENTER_X - hub_span);
            const int32_t x_end   = std::min(static_cast<int32_t>(Width - 1), CENTER_X + hub_span);

            for (int32_t x = x_start; x <= x_end; ++x) {
                const int32_t px = x - CENTER_X;
                const int32_t r_sq = px * px + py_sq;
                if (r_sq <= R_HUB_IN * R_HUB_IN) {
                    line_buffer[static_cast<size_t>(x)] = COL_HUB_PIN;
                } else if (r_sq <= R_HUB_OUT * R_HUB_OUT) {
                    line_buffer[static_cast<size_t>(x)] = COL_HUB_RING;
                }
            }
        }
    }

private:
    /// Швидке накладання сегмента стрілки на поточний сканлайн
    void render_needle_scanline(uint16_t y, std::span<uint16_t, Width> line_buffer) noexcept {
        const int32_t py = static_cast<int32_t>(y) - CENTER_Y;

        // Визначення орієнтовного діапазону X для перевірки пікселів стрілки
        int32_t x_start = 0;
        int32_t x_end = static_cast<int32_t>(Width - 1);

        if (std::abs(needle_vec_y_) > 2) {
            const int32_t center_x_line = CENTER_X + (py * needle_vec_x_) / needle_vec_y_;
            x_start = std::max(int32_t{0}, center_x_line - 5);
            x_end   = std::min(static_cast<int32_t>(Width - 1), center_x_line + 5);
        } else {
            x_start = std::max(int32_t{0}, std::min(CENTER_X, tip_x_) - 3);
            x_end   = std::min(static_cast<int32_t>(Width - 1), std::max(CENTER_X, tip_x_) + 3);
        }

        for (int32_t x = x_start; x <= x_end; ++x) {
            const int32_t px = x - CENTER_X;
            const int32_t dot = px * needle_vec_x_ + py * needle_vec_y_;

            if (dot >= 0 && dot <= needle_len_sq_) {
                // Квадрат перпендикулярної відстані від точки (px, py) до осі стрілки
                const int64_t dist_sq = (static_cast<int64_t>(px * px + py * py) * needle_len_sq_ -
                                         static_cast<int64_t>(dot) * dot) / needle_len_sq_;

                // Нормалізований параметр положення вздовж стрілки [0..256] (0 - корінь, 256 - кінчик)
                const int32_t t_q8 = (dot * 256) / needle_len_sq_;

                // Лінійне конічне звуження: напівтовщина 3 пікселі біля осі, 1 піксель на кінчику
                const int32_t half_w = 3 - (2 * t_q8) / 256;

                if (dist_sq <= half_w * half_w) {
                    const uint16_t col = (t_q8 > 210) ? COL_NEEDLE_TIP : COL_NEEDLE;
                    line_buffer[static_cast<size_t>(x)] = col;
                }
            }
        }
    }

    int tip_x_{CENTER_X};
    int tip_y_{CENTER_Y};
    int32_t needle_vec_x_{0};
    int32_t needle_vec_y_{0};
    int32_t needle_len_sq_{1};
    int32_t needle_min_y_{0};
    int32_t needle_max_y_{0};
    int cached_angle_{-1};
};
