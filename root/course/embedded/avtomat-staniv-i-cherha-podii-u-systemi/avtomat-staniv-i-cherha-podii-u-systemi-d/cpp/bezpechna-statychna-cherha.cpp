enum class Signal : uint16_t;

struct Event {
    Signal   sig{};
    uint16_t len{0};
    union Param {
        uint32_t u32;
        int32_t  i32;
        void*    ptr;
        uint8_t  raw[8];
    } param{};
};
