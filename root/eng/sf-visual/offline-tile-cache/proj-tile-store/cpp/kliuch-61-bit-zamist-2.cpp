// b₂₃…b₀  →  0 b₂₃ 0 b₂₂ … 0 b₀   (24 біти розтягнуто на 48 позицій)
constexpr uint64_t spread24(uint32_t v)
{
    uint64_t x = v & 0xFFFFFFu;
    x = (x ^ (x << 16)) & 0x0000FFFF0000FFFFULL;
    x = (x ^ (x <<  8)) & 0x00FF00FF00FF00FFULL;
    x = (x ^ (x <<  4)) & 0x0F0F0F0F0F0F0F0FULL;
    x = (x ^ (x <<  2)) & 0x3333333333333333ULL;
    x = (x ^ (x <<  1)) & 0x5555555555555555ULL;
    return x;
}

constexpr uint64_t tile_key(uint8_t src, uint32_t z, uint32_t x, uint32_t y)
{
    return src_z(src, z) | (spread24(y) << 1) | spread24(x);
}

// x = 1011₂, y = 0110₂  →  пари (y₃x₃)(y₂x₂)(y₁x₁)(y₀x₀) = 01 10 11 01
static_assert(tile_key(0, 0, 0b1011, 0b0110) == 0b01101101, "чергування бітів");
