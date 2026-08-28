enum class NodeType : uint8_t {
    Constant      = 0x01,
    Variable      = 0x02,
    Add           = 0x10,
    Subtract      = 0x11,
    Multiply      = 0x12,
    Divide        = 0x13,
    Exponent      = 0x14,
    BoundedSum    = 0x20,
    BoundedProd   = 0x21,
    BoundedSearch = 0x22
};
