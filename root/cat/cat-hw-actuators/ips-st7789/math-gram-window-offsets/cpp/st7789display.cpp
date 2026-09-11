#include <cstdint>

class ST7789Display {
public:
    ST7789Display(uint16_t col_offset = 0, uint16_t row_offset = 0)
        : col_offset_(col_offset), row_offset_(row_offset) {}

    // Встановлення прямокутного вікна оновлення в GRAM
    void set_address_window(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2) const {
        // Трансляція логічних координат програми у фізичні адреси пам'яті
        const uint16_t xs = x1 + col_offset_;
        const uint16_t xe = x2 + col_offset_;
        const uint16_t ys = y1 + row_offset_;
        const uint16_t ye = y2 + row_offset_;

        // Встановлення меж стовпчиків (CASET)
        write_command(0x2A);
        write_data16(xs);
        write_data16(xe);

        // Встановлення меж рядків (RASET)
        write_command(0x2B);
        write_data16(ys);
        write_data16(ye);

        // Підготовка до прийому пікселів (RAMWR)
        write_command(0x2C);
    }

private:
    uint16_t col_offset_;
    uint16_t row_offset_;

    void write_command(uint8_t cmd) const;
    void write_data16(uint16_t value) const;
};
