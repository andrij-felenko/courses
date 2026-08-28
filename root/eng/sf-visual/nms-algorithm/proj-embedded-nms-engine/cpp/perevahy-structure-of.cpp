struct alignas(8) BoxAoS {
    int32_t x1{0};
    int32_t y1{0};
    int32_t x2{0};
    int32_t y2{0};
    int32_t score{0};
    int16_t class_id{0};
    uint8_t flags{0};
    uint8_t padding{0};
};
