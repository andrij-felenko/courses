#include <vector>
#include <numeric>
#include <cmath>
#include <span>
#include <random>
#include <algorithm>
#include <iostream>

struct Point {
    double x = 0.0;
    double y = 0.0;

    [[nodiscard]] double distance_to(const Point& other) const noexcept {
        const double dx = x - other.x;
        const double dy = y - other.y;
        return std::sqrt(dx * dx + dy * dy);
    }
};

struct SimulatedAnnealingConfig {
    double initial_temp = 1000.0;
    double min_temp = 1e-4;
    double alpha = 0.96;
    std::size_t epoch_length = 5000;
};

class TspSolver {
public:
    explicit TspSolver(std::vector<Point> cities)
        : cities_(std::move(cities)) {}

    [[nodiscard]] double calculate_tour_distance(std::span<const std::size_t> tour) const noexcept {
        double total = 0.0;
        const std::size_t n = tour.size();
        for (std::size_t i = 0; i < n; ++i) {
            const std::size_t next = (i + 1 == n) ? 0 : i + 1;
            total += cities_[tour[i]].distance_to(cities_[tour[next]]);
        }
        return total;
    }

    [[nodiscard]] std::pair<std::vector<std::size_t>, double> solve(
        const SimulatedAnnealingConfig& config,
        std::uint64_t seed = 42) const {
        
        const std::size_t n = cities_.size();
        if (n < 2) {
            std::vector<std::size_t> trivial(n);
            std::iota(trivial.begin(), trivial.end(), 0);
            return {trivial, 0.0};
        }

        std::vector<std::size_t> current_tour(n);
        std::iota(current_tour.begin(), current_tour.end(), 0);

        std::vector<std::size_t> best_tour = current_tour;
        double current_energy = calculate_tour_distance(current_tour);
        double best_energy = current_energy;

        std::mt19937_64 rng(seed);
        std::uniform_int_distribution<std::size_t> index_dist(0, n - 1);
        std::uniform_real_distribution<double> uniform_dist(0.0, 1.0);

        double temp = config.initial_temp;

        while (temp > config.min_temp) {
            for (std::size_t step = 0; step < config.epoch_length; ++step) {
                std::size_t idx1 = index_dist(rng);
                std::size_t idx2 = index_dist(rng);
                if (idx1 == idx2) continue;

                std::size_t i = std::min(idx1, idx2);
                std::size_t j = std::max(idx1, idx2);
                if (i == 0 && j == n - 1) continue;

                const std::size_t u = current_tour[i];
                const std::size_t v = current_tour[i + 1];
                const std::size_t w = current_tour[j];
                const std::size_t z = current_tour[(j + 1 == n) ? 0 : j + 1];

                // Інкрементний перерахунок довжини туру за O(1)
                const double d_old = cities_[u].distance_to(cities_[v]) +
                                     cities_[w].distance_to(cities_[z]);
                const double d_new = cities_[u].distance_to(cities_[w]) +
                                     cities_[v].distance_to(cities_[z]);
                const double delta_e = d_new - d_old;

                bool accept = false;
                if (delta_e <= 0.0) {
                    accept = true;
                } else {
                    const double prob = std::exp(-delta_e / temp);
                    if (uniform_dist(rng) < prob) {
                        accept = true;
                    }
                }

                if (accept) {
                    std::reverse(current_tour.begin() + static_cast<std::ptrdiff_t>(i + 1),
                                 current_tour.begin() + static_cast<std::ptrdiff_t>(j + 1));
                    current_energy += delta_e;

                    if (current_energy < best_energy) {
                        best_energy = current_energy;
                        best_tour = current_tour;
                    }
                }
            }
            temp *= config.alpha;
        }

        return {best_tour, best_energy};
    }

private:
    std::vector<Point> cities_;
};
