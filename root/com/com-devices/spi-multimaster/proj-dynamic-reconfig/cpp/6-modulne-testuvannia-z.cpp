// Тестовий Mock для емуляції апаратного модуля SPI
struct MockSpiRegisters {
    static constexpr uint32_t CR1_SPE     = (1u << 6);
    static constexpr uint32_t CR1_MSTR    = (1u << 2);
    static constexpr uint32_t CR1_CPOL    = (1u << 1);
    static constexpr uint32_t CR1_CPHA    = (1u << 0);
    static constexpr uint32_t CR1_LSBFIRST= (1u << 7);
    static constexpr uint32_t CR1_BR_MASK = (7u << 3);

    static constexpr uint32_t SR_TXE      = (1u << 1);
    static constexpr uint32_t SR_RXNE     = (1u << 0);
    static constexpr uint32_t SR_BSY      = (1u << 7);
    static constexpr uint32_t SR_MODF     = (1u << 5);

    uint32_t CR1{CR1_MSTR | CR1_SPE};
    uint32_t CR2{0};
    uint32_t SR{SR_TXE | SR_RXNE};
    uint32_t DR{0x00};
};

struct MockGpio {
    void writePin(uint8_t port, uint8_t pin, bool level) {
        lastPort = port;
        lastPin = pin;
        lastLevel = level;
    }
    void delayUs(uint32_t us) { totalDelayUs += us; }

    uint8_t  lastPort{0};
    uint8_t  lastPin{0};
    bool     lastLevel{true};
    uint32_t totalDelayUs{0};
};
