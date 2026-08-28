#include <cstddef>
#include <array>
#include <iostream>
#include <type_traits>

template<typename T, std::size_t Rows, std::size_t Cols>
class FixedMatrix {
public:
    static_assert(Rows > 0 && Cols > 0, "Розміри матриці повинні бути більшими за 0!");

    // Конструктор із 2D-масиву посилань
    constexpr explicit FixedMatrix(const T (&arr)[Rows][Cols]) {
        for (std::size_t r = 0; r < Rows; ++r) {
            for (std::size_t c = 0; c < Cols; ++c) {
                m_data[r * Cols + c] = arr[r][c];
            }
        }
    }

    [[nodiscard]] constexpr std::size_t rows() const noexcept { return Rows; }
    [[nodiscard]] constexpr std::size_t cols() const noexcept { return Cols; }

    [[nodiscard]] constexpr const T& at(std::size_t r, std::size_t c) const {
        return m_data[r * Cols + c];
    }

    void print() const {
        for (std::size_t r = 0; r < Rows; ++r) {
            std::cout << "[ ";
            for (std::size_t c = 0; c < Cols; ++c) {
                std::cout << at(r, c) << ' ';
            }
            std::cout << "]\n";
        }
    }

private:
    std::array<T, Rows * Cols> m_data{};
};

// Керівне правило виведення для 2D-масивів
template<typename T, std::size_t Rows, std::size_t Cols>
FixedMatrix(const T (&)[Rows][Cols]) -> FixedMatrix<std::decay_t<T>, Rows, Cols>;
