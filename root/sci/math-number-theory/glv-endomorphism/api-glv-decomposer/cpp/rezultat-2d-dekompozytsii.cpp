namespace crypto::glv {

struct Split2D {
    std::array<uint64_t, 2> k1{};           // Модуль першого скаляра k1
    std::array<uint64_t, 2> k2{};           // Модуль другого скаляра k2
    bool k1_is_negative{false};             // Прапор знака k1
    bool k2_is_negative{false};             // Прапор знака k2
};

} // namespace crypto::glv
