#include <iostream>
#include <array>
#include <vector>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <iomanip>

// Структура прямого (контраваріантного) вектора у просторі V
template <std::size_t N>
struct Vector {
    std::array<double, N> data{};

    double& operator[](std::size_t i) { return data[i]; }
    const double& operator[](std::size_t i) const { return data[i]; }
};

// Структура дуального (коваріантного) ковектора у просторі V*
template <std::size_t N>
struct Covector {
    std::array<double, N> data{};

    double& operator[](std::size_t i) { return data[i]; }
    const double& operator[](std::size_t i) const { return data[i]; }
};

// Квадратна матриця розміру N x N
template <std::size_t N>
struct Matrix {
    std::array<std::array<double, N>, N> m{};

    double& operator()(std::size_t r, std::size_t c) { return m[r][c]; }
    const double& operator()(std::size_t r, std::size_t c) const { return m[r][c]; }
};

// Дуальна пара (згортка ковектора з вектором) -> скаляр
template <std::size_t N>
double evaluate(const Covector<N>& p, const Vector<N>& v) {
    double sum = 0.0;
    for (std::size_t i = 0; i < N; ++i) {
        sum += p[i] * v[i];
    }
    return sum;
}

// Обернення матриці 2х2
Matrix<2> invert2x2(const Matrix<2>& a) {
    double det = a(0, 0) * a(1, 1) - a(0, 1) * a(1, 0);
    if (std::abs(det) < 1e-12) {
        throw std::runtime_error("Матриця вироджена: визначник близький до нуля");
    }
    Matrix<2> inv;
    inv(0, 0) =  a(1, 1) / det;
    inv(0, 1) = -a(0, 1) / det;
    inv(1, 0) = -a(1, 0) / det;
    inv(1, 1) =  a(0, 0) / det;
    return inv;
}

// Перетворення контраваріантного вектора: v' = P^(-1) * v
Vector<2> transformVector(const Vector<2>& v, const Matrix<2>& p_inv) {
    Vector<2> v_prime;
    v_prime[0] = p_inv(0, 0) * v[0] + p_inv(0, 1) * v[1];
    v_prime[1] = p_inv(1, 0) * v[0] + p_inv(1, 1) * v[1];
    return v_prime;
}

// Перетворення коваріантного ковектора: p' = p * P
Covector<2> transformCovector(const Covector<2>& p, const Matrix<2>& p_mat) {
    Covector<2> p_prime;
    p_prime[0] = p[0] * p_mat(0, 0) + p[1] * p_mat(1, 0);
    p_prime[1] = p[0] * p_mat(0, 1) + p[1] * p_mat(1, 1);
    return p_prime;
}

// Опускання індексу (вектор -> ковектор) через метрику g: p = g * v
Covector<2> lowerIndex(const Vector<2>& v, const Matrix<2>& g) {
    Covector<2> p;
    p[0] = g(0, 0) * v[0] + g(0, 1) * v[1];
    p[1] = g(1, 0) * v[0] + g(1, 1) * v[1];
    return p;
}

// Підняття індексу (ковектор -> вектор) через обернену метрику g^(-1): v = g_inv * p
Vector<2> raiseIndex(const Covector<2>& p, const Matrix<2>& g_inv) {
    Vector<2> v;
    v[0] = g_inv(0, 0) * p[0] + g_inv(0, 1) * p[1];
    v[1] = g_inv(1, 0) * p[0] + g_inv(1, 1) * p[1];
    return v;
}

int main() {
    std::cout << std::fixed << std::setprecision(4);

    // 1. Початковий вектор швидкості та ковектор цін/градієнта
    Vector<2> v{ { 2.0, 3.0 } };
    Covector<2> p{ { 4.0, -1.0 } };

    double initial_pairing = evaluate(p, v);
    std::cout << "Початкова згортка <p, v>: " << initial_pairing << " (очікувано: 4*2 + (-1)*3 = 5.0000)\n";

    // 2. Матриця переходу до нового базису (розтягнення першої осі у 2 рази)
    Matrix<2> P;
    P(0, 0) = 2.0; P(0, 1) = 0.0;
    P(1, 0) = 0.0; P(1, 1) = 1.0;

    Matrix<2> P_inv = invert2x2(P);

    // Перетворення вектора та ковектора
    Vector<2> v_prime = transformVector(v, P_inv);
    Covector<2> p_prime = transformCovector(p, P);

    std::cout << "\nПісля зміни базису (x1 розтягнуто вдвічі):\n";
    std::cout << "Вектор v' (контраваріантний, стиснувся): [" << v_prime[0] << ", " << v_prime[1] << "]\n";
    std::cout << "Ковектор p' (коваріантний, розтягнувся):  [" << p_prime[0] << ", " << p_prime[1] << "]\n";

    double transformed_pairing = evaluate(p_prime, v_prime);
    std::cout << "Нова згортка <p', v'>: " << transformed_pairing << " (інваріантність збережено!)\n";

    // 3. Метричний місток (косокутна метрика)
    Matrix<2> g;
    g(0, 0) = 2.0; g(0, 1) = 1.0;
    g(1, 0) = 1.0; g(1, 1) = 3.0;

    Matrix<2> g_inv = invert2x2(g);

    Covector<2> p_from_v = lowerIndex(v, g);
    Vector<2> v_restored = raiseIndex(p_from_v, g_inv);

    std::cout << "\nМетричний місток:\n";
    std::cout << "Опускання індексу v -> v_flat (ковектор): [" << p_from_v[0] << ", " << p_from_v[1] << "]\n";
    std::cout << "Підняття індексу v_flat -> v_sharp (відновлений вектор): [" << v_restored[0] << ", " << v_restored[1] << "]\n";

    return 0;
}
