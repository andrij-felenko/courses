class Qmc5883l {
public:
    static constexpr std::uint8_t ADDR    = 0x0D;
    static constexpr std::uint8_t DATA    = 0x00;  // X(L,H) Y(L,H) Z(L,H) — LSB першим
    static constexpr std::uint8_t STATUS  = 0x06;  // біт0=DRDY, біт1=OVL
    static constexpr std::uint8_t CONFIG1 = 0x09;
    static constexpr std::uint8_t RESET   = 0x0B;
    // ±2 Гаус → 12000 LSb/Gauss; ±8 Гаус → 3000 LSb/Gauss (datasheet QST)
    static constexpr float LSB_PER_GAUSS = 12000.0f;

    struct Axes { std::int16_t x, y, z; };

    static void init() {
        i2c_write_reg(ADDR, 0x0A, 0x80);    // м'яке скидання
        // (у власному HAL тут коротка пауза ~5 мс)
        i2c_write_reg(ADDR, RESET, 0x01);   // SET/RESET Period — ОБОВ'ЯЗКОВО
        i2c_write_reg(ADDR, CONFIG1, 0x1D); // 512x, ±2G, 200Гц, безперервний
    }

    static std::optional<Axes> read_raw() {
        std::uint8_t st;
        if (i2c_read_regs(ADDR, STATUS, &st, 1) != 0) return std::nullopt;
        if (!(st & 0x01)) return std::nullopt;  // DRDY=0 → нових даних ще немає
        std::uint8_t b[6];
        if (i2c_read_regs(ADDR, DATA, b, 6) != 0) return std::nullopt;
        // little-endian: молодший байт першим
        Axes a;
        a.x = static_cast<std::int16_t>((b[1] << 8) | b[0]);
        a.y = static_cast<std::int16_t>((b[3] << 8) | b[2]);
        a.z = static_cast<std::int16_t>((b[5] << 8) | b[4]);
        if (st & 0x02) return std::nullopt;     // OVL=1 → переповнення діапазону
        return a;
    }
};
