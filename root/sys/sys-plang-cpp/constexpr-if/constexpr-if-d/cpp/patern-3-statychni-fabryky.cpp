enum class BusWidth { Bit8, Bit16, Bit32 };

template<BusWidth Width>
class HardwareBus {
public:
    template<typename T>
    void write_data(uint32_t address, T value) {
        volatile auto* reg = reinterpret_cast<volatile uint32_t*>(address);

        if constexpr (Width == BusWidth::Bit8) {
            *reinterpret_cast<volatile uint8_t*>(reg) = static_cast<uint8_t>(value);
        } else if constexpr (Width == BusWidth::Bit16) {
            *reinterpret_cast<volatile uint16_t*>(reg) = static_cast<uint16_t>(value);
        } else {
            *reg = static_cast<uint32_t>(value);
        }
    }
};
