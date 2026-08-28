#include <array>
#include <cstdint>
#include <cstddef>
#include <expected>
#include <span >

namespace crypto::pairing {

enum class ErrorCode : std::uint8_t {
    Success = 0,
    InvalidPoint,
    NotInGroup,
    BufferTooSmall,
    VerificationFailed,
    NullPointer
};

// Елемент базового поля F_p (48 байт) у стилі C++20
struct alignas(64) Fp {
    std::array<std::uint64_t, 6> limbs{};
};

// Елемент розширення F_{p^2}
struct alignas(64) Fp2 {
    Fp c0{};
    Fp c1{};
};

// Елемент цільової групи Gt (F_{p^{12}}, 576 байт)
struct alignas(64) Fp12 {
    std::array<Fp2, 3> c0{};
    std::array<Fp2, 3> c1{};
};

// Точка групи G1 в афінних координатах
struct G1Affine {
    Fp x{};
    Fp y{};
    bool infinity{false};
};

// Точка групи G2 в афінних координатах
struct G2Affine {
    Fp2 x{};
    Fp2 y{};
    bool infinity{false};
};

} // namespace crypto::pairing
