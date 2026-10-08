#include <cstdint>

struct DvpPolarityConfig {
    bool pclkRisingEdge{true};
    bool hrefActiveHigh{true};
    bool vsyncActiveHigh{false};
};

class DvpInterfaceManager {
public:
    explicit DvpInterfaceManager(bool (*bankWriteFn)(uint8_t, uint8_t, uint8_t))
        : m_bankWrite(bankWriteFn) {}

    bool applyPolarities(const DvpPolarityConfig& config) const {
        uint8_t regValue = 0x00;
        if (config.pclkRisingEdge)  regValue |= (1U << 4);
        if (config.hrefActiveHigh)   regValue |= (1U << 3);
        if (config.vsyncActiveHigh)  regValue |= (1U << 2);

        // Bank 0x00, Register 0x11: DVP Signal Control
        return m_bankWrite(0x00, 0x11, regValue);
    }

private:
    bool (*m_bankWrite)(uint8_t, uint8_t, uint8_t){nullptr};
};
