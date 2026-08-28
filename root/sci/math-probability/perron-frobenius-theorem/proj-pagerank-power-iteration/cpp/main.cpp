#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

using Matrix = std::vector<std::vector<double>>;
using Vector = std::vector<double>;

// Множення матриці на вектор
Vector multiply(const Matrix& mat, const Vector& vec) {
    size_t n = mat.size();
    Vector result(n, 0.0);
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            result[i] += mat[i][j] * vec[j];
        }
    }
    return result;
}

// Нормалізація вектора (сума компонентів дорівнює 1)
void normalize(Vector& vec) {
    double sum = 0.0;
    for (double val : vec) sum += val;
    for (double& val : vec) val /= sum;
}

// Перевірка умови зупинки (L1-норма різниці векторів)
double distance(const Vector& v1, const Vector& v2) {
    double dist = 0.0;
    for (size_t i = 0; i < v1.size(); ++i) {
        dist += std::abs(v1[i] - v2[i]);
    }
    return dist;
}

int main() {
    // Матриця суміжності графа (хто на кого посилається)
    // 0 -> 1, 2
    // 1 -> 2
    // 2 -> 0
    // 3 -> 2
    Matrix adj = {
        {0, 1, 1, 0},
        {0, 0, 1, 0},
        {1, 0, 0, 0},
        {0, 0, 1, 0}
    };
    size_t n = adj.size();

    // Побудова стохастичної матриці переходів P
    Matrix P(n, Vector(n, 0.0));
    for (size_t i = 0; i < n; ++i) {
        double out_degree = 0;
        for (size_t j = 0; j < n; ++j) out_degree += adj[i][j];
        
        for (size_t j = 0; j < n; ++j) {
            if (out_degree > 0) {
                P[j][i] = adj[i][j] / out_degree; // Зверніть увагу: транспонування для P*v
            } else {
                P[j][i] = 1.0 / n; // Обробка "висячих" вузлів
            }
        }
    }

    // Додавання фактора загасання d = 0.85
    double d = 0.85;
    Matrix GoogleMatrix(n, Vector(n, 0.0));
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            GoogleMatrix[i][j] = d * P[i][j] + (1.0 - d) / n;
        }
    }

    // Степеневий метод (Power Iteration)
    Vector v(n, 1.0 / n); // Початковий вектор (рівномірний розподіл)
    double epsilon = 1e-6; // Точність
    int iterations = 0;
    
    while (true) {
        Vector next_v = multiply(GoogleMatrix, v);
        normalize(next_v);
        
        if (distance(v, next_v) < epsilon) {
            v = next_v;
            break;
        }
        v = next_v;
        iterations++;
    }

    // Вивід результатів
    std::cout << "PageRank збігся за " << iterations << " ітерацій.\n";
    std::cout << "Стаціонарний вектор (рейтинги сторінок):\n";
    for (size_t i = 0; i < n; ++i) {
        std::cout << "Сторінка " << i << ": " 
                  << std::fixed << std::setprecision(4) << v[i] << "\n";
    }

    return 0;
}
