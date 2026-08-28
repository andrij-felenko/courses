constexpr unsigned PRN_MOD = 16384;

// Класичний лінійний конгруентний генератор із «man 3 rand».
static unsigned prn(unsigned seed)
{
    seed = seed * 1103515245u + 12345u;
    return (seed / 65536u) % PRN_MOD;
}

static unsigned isqrt(unsigned v)
{
    if (v == 0) return 0;
    unsigned x = v, y = (x + 1) / 2;
    while (y < x) { x = y; y = (x + v / x) / 2; }
    return x;
}

// ranked — непропущені кандидати в порядку спадання балу.
static int pick_after_skip(const std::vector<int>& ranked)
{
    if (ranked.empty()) return -1;      // перевіряти нема чого
    const unsigned n = static_cast<unsigned>(ranked.size());
    const unsigned r = prn(n);
    // дві частки, кожна менша за одиницю: індекс тягне до початку списку,
    // але хвіст лишається — інколи стрибаємо далеко
    const unsigned index = static_cast<unsigned>(
        static_cast<std::uint64_t>(n) * r / PRN_MOD * isqrt(r) / isqrt(PRN_MOD));
    return ranked[std::min(index, n - 1)];
}
