template <size_t MaxBoxes>
struct BoxSoA {
    std::array<int32_t, MaxBoxes> x1{};
    std::array<int32_t, MaxBoxes> y1{};
    std::array<int32_t, MaxBoxes> x2{};
    std::array<int32_t, MaxBoxes> y2{};
    std::array<int32_t, MaxBoxes> score{};
    std::array<int16_t, MaxBoxes> class_id{};
    uint32_t count{0};
};
