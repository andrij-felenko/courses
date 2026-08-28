#pragma once

#include <concepts>
#include <cstddef>
#include <cstdint>
#include <random>
#include <span>
#include <functional>
#include <algorithm>
#include <cmath>

namespace sa {

/* Концепт C++20 для визначення задачі відпалу */
template <typename Problem, typename State, typename Move>
concept AnnealingProblem = requires(Problem p, State& s, const State& cs, const Move& m, std::mt19937_64& rng) {
    { p.evaluate_full(cs) } -> std::convertible_to<double>;
    { p.propose_move(cs, rng) } -> std::same_as<Move>;
    { p.evaluate_delta(cs, m) } -> std::convertible_to<double>;
    { p.apply_move(s, m) } -> std::same_as<void>;
};

enum class CoolingType {
    Geometric,
    Linear,
    Logarithmic
};

struct Params {
    double initial_temp = 1000.0;
    double min_temp = 1e-4;
    double cooling_rate = 0.95;
    std::size_t steps_per_epoch = 1000;
    std::size_t max_epochs = 5000;
    std::size_t max_stagnation = 200;
    std::size_t resync_interval = 10000;
    CoolingType cooling_type = CoolingType::Geometric;
};

struct Stats {
    std::uint64_t total_proposals = 0;
    std::uint64_t accepted_improvements = 0;
    std::uint64_t accepted_deteriorations = 0;
    std::uint64_t rejected_moves = 0;
    double best_energy = 0.0;
    double final_temp = 0.0;
    std::size_t epochs_run = 0;

    [[nodiscard]] double acceptance_rate() const noexcept {
        if (total_proposals == 0) return 0.0;
        return static_cast<double>(accepted_improvements + accepted_deteriorations) / 
               static_cast<double>(total_proposals);
    }
};

/* Шаблонний оптимізатор з нульовим оверхедом поліморфізму */
template <typename State, typename Move, AnnealingProblem<State, Move> Problem>
class Optimizer {
public:
    using ObserverCallback = std::function<void(std::size_t epoch, double temp, double best_energy, double accept_rate)>;

    explicit Optimizer(Problem problem, Params params = {})
        : problem_(std::move(problem)), params_(params) {}

    Stats run(State& initial_state, std::uint64_t seed = 42, ObserverCallback observer = nullptr) {
        std::mt19937_64 rng(seed);
        std::uniform_real_distribution<double> uniform_dist(0.0, 1.0);

        State current_state = initial_state;
        State best_state = initial_state;

        double current_energy = problem_.evaluate_full(current_state);
        double best_energy = current_energy;

        double temp = params_.initial_temp;
        Stats stats{};
        stats.best_energy = best_energy;

        std::size_t stagnation_counter = 0;
        std::size_t steps_since_resync = 0;

        for (std::size_t epoch = 0; epoch < params_.max_epochs && temp > params_.min_temp; ++epoch) {
            std::uint64_t epoch_proposals = 0;
            std::uint64_t epoch_accepted = 0;

            for (std::size_t step = 0; step < params_.steps_per_epoch; ++step) {
                Move move = problem_.propose_move(current_state, rng);
                double delta_e = problem_.evaluate_delta(current_state, move);

                ++stats.total_proposals;
                ++epoch_proposals;
                ++steps_since_resync;

                bool accept = false;
                if (delta_e <= 0.0) {
                    accept = true;
                    ++stats.accepted_improvements;
                } else {
                    double acceptance_prob = std::exp(-delta_e / temp);
                    if (uniform_dist(rng) < acceptance_prob) {
                        accept = true;
                        ++stats.accepted_deteriorations;
                    } else {
                        ++stats.rejected_moves;
                    }
                }

                if (accept) {
                    problem_.apply_move(current_state, move);
                    current_energy += delta_e;
                    ++epoch_accepted;

                    if (steps_since_resync >= params_.resync_interval) {
                        current_energy = problem_.evaluate_full(current_state);
                        steps_since_resync = 0;
                    }

                    if (current_energy < best_energy) {
                        best_energy = current_energy;
                        best_state = current_state;
                        stagnation_counter = 0;
                    }
                }
            }

            stats.best_energy = best_energy;
            stats.final_temp = temp;
            stats.epochs_run = epoch + 1;

            if (observer) {
                double epoch_rate = epoch_proposals > 0 
                    ? static_cast<double>(epoch_accepted) / static_cast<double>(epoch_proposals) 
                    : 0.0;
                observer(epoch, temp, best_energy, epoch_rate);
            }

            // Оновлення температури за обраним законом
            switch (params_.cooling_type) {
                case CoolingType::Geometric:
                    temp *= params_.cooling_rate;
                    break;
                case CoolingType::Linear:
                    temp = std::max(params_.min_temp, temp - params_.cooling_rate);
                    break;
                case CoolingType::Logarithmic:
                    temp = params_.initial_temp / std::log(2.0 + static_cast<double>(epoch));
                    break;
            }

            ++stagnation_counter;
            if (stagnation_counter >= params_.max_stagnation) {
                break; // Дострокова зупинка при замерзанні
            }
        }

        initial_state = std::move(best_state);
        return stats;
    }

private:
    Problem problem_;
    Params params_;
};

} // namespace sa
