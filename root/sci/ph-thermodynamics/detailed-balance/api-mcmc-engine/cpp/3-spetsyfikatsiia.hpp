#ifndef MCMC_ENGINE_HPP
#define MCMC_ENGINE_HPP

#include <vector>
#include <memory>
#include <expected>
#include <string>
#include <span>

namespace mcmc {

enum class ErrorCode {
    InvalidParam,
    OutOfMemory,
    NotConverged,
    BalanceViolated
};

struct Config {
    std::size_t num_states{0};
    double temperature{1.0};
    std::size_t burn_in_steps{100'000};
    std::size_t sampling_steps{1'000'000};
    unsigned int random_seed{42};
    double balance_tolerance{1e-4};
};

struct BalanceReport {
    double max_imbalance_flux{0.0};
    std::size_t worst_edge_from{0};
    std::size_t worst_edge_to{0};
    double entropy_production_rate{0.0};
    bool is_balanced{false};
};

class Engine {
public:
    static std::expected<std::unique_ptr<Engine>, ErrorCode> create(const Config& config);
    
    ~Engine();
    Engine(const Engine&) = delete;
    Engine& operator=(const Engine&) = delete;
    Engine(Engine&&) noexcept;
    Engine& operator=(Engine&&) noexcept;

    ErrorCode set_energies(std::span<const double> energies);
    ErrorCode run();
    
    [[nodiscard]] std::span<const double> get_probabilities() const noexcept;
    [[nodiscard]] BalanceReport verify_balance() const;

private:
    explicit Engine(const Config& config);
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace mcmc

#endif // MCMC_ENGINE_HPP
