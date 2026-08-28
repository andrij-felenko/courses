#pragma once
#include <cstdint>
#include <optional>
#include <vector>
#include <concepts>
#include <span>

namespace jinv {

/* Концепт простого модуля поля */
template <int64_t P>
concept ValidPrime = (P > 2) && (P % 4 == 3);

/* Шаблонний клас елемента поля F_{p^2} */
template <int64_t P>
requires ValidPrime<P>
class FieldExtension2 {
public:
    int64_t re{0};
    int64_t im{0};

    constexpr FieldExtension2() noexcept = default;
    constexpr FieldExtension2(int64_t r, int64_t i = 0) noexcept;

    [[nodiscard]] constexpr bool operator==(const FieldExtension2& o) const noexcept;
    [[nodiscard]] constexpr FieldExtension2 operator+(const FieldExtension2& o) const noexcept;
    [[nodiscard]] constexpr FieldExtension2 operator-(const FieldExtension2& o) const noexcept;
    [[nodiscard]] constexpr FieldExtension2 operator*(const FieldExtension2& o) const noexcept;
    [[nodiscard]] constexpr FieldExtension2 inv() const noexcept;
    [[nodiscard]] constexpr FieldExtension2 conj() const noexcept;
    [[nodiscard]] constexpr int64_t norm() const noexcept;
};

/* Клас короткої форми кривої Вейєрштрасса */
template <int64_t P>
class EllipticCurve {
private:
    FieldExtension2<P> m_a;
    FieldExtension2<P> m_b;

public:
    constexpr EllipticCurve(FieldExtension2<P> a, FieldExtension2<P> b) noexcept;

    [[nodiscard]] constexpr FieldExtension2<P> a() const noexcept { return m_a; }
    [[nodiscard]] constexpr FieldExtension2<P> b() const noexcept { return m_b; }

    /* Обчислення дискримінанта Delta = -16(4A^3 + 27B^2) */
    [[nodiscard]] constexpr FieldExtension2<P> discriminant() const noexcept;

    /* Обчислення j-інваріанта: повертає std::nullopt для сингулярних кривих */
    [[nodiscard]] std::optional<FieldExtension2<P>> j_invariant() const noexcept;

    /* Відновлення канонічної кривої за числовим інваріантом */
    [[nodiscard]] static EllipticCurve from_j(FieldExtension2<P> j0) noexcept;

    /* Перевірка, чи є криві твістами */
    [[nodiscard]] bool is_twist_of(const EllipticCurve& other) const noexcept;
};

/* Дослідник графа надсингулярних ізогеній */
template <int64_t P>
class IsogenyGraph {
public:
    [[nodiscard]] static std::vector<FieldExtension2<P>> get_2neighbors(FieldExtension2<P> j_vertex);
    [[nodiscard]] static size_t count_connected_component(FieldExtension2<P> start_j);
};

} // namespace jinv
