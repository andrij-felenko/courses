#include <iostream>
#include <vector>
#include <cstddef>
#include <chrono>
#include <cmath>

// ============================================================================
// 1. Базовий клас CRTP для всіх виразів (Static Polymorphism Interface)
// ============================================================================
template <typename Derived>
struct VecExpr {
    // Делегування виклику operator[] до статичного типу похідного класу
    [[nodiscard]] decltype(auto) operator[](std::size_t i) const {
        return static_cast<const Derived&>(*this)[i];
    }

    // Повертає розмір виміру
    [[nodiscard]] std::size_t size() const {
        return static_cast<const Derived&>(*this).size();
    }
};

// ============================================================================
// 2. Конкретний контейнер векторів з власним буфером пам'яті
// ============================================================================
class Vector : public VecExpr<Vector> {
private:
    std::vector<double> data_;

public:
    explicit Vector(std::size_t size, double val = 0.0) : data_(size, val) {}

    // Конструктор ініціалізації з довільного шаблону виразу
    template <typename E>
    Vector(const VecExpr<E>& expr) : data_(expr.size()) {
        *this = expr;
    }

    // Оператор присвоєння від шаблону виразу — ДРАЙВЕР ОБЧИСЛЕННЯ ВЕСЬОГО ДЕРЕВА
    template <typename E>
    Vector& operator=(const VecExpr<E>& expr) {
        const E& e = static_cast<const E&>(expr);
        const std::size_t n = e.size();
        
        if (data_.size() != n) {
            data_.resize(n);
        }
        
        // Єдиний цикл, у якому компілятор інлайнить усе дерево виразу!
        for (std::size_t i = 0; i < n; ++i) {
            data_[i] = e[i];
        }
        return *this;
    }

    [[nodiscard]] double operator[](std::size_t i) const { return data_[i]; }
    [[nodiscard]] double& operator[](std::size_t i) { return data_[i]; }
    [[nodiscard]] std::size_t size() const { return data_.size(); }
};

// ============================================================================
// 3. Вузол бінарного додавання: VecAdd<LHS, RHS>
// ============================================================================
template <typename LHS, typename RHS>
class VecAdd : public VecExpr<VecAdd<LHS, RHS>> {
private:
    const LHS& lhs_;
    const RHS& rhs_;

public:
    VecAdd(const LHS& lhs, const RHS& rhs) : lhs_(lhs), rhs_(rhs) {}

    [[nodiscard]] double operator[](std::size_t i) const {
        return lhs_[i] + rhs_[i];
    }

    [[nodiscard]] std::size_t size() const {
        return lhs_.size();
    }
};

// ============================================================================
// 4. Вузол скалярного множення: VecScale<E>
// ============================================================================
template <typename E>
class VecScale : public VecExpr<VecScale<E>> {
private:
    const E& expr_;
    double alpha_;

public:
    VecScale(const E& expr, double alpha) : expr_(expr), alpha_(alpha) {}

    [[nodiscard]] double operator[](std::size_t i) const {
        return expr_[i] * alpha_;
    }

    [[nodiscard]] std::size_t size() const {
        return expr_.size();
    }
};

// ============================================================================
// 5. Оператори-генератори AST вузлів
// ============================================================================
template <typename LHS, typename RHS>
VecAdd<LHS, RHS> operator+(const VecExpr<LHS>& lhs, const VecExpr<RHS>& rhs) {
    return VecAdd<LHS, RHS>(static_cast<const LHS&>(lhs), static_cast<const RHS&>(rhs));
}

template <typename E>
VecScale<E> operator*(const VecExpr<E>& expr, double alpha) {
    return VecScale<E>(static_cast<const E&>(expr), alpha);
}

template <typename E>
VecScale<E> operator*(double alpha, const VecExpr<E>& expr) {
    return VecScale<E>(static_cast<const E&>(expr), alpha);
}

int main() {
    constexpr std::size_t N = 10'000'000;
    Vector A(N, 1.0);
    Vector B(N, 2.0);
    Vector C(N, 3.0);
    Vector R(N, 0.0);

    auto start = std::chrono::high_resolution_clock::now();

    // Синтаксис вищого рівня: створює дерево типів VecAdd<VecAdd<Vector, VecScale<Vector>>, Vector>
    // ЖОДНОЇ алокації буфера під час обчислення!
    R = A + B * 2.5 + C;

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> ms = end - start;

    std::cout << "R[0] = " << R[0] << " (очікується 9.0)\n";
    std::cout << "Час виконання (C++ Expression Templates): " << ms.count() << " ms\n";
    return 0;
}
