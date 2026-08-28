struct [[gnu::packed]] ImageVersion {
    uint8_t  major{0};
    uint8_t  minor{0};
    uint16_t revision{0};
    uint32_t buildNum{0};
};

struct [[gnu::packed]] ImageHeader {
    uint32_t     magic{0x96F3B83DUL};
    uint32_t     loadAddr{0};
    uint16_t     hdrSize{32};
    uint16_t     protectTlvSize{0};
    uint32_t     imgSize{0};
    uint32_t     flags{0};
    ImageVersion version{};
    uint32_t     reserved{0};
};
