#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <algorithm>
#include <span>
#include <optional>

class Lattice {
public:
    explicit Lattice(std::vector<std::vector<int64_t>> basis)
        : basis_(std::move(basis)),
          n_(static_cast<int>(basis_.size())),
          m_(static_cast<int>(basis_.empty() ? 0 : basis_[0].size())) {}

    [[nodiscard]] int rows() const noexcept { return n_; }
    [[nodiscard]] int cols() const noexcept { return m_; }
    [[nodiscard]] const std::vector<int64_t>& operator[](size_t i) const { return basis_[i]; }
    [[nodiscard]] std::vector<int64_t>& operator[](size_t i) { return basis_[i]; }

    void reduce(double delta = 0.75) {
        if (n_ <= 1) return;

        std::vector<std::vector<double>> b_star(n_, std::vector<double>(m_, 0.0));
        std::vector<std::vector<double>> mu(n_, std::vector<double>(n_, 0.0));
        std::vector<double> b_star_sq(n_, 0.0);

        compute_gso(b_star, mu, b_star_sq);

        int k = 1;
        while (k < n_) {
            // Розмірне редукування для сусіднього вектора
            size_reduce(k, k - 1, mu);

            // Перевірка умови Ловаса
            const double lhs = b_star_sq[k];
            const double rhs = (delta - mu[k][k - 1] * mu[k][k - 1]) * b_star_sq[k - 1];

            if (lhs < rhs) {
                // Обмін та крок назад
                std::swap(basis_[k], basis_[k - 1]);
                compute_gso(b_star, mu, b_star_sq);
                if (k > 1) {
                    k--;
                }
            } else {
                // Повне розмірне редукування для попередніх напрямків
                for (int j = k - 2; j >= 0; j--) {
                    size_reduce(k, j, mu);
                }
                k++;
            }
        }
    }

private:
    void compute_gso(std::vector<std::vector<double>>& b_star,
                     std::vector<std::vector<double>>& mu,
                     std::vector<double>& b_star_sq) const {
        for (int i = 0; i < n_; i++) {
            for (int c = 0; c < m_; c++) {
                b_star[i][c] = static_cast<double>(basis_[i][c]);
            }
            for (int j = 0; j < i; j++) {
                double dot = 0.0;
                for (int c = 0; c < m_; c++) {
                    dot += static_cast<double>(basis_[i][c]) * b_star[j][c];
                }
                mu[i][j] = dot / b_star_sq[j];
                for (int c = 0; c < m_; c++) {
                    b_star[i][c] -= mu[i][j] * b_star[j][c];
                }
            }
            mu[i][i] = 1.0;
            double norm_sq = 0.0;
            for (int c = 0; c < m_; c++) {
                norm_sq += b_star[i][c] * b_star[i][c];
            }
            b_star_sq[i] = norm_sq;
        }
    }

    void size_reduce(int k, int j, std::vector<std::vector<double>>& mu) {
        if (std::abs(mu[k][j]) > 0.5) {
            const auto q = static_cast<int64_t>(std::round(mu[k][j]));
            for (int c = 0; c < m_; c++) {
                basis_[k][c] -= q * basis_[j][c];
            }
            for (int l = 0; l < j; l++) {
                mu[k][l] -= static_cast<double>(q) * mu[j][l];
            }
            mu[k][j] -= static_cast<double>(q);
        }
    }

    std::vector<std::vector<int64_t>> basis_;
    int n_;
    int m_;
};
