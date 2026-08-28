constexpr uint64_t spread_bits3d(uint32_t v) noexcept {
    uint64_t x = v & 0x1FFFFFULL; // 21 біт
    x = (x | (x << 32)) & 0x1F00000000FFFFULL;
    x = (x | (x << 16)) & 0x1F0000FF0000FFULL;
    x = (x | (x <<  8)) & 0x100F00F00F00F0ULL;
    x = (x | (x <<  4)) & 0x10C30C30C30C30ULL;
    x = (x | (x <<  2)) & 0x12492492492492ULL;
    return x;
}

uint64_t morton_encode3d(uint32_t x, uint32_t y, uint32_t z) noexcept {
    return spread_bits3d(x) | (spread_bits3d(y) << 1) | (spread_bits3d(z) << 2);
}
