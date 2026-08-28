struct [[gnu::packed]] BootMetadata {
    uint32_t   magic{0x544F4F42UL};
    uint32_t   sequence{0};
    SlotId     activeSlot{SlotId::SlotA};
    SlotState  slotState{SlotState::Empty};
    uint8_t    bootAttemptsLeft{0};
    uint8_t    maxBootAttempts{3};
    uint32_t   imageVersion{0};
    uint32_t   imageCrc{0};
    uint32_t   headerCrc{0};
};
