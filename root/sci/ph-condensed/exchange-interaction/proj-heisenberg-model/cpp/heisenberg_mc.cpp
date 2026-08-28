// heisenberg_mc.cpp — Ідіоматичний C++20 симулятор спінового гамільтоніана Гейзенберга
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <random>
#include <numeric>

struct SpinVector {
    double x{0.0}, y{0.0}, z{1.0};

    [[nodiscard]] double dot(const SpinVector& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }

    SpinVector& operator+=(const SpinVector& o) noexcept {
        x += o.x; y += o.y; z += o.z;
        return *this;
    }
};

class HeisenbergLattice {
public:
    HeisenbergLattice(std::size_t side_length, double J_exchange, double ext_field, double temperature)
        : size_(side_length), J_(J_exchange), h_(ext_field), temp_(temperature),
          rng_(std::random_device{}()), dist_01_(0.0, 1.0), spins_(side_length * side_length) 
    {
        for (auto& s : spins_) {
            s = generate_random_spin();
        }
    }

    void sweep_metropolis() {
        std::uniform_int_distribution<std::size_t> site_dist(0, spins_.size() - 1);

        for (std::size_t i = 0; i < spins_.size(); ++i) {
            std::size_t idx = site_dist(rng_);
            const auto nbrs = get_neighbors(idx);

            SpinVector nbr_sum{};
            for (auto n : nbrs) nbr_sum += spins_[n];

            const SpinVector old_s = spins_[idx];
            const SpinVector new_s = generate_random_spin();

            double dE = -J_ * (new_s.dot(nbr_sum) - old_s.dot(nbr_sum))
                        - h_ * (new_s.z - old_s.z);

            if (dE <= 0.0 || dist_01_(rng_) < std::exp(-dE / temp_)) {
                spins_[idx] = new_s;
            }
        }
    }

    struct Observables {
        double energy_per_spin;
        double magnetization;
    };

    [[nodiscard]] Observables measure() const {
        double total_energy = 0.0;
        SpinVector total_m{};

        for (std::size_t idx = 0; idx < spins_.size(); ++idx) {
            std::size_t r = idx / size_;
            std::size_t c = idx % size_;
            std::size_t south = ((r + 1) % size_) * size_ + c;
            std::size_t east  = r * size_ + ((c + 1) % size_);

            double e_pair = spins_[idx].dot(spins_[south]) + spins_[idx].dot(spins_[east]);
            total_energy -= J_ * e_pair + h_ * spins_[idx].z;
            total_m += spins_[idx];
        }

        double n = static_cast<double>(spins_.size());
        double mag_abs = std::sqrt(total_m.dot(total_m)) / n;
        return { total_energy / n, mag_abs };
    }

private:
    SpinVector generate_random_spin() {
        double z = 2.0 * dist_01_(rng_) - 1.0;
        double phi = 2.0 * M_PI * dist_01_(rng_);
        double r = std::sqrt(1.0 - z * z);
        return { r * std::cos(phi), r * std::sin(phi), z };
    }

    [[nodiscard]] std::array<std::size_t, 4> get_neighbors(std::size_t idx) const noexcept {
        std::size_t r = idx / size_;
        std::size_t c = idx % size_;
        return {
            ((r + size_ - 1) % size_) * size_ + c,
            ((r + 1) % size_) * size_ + c,
            r * size_ + ((c + 1) % size_),
            r * size_ + ((c + size_ - 1) % size_)
        };
    }

    std::size_t size_;
    double J_, h_, temp_;
    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_01_;
    std::vector<SpinVector> spins_;
};

int main() {
    constexpr std::size_t L = 16;
    HeisenbergLattice lattice(L, 1.0, 0.05, 0.8);

    std::cout << "Термалізація C++ системи...\n";
    for (int i = 0; i < 2000; ++i) lattice.sweep_metropolis();

    double sum_e = 0.0, sum_m = 0.0;
    constexpr int steps = 1000;
    for (int i = 0; i < steps; ++i) {
        lattice.sweep_metropolis();
        auto [e, m] = lattice.measure();
        sum_e += e;
        sum_m += m;
    }

    std::cout << "C++20 Результати:\n"
              << " Середня енергія на спін: " << sum_e / steps << '\n'
              << " Модуль намагніченості |M|: " << sum_m / steps << '\n';
}
