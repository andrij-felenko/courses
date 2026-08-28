#include <cstdint>
#include <optional>
#include <array>

// ── Ці дві функції реалізуєш під свою платформу (STM32 HAL, ESP-IDF, тощо) ──
// Записати один байт val у регістр reg пристрою addr. Повернути 0 при успіху.
extern int i2c_write_reg(std::uint8_t addr, std::uint8_t reg, std::uint8_t val);
// Прочитати n байтів у buf, починаючи з reg. Повернути 0 при успіху.
extern int i2c_read_regs(std::uint8_t addr, std::uint8_t reg,
                         std::uint8_t* buf, std::uint8_t n);

class Hmc5883l {
public:
    static constexpr std::uint8_t ADDR      = 0x1E;
    static constexpr std::uint8_t CONFIG_A  = 0x00;
    static constexpr std::uint8_t CONFIG_B  = 0x01;
    static constexpr std::uint8_t MODE      = 0x02;
    static constexpr std::uint8_t DATA      = 0x03;  // X(H,L) Z(H,L) Y(H,L)
    static constexpr std::uint8_t ID_A      = 0x0A;  // 'H' (0x48)
    // Підсилення для типового ±1.3 Гаус (Config B = 0x20): 1090 LSb/Gauss
    static constexpr float LSB_PER_GAUSS = 1090.0f;

    struct Axes { std::int16_t x, y, z; };

    // true, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3')
    static bool detect() {
        std::array<std::uint8_t, 3> id{};
        if (i2c_read_regs(ADDR, ID_A, id.data(), 3) != 0) return false;
        return id[0] == 'H' && id[1] == '4' && id[2] == '3';  // 0x48 0x34 0x33
    }

    static void init() {
        i2c_write_reg(ADDR, CONFIG_A, 0x70);   // 8 усереднень, 15 Гц
        i2c_write_reg(ADDR, CONFIG_B, 0x20);   // ±1.3 Гаус
        i2c_write_reg(ADDR, MODE,     0x00);   // безперервний вимір
    }

    // Три осі, або std::nullopt при переповненні / помилці шини.
    static std::optional<Axes> read_raw() {
        std::uint8_t b[6];
        if (i2c_read_regs(ADDR, DATA, b, 6) != 0) return std::nullopt;
        // Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
        Axes a;
        a.x = static_cast<std::int16_t>((b[0] << 8) | b[1]);
        a.z = static_cast<std::int16_t>((b[2] << 8) | b[3]);
        a.y = static_cast<std::int16_t>((b[4] << 8) | b[5]);
        // -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
        if (a.x == -4096 || a.y == -4096 || a.z == -4096) return std::nullopt;
        return a;
    }

    // Перевести сирий відлік у Гауси (для діагностики / нахилокомпенсації)
    static float to_gauss(std::int16_t raw) {
        return static_cast<float>(raw) / LSB_PER_GAUSS;
    }
};
