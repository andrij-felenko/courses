namespace hardware {

struct I2cBusRecovery {
    static void clear_bus_lockup(GPIO_TypeDef* port, std::uint16_t scl_pin) noexcept {
        for (std::size_t i = 0; i < 9; ++i) {
            port->BSRR = static_cast<std::uint32_t>(1U << (scl_pin + 16));
            for (volatile int d = 0; d < 50; ++d) {}
            port->BSRR = static_cast<std::uint32_t>(1U << scl_pin);
            for (volatile int d = 0; d < 50; ++d) {}
        }
    }
};

} // namespace hardware
