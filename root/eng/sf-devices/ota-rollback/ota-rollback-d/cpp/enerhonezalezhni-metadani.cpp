#include <cstdint>

namespace bootloader {

enum class SlotId : uint8_t {
    SlotA = 0,
    SlotB = 1,
    None  = 0xFF
};

enum class SlotState : uint8_t {
    Empty        = 0xFF,
    Unvalidated  = 0x01,
    Valid        = 0x02,
    MarkedBad    = 0x03
};

struct [[gnu::packed]] BootMetadata {
    uint32_t  magic{0x544F4F42UL};
    uint32_t  sequenceNumber{0};
    SlotId    activeSlot{SlotId::SlotA};
    SlotState slotState{SlotState::Empty};
    uint8_t   bootAttemptsLeft{0};
    uint8_t   maxBootAttempts{3};
    uint32_t  imageVersion{0};
    uint32_t  imageCrc{0};
    uint32_t  headerCrc{0};
};

} // namespace bootloader
