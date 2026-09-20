#include <cstdint>

class ShiftRegister74HC165 {
public:
    uint8_t read_config_byte() const noexcept {
        uint8_t raw_data = 0;

        // Строб завантаження PL
        set_pl(false);
        delay_us(1);
        set_pl(true);

        // Попослідовне вичитування бітів
        for (uint8_t i = 0; i < 8; ++i) {
            raw_data = static_cast<uint8_t>((raw_data << 1) | (read_q7() ? 1U : 0U));
            set_clk(true);
            delay_us(1);
            set_clk(false);
        }

        return static_cast<uint8_t>(~raw_data);
    }
private:
    void set_pl(bool state) const noexcept;
    void set_clk(bool state) const noexcept;
    bool read_q7() const noexcept;
    void delay_us(uint32_t us) const noexcept;
};
