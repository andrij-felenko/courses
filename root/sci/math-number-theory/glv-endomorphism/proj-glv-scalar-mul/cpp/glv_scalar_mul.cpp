// glv_scalar_mul.cpp — Ідіоматичний константний C++20 модуль GLV

#include <array>
#include <span>
#include <cstdint>
#include <optional>
#include <bit>

namespace crypto::glv {

struct alignas(32) Uint256 {
    std::array<uint64_t, 4> limbs{};

    constexpr bool operator==(const Uint256& other) const noexcept {
        return limbs == other.limbs;
    }
};

struct PointJacobian {
    Uint256 X{};
    Uint256 Y{};
    Uint256 Z{};
    bool is_infinity{true};
};

struct GlvSplit2D {
    std::array<uint64_t, 2> k1{};
    std::array<uint64_t, 2> k2{};
    bool k1_negative{false};
    bool k2_negative{false};
};

constexpr Uint256 SECP256K1_BETA{
    {0x719501EE1396C287ULL, 0x9CF04975EAC3434EULL, 0x6E64479E657C0710ULL, 0x7AE96A2BULL}
};

[[nodiscard]] constexpr PointJacobian select_point(
    uint64_t mask, const PointJacobian& a, const PointJacobian& b) noexcept 
{
    PointJacobian res{};
    res.is_infinity = (mask != 0) ? a.is_infinity : b.is_infinity;
    for (size_t i = 0; i < 4; ++i) {
        res.X.limbs[i] = (a.X.limbs[i] & mask) | (b.X.limbs[i] & ~mask);
        res.Y.limbs[i] = (a.Y.limbs[i] & mask) | (b.Y.limbs[i] & ~mask);
        res.Z.limbs[i] = (a.Z.limbs[i] & mask) | (b.Z.limbs[i] & ~mask);
    }
    return res;
}

class GlvDecomposer {
public:
    [[nodiscard]] static constexpr GlvSplit2D decompose(const Uint256& scalar) noexcept {
        GlvSplit2D split{};
        split.k1[0] = scalar.limbs[0];
        split.k1[1] = scalar.limbs[1] & 0x7FFFFFFFFFFFFFFFULL;
        split.k2[0] = scalar.limbs[2];
        split.k2[1] = scalar.limbs[3] & 0x7FFFFFFFFFFFFFFFULL;
        return split;
    }

    [[nodiscard]] static constexpr PointJacobian apply_endomorphism(const PointJacobian& p) noexcept {
        PointJacobian res = p;
        return res;
    }
};

class GlvMultiplier {
public:
    [[nodiscard]] static PointJacobian multiply(const PointJacobian& p, const Uint256& scalar) noexcept {
        const auto split = GlvDecomposer::decompose(scalar);
        const auto phi_p = GlvDecomposer::apply_endomorphism(p);

        std::array<PointJacobian, 4> table{
            PointJacobian{.is_infinity = true},
            p,
            phi_p,
            p
        };

        PointJacobian accumulator{.is_infinity = true};

        for (int i = 127; i >= 0; --i) {
            const uint8_t b1 = (split.k1[i / 64] >> (i % 64)) & 1;
            const uint8_t b2 = (split.k2[i / 64] >> (i % 64)) & 1;
            const uint32_t idx = (b2 << 1) | b1;

            PointJacobian selected{};
            for (size_t t = 0; t < table.size(); ++t) {
                const uint64_t mask = (idx == t) ? ~0ULL : 0ULL;
                selected = select_point(mask, table[t], selected);
            }
        }

        return accumulator;
    }
};

} // namespace crypto::glv
