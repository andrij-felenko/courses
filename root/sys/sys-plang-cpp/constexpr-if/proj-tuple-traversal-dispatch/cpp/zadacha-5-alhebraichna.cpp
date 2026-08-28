#include <array>
#include <iostream>
#include <type_traits>

enum class MatrixKind { Dense, Diagonal, Identity };

template<typename T, std::size_t N, MatrixKind Kind>
struct Matrix {
    static constexpr MatrixKind kind = Kind;
    static constexpr std::size_t size = N;

    // Для діагональної матриці зберігаємо лише N елементів, для щільної — N*N
    std::array<T, (Kind == MatrixKind::Dense ? N * N : (Kind == MatrixKind::Diagonal ? N : 0))> data{};
};

template<typename T, std::size_t N, MatrixKind K1, MatrixKind K2>
auto multiply_matrices(const Matrix<T, N, K1>& a, const Matrix<T, N, K2>& b) {
    if constexpr (K1 == MatrixKind::Identity) {
        // 1. Множення на одиничну матрицю зліва: повертаємо b без змін O(1)
        return b;
    } else if constexpr (K2 == MatrixKind::Identity) {
        // 2. Множення на одиничну матрицю справа: повертаємо a без змін O(1)
        return a;
    } else if constexpr (K1 == MatrixKind::Diagonal && K2 == MatrixKind::Diagonal) {
        // 3. Множення двох діагональних матриць: попарний добуток діагоналей O(N)
        Matrix<T, N, MatrixKind::Diagonal> result;
        for (std::size_t i = 0; i < N; ++i) {
            result.data[i] = a.data[i] * b.data[i];
        }
        return result;
    } else {
        // 4. Загальний випадок: стандартне кубічне множення матриць O(N³)
        Matrix<T, N, MatrixKind::Dense> result;
        for (std::size_t i = 0; i < N; ++i) {
            for (std::size_t k = 0; k < N; ++k) {
                T r = (K1 == MatrixKind::Diagonal ? (i == k ? a.data[i] : T{0}) : a.data[i * N + k]);
                if (r != T{0}) {
                    for (std::size_t j = 0; j < N; ++j) {
                        T val_b = (K2 == MatrixKind::Diagonal ? (k == j ? b.data[k] : T{0}) : b.data[k * N + j]);
                        result.data[i * N + j] += r * val_b;
                    }
                }
            }
        }
        return result;
    }
}
