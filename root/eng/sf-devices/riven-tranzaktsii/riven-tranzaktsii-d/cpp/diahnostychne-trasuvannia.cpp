class ScopedTracePin {
public:
    ScopedTracePin()  { GPIOB->BSRR = GPIO_PIN_12; }
    ~ScopedTracePin() { GPIOB->BSRR = static_cast<uint32_t>(GPIO_PIN_12) << 16; }
};

inline auto read_with_trace(IBusAdapter& bus, uint16_t reg, std::span<uint8_t> buf) {
    ScopedTracePin trace{};
    return bus.read_reg(reg, buf);
}
