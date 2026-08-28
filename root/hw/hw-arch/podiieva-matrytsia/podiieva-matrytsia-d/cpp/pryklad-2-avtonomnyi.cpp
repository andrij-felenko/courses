#include <cstdint>

namespace hal::stm32 {

enum class GeneratorSignal : uint8_t {
    ExtiLine0 = 1,
    Tim1Trgo  = 10,
    Comp1Out  = 23
};

enum class EdgePolarity : uint8_t {
    Disabled    = 0,
    RisingEdge  = 1,
    FallingEdge = 2,
    BothEdges   = 3
};

class DmaMuxController {
public:
    explicit constexpr DmaMuxController(uintptr_t base_addr) noexcept 
        : base_(base_addr) {}

    void configure_request_generator(
        uint8_t generator_index,
        GeneratorSignal signal,
        EdgePolarity polarity,
        uint8_t transfers_per_event = 1
    ) const noexcept {
        auto* rgcr = reinterpret_cast<volatile uint32_t*>(base_ + 0x100 + generator_index * 4);
        
        uint32_t val = (static_cast<uint32_t>(signal) & 0x1F) |
                       ((static_cast<uint32_t>(polarity) & 0x03) << 17) |
                       (((transfers_per_event - 1) & 0x1F) << 19) |
                       (1UL << 16); // GE: Enable
        *rgcr = val;
    }

    void map_channel_to_generator(uint8_t dma_channel, uint8_t generator_index) const noexcept {
        auto* ccr = reinterpret_cast<volatile uint32_t*>(base_ + dma_channel * 4);
        // Ідентифікатори генераторів запитів починаються з індексу 1
        uint32_t req_id = (generator_index + 1) & 0x7F;
        *ccr = req_id;
    }

private:
    uintptr_t base_;
};

} // namespace hal::stm32
