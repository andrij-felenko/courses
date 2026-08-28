#include <cstdint>
#include <array>
#include <span>
#include <expected>

namespace koblitz {

enum class Status : int32_t {
    Ok                  = 0,
    ErrNullParam        = -1,
    ErrInvalidCurve     = -2,
    ErrPointNotOnCurve  = -3,
    ErrPointAtInfinity  = -4,
    ErrScalarOutOfRange = -5,
    ErrBufferTooSmall   = -6,
    ErrDivByZero        = -7,
    ErrSelfTestFailed   = -8
};

template <size_t M>
struct DomainParams {
    static constexpr size_t Degree = M;
    static constexpr size_t Words = (M + 63) / 64;
    uint8_t a{0};
    int8_t mu{-1};
    uint8_t h{4};
    uint64_t top_mask{0};
    std::array<uint64_t, Words> poly{};
    std::array<uint64_t, Words> r{};
};

template <size_t M>
struct Point {
    static constexpr size_t Words = (M + 63) / 64;
    std::array<uint64_t, Words> x{};
    std::array<uint64_t, Words> y{};
    bool is_infinity{true};
};

struct AlgebraicZTau {
    int64_t r0{0};
    int64_t r1{0};
};

template <size_t M>
struct PrecompTable {
    static constexpr size_t Capacity = 8;
    std::array<Point<M>, Capacity> points{};
    size_t count{0};
};

} // namespace koblitz
