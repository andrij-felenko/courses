#include <array>
#include <algorithm>
#include <span>
#include <cmath>

class P2Quantile {
public:
    explicit P2Quantile(double target_quantile) noexcept
        : p_{target_quantile},
          dn_{0.0, target_quantile / 2.0, target_quantile, (1.0 + target_quantile) / 2.0, 1.0} {}

    void update(double x) noexcept {
        if (count_ < 5) {
            q_[count_++] = x;
            if (count_ == 5) {
                std::ranges::sort(q_);
                for (int i = 0; i < 5; ++i) {
                    n_[i] = i + 1;
                    n_prime_[i] = 1.0 + 4.0 * dn_[i];
                }
            }
            return;
        }

        int k = 0;
        if (x < q_[0]) {
            q_[0] = x;
            k = 0;
        } else if (x >= q_[4]) {
            q_[4] = x;
            k = 3;
        } else {
            for (int i = 1; i < 5; ++i) {
                if (x < q_[i]) {
                    k = i - 1;
                    break;
                }
            }
        }

        for (int i = k + 1; i < 5; ++i) {
            ++n_[i];
        }

        for (int i = 0; i < 5; ++i) {
            n_prime_[i] += dn_[i];
        }

        for (int i = 1; i <= 3; ++i) {
            const double d = n_prime_[i] - static_cast<double>(n_[i]);
            if ((d >= 1.0 && n_[i + 1] - n_[i] > 1) ||
                (d <= -1.0 && n_[i - 1] - n_[i] < -1)) {
                const int step = (d >= 0.0) ? 1 : -1;
                const double q_new = parabolic(i, step);

                if (q_[i - 1] < q_new && q_new < q_[i + 1]) {
                    q_[i] = q_new;
                } else {
                    q_[i] = linear(i, step);
                }
                n_[i] += step;
            }
        }
    }

    [[nodiscard]] double value() const noexcept {
        if (count_ == 0) return 0.0;
        if (count_ <= 5) {
            std::array<double, 5> temp = q_;
            std::sort(temp.begin(), temp.begin() + count_);
            const auto idx = static_cast<std::size_t>(p_ * (count_ - 1));
            return temp[idx];
        }
        return q_[2];
    }

    [[nodiscard]] int count() const noexcept { return count_; }

private:
    [[nodiscard]] double parabolic(int i, int d) const noexcept {
        const double q0 = q_[i - 1], q1 = q_[i], q2 = q_[i + 1];
        const int n0 = n_[i - 1], n1 = n_[i], n2 = n_[i + 1];

        const double term1 = static_cast<double>(d) / (n2 - n0);
        const double term2 = (n1 - n0 + d) * (q2 - q1) / (n2 - n1);
        const double term3 = (n2 - n1 - d) * (q1 - q0) / (n1 - n0);

        return q1 + term1 * (term2 + term3);
    }

    [[nodiscard]] double linear(int i, int d) const noexcept {
        return q_[i] + d * (q_[i + d] - q_[i]) / (n_[i + d] - n_[i]);
    }

    double p_;
    int count_{0};
    std::array<double, 5> q_{0.0, 0.0, 0.0, 0.0, 0.0};
    std::array<int, 5> n_{0, 0, 0, 0, 0};
    std::array<double, 5> n_prime_{0.0, 0.0, 0.0, 0.0, 0.0};
    std::array<double, 5> dn_{0.0, 0.0, 0.0, 0.0, 0.0};
};
