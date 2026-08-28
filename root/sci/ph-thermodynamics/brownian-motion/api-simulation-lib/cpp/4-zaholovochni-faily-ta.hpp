#ifndef BROWNIAN_SIM_HPP
#define BROWNIAN_SIM_HPP

#include <vector>
#include <array>
#include <memory>
#include <optional>
#include <cstddef>
#include <stdexcept>

namespace brownian {

class Simulator {
public:
    explicit Simulator(Config config) : config_(std::move(config)) {}

    ~Simulator() = default;

    Simulator(const Simulator&) = delete;
    Simulator& operator=(const Simulator&) = delete;
    Simulator(Simulator&&) noexcept = default;
    Simulator& operator=(Simulator&&) noexcept = default;

    [[nodiscard]] std::vector<std::vector<State>> run_ensemble();
    [[nodiscard]] MsdAnalysis analyze(const std::vector<std::vector<State>>& trajectories) const;

    [[nodiscard]] const Config& config() const noexcept { return config_; }

private:
    Config config_;
};

} // namespace brownian

#endif // BROWNIAN_SIM_HPP
