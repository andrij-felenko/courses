#include <cstdint>
#include <array>

struct EcpPointProj {
    std::array<uint32_t, 8> X{};
    std::array<uint32_t, 8> Z{};
};

class MontgomeryLadderEngine {
public:
    static void step(EcpPointProj& r0, EcpPointProj& r1, const EcpPointProj& p, uint8_t bit) {
        uint32_t mask = static_cast<uint32_t>(-static_cast<int32_t>(bit));
        for (size_t i = 0; i < 8; ++i) {
            uint32_t diff_X = mask & (r0.X[i] ^ r1.X[i]);
            uint32_t diff_Z = mask & (r0.Z[i] ^ r1.Z[i]);
            r0.X[i] ^= diff_X; r1.X[i] ^= diff_X;
            r0.Z[i] ^= diff_Z; r1.Z[i] ^= diff_Z;
        }
    }
};
