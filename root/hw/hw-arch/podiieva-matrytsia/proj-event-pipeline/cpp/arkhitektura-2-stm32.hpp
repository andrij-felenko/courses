#include <cstdint>
#include <cstddef>

namespace hal::stm32 {

enum class TriggerSource : uint8_t {
    Tim2Trgo = 0x0B,
    Tim3Trgo = 0x0E,
    ExtiLine11 = 0x06
};

enum class TriggerEdge : uint8_t {
    Disabled = 0x00,
    RisingEdge = 0x01,
    FallingEdge = 0x02,
    BothEdges = 0x03
};

struct DmaMuxConfig {
    uint8_t dma_request_id;
    bool enable_sync;
    TriggerSource sync_trigger;
    TriggerEdge sync_edge;
};

class HardwarePipelineBuilder {
public:
    static void configure_timer_master(uintptr_t tim_base, uint32_t delay_ticks) noexcept {
        auto* tim = reinterpret_cast<volatile uint32_t*>(tim_base);
        // CR2 (зсув 0x04): встановлюємо MMS = 0b100 (Compare pulse)
        tim[1] = (tim[1] & ~(0x7UL << 4)) | (0x4UL << 4);
        // CCR1 (зсув 0x34): записуємо затримку
        tim[13] = delay_ticks;
    }

    static void configure_adc_external_trigger(
        uintptr_t adc_base,
        TriggerSource trigger,
        TriggerEdge edge
    ) noexcept {
        auto* cfgr = reinterpret_cast<volatile uint32_t*>(adc_base + 0x0C);
        uint32_t val = *cfgr;
        val &= ~((0x3UL << 10) | (0x1FUL << 5));
        val |= (static_cast<uint32_t>(edge) << 10);
        val |= (static_cast<uint32_t>(trigger) << 5);
        val |= (1UL << 0); // DMAEN
        *cfgr = val;
    }

    static void route_dmamux(uintptr_t dmamux_base, uint8_t channel, uint8_t request_source) noexcept {
        auto* ccr = reinterpret_cast<volatile uint32_t*>(dmamux_base + channel * 4);
        *ccr = (request_source & 0x7FUL);
    }
};

} // namespace hal::stm32
