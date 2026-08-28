namespace hal::stm32 {

template <uintptr_t PortBase, uint8_t PinIndex>
requires (PinIndex <= 15)
struct StaticGpioPin {
    static inline auto* const Port = reinterpret_cast<GpioRegisters*>(PortBase);

    static Status set_level(PinLevel lvl) noexcept {
        if (lvl == PinLevel::High) {
            Port->BSRR = (1U << PinIndex);
        } else {
            Port->BSRR = (1U << (PinIndex + 16));
        }
        return Status::Ok;
    }
};

} // namespace hal::stm32
