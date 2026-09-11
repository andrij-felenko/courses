// ST7789.hpp — C++ клас драйвера для вбудованих систем
#pragma once

#include <cstdint>
#include <cstddef>
#include <algorithm>

class ST7789 {
public:
    static constexpr uint16_t Width  = 240;
    static constexpr uint16_t Height = 240;

    struct Interface {
        void (*set_cs)(bool level);
        void (*set_dc)(bool level);
        void (*set_res)(bool level);
        void (*set_blk)(bool level);
        void (*spi_write)(const uint8_t *data, size_t len);
        void (*delay_ms)(uint32_t ms);
    };

    explicit ST7789(const Interface &hal) noexcept
        : hal_(hal), offset_x_(0), offset_y_(0) {}

    void init() noexcept {
        hal_.set_cs(true);
        hal_.set_blk(false);

        // Апаратне скидання
        hal_.set_res(false);
        hal_.delay_ms(1);
        hal_.set_res(true);
        hal_.delay_ms(10);

        // Програмне скидання та вихід зі сну
        write_cmd(0x01); // SWRESET
        hal_.delay_ms(150);

        write_cmd(0x11); // SLPOUT
        hal_.delay_ms(120); // Пауза для виходу помп заряду на режим

        write_cmd(0x3A); // COLMOD
        write_data_byte(0x55); // 16 біт на піксель

        write_cmd(0x36); // MADCTL
        write_data_byte(0x00);

        write_cmd(0x21); // INVON — обов'язкова інверсія для IPS
        write_cmd(0x29); // DISPON
        hal_.delay_ms(20);

        fill_color(0x0000); // Очищення кадру перед увімкненням підсвічування
        hal_.set_blk(true);
    }

    void set_address_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) noexcept {
        const uint16_t xs = x0 + offset_x_;
        const uint16_t xe = x1 + offset_x_;
        const uint16_t ys = y0 + offset_y_;
        const uint16_t ye = y1 + offset_y_;

        const uint8_t col[] = {
            static_cast<uint8_t>(xs >> 8), static_cast<uint8_t>(xs & 0xFF),
            static_cast<uint8_t>(xe >> 8), static_cast<uint8_t>(xe & 0xFF)
        };
        const uint8_t row[] = {
            static_cast<uint8_t>(ys >> 8), static_cast<uint8_t>(ys & 0xFF),
            static_cast<uint8_t>(ye >> 8), static_cast<uint8_t>(ye & 0xFF)
        };

        write_cmd(0x2A); // CASET
        write_data(col, sizeof(col));

        write_cmd(0x2B); // RASET
        write_data(row, sizeof(row));

        write_cmd(0x2C); // RAMWR
    }

    void fill_color(uint16_t color) noexcept {
        set_address_window(0, 0, Width - 1, Height - 1);
        const uint8_t pixel[2] = {
            static_cast<uint8_t>(color >> 8),
            static_cast<uint8_t>(color & 0xFF)
        };

        uint8_t line_buffer[128];
        for (size_t i = 0; i < 64; ++i) {
            line_buffer[2 * i]     = pixel[0];
            line_buffer[2 * i + 1] = pixel[1];
        }

        hal_.set_dc(true);
        hal_.set_cs(false);
        const size_t total = Width * Height;
        const size_t blocks = total / 64;
        for (size_t i = 0; i < blocks; ++i) {
            hal_.spi_write(line_buffer, sizeof(line_buffer));
        }
        hal_.set_cs(true);
    }

    void draw_pixel(uint16_t x, uint16_t y, uint16_t color) noexcept {
        if (x >= Width || y >= Height) return;
        set_address_window(x, y, x, y);
        const uint8_t pixel[2] = {
            static_cast<uint8_t>(color >> 8),
            static_cast<uint8_t>(color & 0xFF)
        };
        write_data(pixel, sizeof(pixel));
    }

    void fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color) noexcept {
        if (x >= Width || y >= Height || w == 0 || h == 0) return;
        w = std::min<uint16_t>(w, Width - x);
        h = std::min<uint16_t>(h, Height - y);

        set_address_window(x, y, x + w - 1, y + h - 1);
        const uint8_t pixel[2] = {
            static_cast<uint8_t>(color >> 8),
            static_cast<uint8_t>(color & 0xFF)
        };

        hal_.set_dc(true);
        hal_.set_cs(false);
        const size_t count = static_cast<size_t>(w) * h;
        for (size_t i = 0; i < count; ++i) {
            hal_.spi_write(pixel, 2);
        }
        hal_.set_cs(true);
    }

private:
    Interface hal_;
    uint16_t offset_x_;
    uint16_t offset_y_;

    void write_cmd(uint8_t cmd) noexcept {
        hal_.set_dc(false);
        hal_.set_cs(false);
        hal_.spi_write(&cmd, 1);
        hal_.set_cs(true);
    }

    void write_data(const uint8_t *buf, size_t len) noexcept {
        hal_.set_dc(true);
        hal_.set_cs(false);
        hal_.spi_write(buf, len);
        hal_.set_cs(true);
    }

    void write_data_byte(uint8_t val) noexcept {
        write_data(&val, 1);
    }
};
