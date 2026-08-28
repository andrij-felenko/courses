namespace Health {

struct FramDriver {
    std::function<void(bool)> spi_select{};
    std::function<void(std::span<const uint8_t>)> spi_transmit{};

    void write_entry(uint32_t address, const BlackboxEntry& entry) const noexcept {
        if (!spi_select || !spi_transmit) return;

        const uint8_t wren = 0x06;
        spi_select(true);
        spi_transmit(std::span<const uint8_t>(&wren, 1));
        spi_select(false);

        const std::array<uint8_t, 4> cmd_hdr{
            0x02,
            static_cast<uint8_t>((address >> 16) & 0xFF),
            static_cast<uint8_t>((address >> 8) & 0xFF),
            static_cast<uint8_t>(address & 0xFF)
        };

        spi_select(true);
        spi_transmit(cmd_hdr);
        spi_transmit(std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&entry), sizeof(BlackboxEntry)));
        spi_select(false);
    }
};

} // namespace Health
