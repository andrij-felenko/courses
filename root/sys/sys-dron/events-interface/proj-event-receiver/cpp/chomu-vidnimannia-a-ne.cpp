enum class Cmp { older, equal, newer };

static Cmp compare(uint16_t expected, uint16_t incoming)
{
    if (expected == incoming) {
        return Cmp::equal;
    }
    const uint16_t diff = static_cast<uint16_t>(incoming - expected);
    return diff > UINT16_MAX / 2 ? Cmp::older : Cmp::newer;
}
