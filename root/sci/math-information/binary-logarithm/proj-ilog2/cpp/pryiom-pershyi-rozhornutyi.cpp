// ⌊log₂n⌋ для n > 0 — двійковий пошук по позиції старшого біта
constexpr int floor_log2_unrolled(std::uint64_t n) {
    int k = 0;
    if (n >= std::uint64_t{1} << 32) { n >>= 32; k += 32; }
    if (n >= std::uint64_t{1} << 16) { n >>= 16; k += 16; }
    if (n >= std::uint64_t{1} <<  8) { n >>=  8; k +=  8; }
    if (n >= std::uint64_t{1} <<  4) { n >>=  4; k +=  4; }
    if (n >= std::uint64_t{1} <<  2) { n >>=  2; k +=  2; }
    if (n >= std::uint64_t{1} <<  1) {           k +=  1; }
    return k;
}
