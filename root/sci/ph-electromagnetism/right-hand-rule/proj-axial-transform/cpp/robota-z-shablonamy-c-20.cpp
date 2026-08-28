#include <concepts>
#include <iostream>

template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

template<Numeric T>
struct PolarVector {
    T x{}, y{}, z{};
};

template<Numeric T>
struct AxialVector {
    T x{}, y{}, z{};
};

// Векторний добуток двох полярних векторів -> повертає Аксіальний вектор
template<Numeric T>
[[nodiscard]] constexpr AxialVector<T> operator^(const PolarVector<T>& a, const PolarVector<T>& b) noexcept {
    return AxialVector<T>{
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

// Векторний добуток полярного та аксіального векторів -> повертає Полярний вектор
template<Numeric T>
[[nodiscard]] constexpr PolarVector<T> operator^(const PolarVector<T>& a, const AxialVector<T>& b) noexcept {
    return PolarVector<T>{
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}
