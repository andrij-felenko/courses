#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <thread>
#include <chrono>

namespace msm {

constexpr size_t FIELD_WORDS = 4;

/* 256-бітне число для представлення елементів поля та скалярів */
struct FieldElement {
    std::array<uint64_t, FIELD_WORDS> d{};

    [[nodiscard]] constexpr bool is_zero() const noexcept {
        return (d[0] | d[1] | d[2] | d[3]) == 0;
    }
};

/* Афінна точка (x, y) */
struct PointAffine {
    FieldElement x{};
    FieldElement y{};
    bool is_infinity{true};

    static constexpr PointAffine infinity() noexcept {
        return PointAffine{{}, {}, true};
    }
};

/* Точка в координатах Якобі (X, Y, Z), де x = X/Z^2, y = Y/Z^3 */
struct PointJacobian {
    FieldElement X{};
    FieldElement Y{};
    FieldElement Z{};

    [[nodiscard]] bool is_infinity() const noexcept {
        return Z.is_zero();
    }

    static constexpr PointJacobian infinity() noexcept {
        return PointJacobian{{}, {}, {}};
    }
};

} // namespace msm
