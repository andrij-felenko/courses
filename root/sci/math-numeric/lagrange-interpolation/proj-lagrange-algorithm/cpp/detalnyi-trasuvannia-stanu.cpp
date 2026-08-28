#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <stdexcept>

class BarycentricInterpolator {
public:
    explicit BarycentricInterpolator(size_t reserve_capacity = 8) {
        x_.reserve(reserve_capacity);
        y_.reserve(reserve_capacity);
        weights_.reserve(reserve_capacity);
    }

    bool add_point(double new_x, double new_y) {
        for (double existing_x : x_) {
            if (std::abs(existing_x - new_x) < 1e-12) {
                return false;
            }
        }

        const size_t n = x_.size();
        x_.push_back(new_x);
        y_.push_back(new_y);

        double new_w = 1.0;
        for (size_t k = 0; k < n; ++k) {
            double diff = x_[k] - new_x;
            weights_[k] /= diff;
            new_w /= (new_x - x_[k]);
        }
        weights_.push_back(new_w);
        return true;
    }

    [[nodiscard]] std::optional<double> eval(double target_x) const {
        if (x_.empty()) return std::nullopt;

        double num = 0.0;
        double den = 0.0;

        for (size_t k = 0; k < x_.size(); ++k) {
            double diff = target_x - x_[k];
            if (std::abs(diff) < 1e-12) {
                return y_[k];
            }
            double term = weights_[k] / diff;
            num += term * y_[k];
            den += term;
        }

        return num / den;
    }

    [[nodiscard]] size_t size() const noexcept { return x_.size(); }

private:
    std::vector<double> x_;
    std::vector<double> y_;
    std::vector<double> weights_;
};

int main() {
    BarycentricInterpolator interp;
    interp.add_point(1.0, 1.0);
    interp.add_point(2.0, 4.0);
    interp.add_point(4.0, 16.0);

    if (auto val = interp.eval(3.0)) {
        std::cout << "C++ Барицентричний P(3.0) = " << *val << "\n";
    }

    interp.add_point(5.0, 25.0);
    if (auto val = interp.eval(3.0)) {
        std::cout << "Після оновлення O(n): P(3.0) = " << *val << "\n";
    }

    return 0;
}
