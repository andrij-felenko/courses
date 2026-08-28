#ifndef LIBTHERMO_PHASE_HPP
#define LIBTHERMO_PHASE_HPP

#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <cstddef>

namespace thermo {

enum class Status {
    Success = 0,
    WarnOverdetermined = 1,
    WarnCriticalPoint = 2,
    ErrInvalidSpecies = -1,
    ErrInvalidPhases = -2,
    ErrNullPointer = -3
};

struct PhaseSystemConfig {
    std::vector<std::string> species_names;
    std::vector<std::vector<double>> stoich_matrix;
    std::size_t num_constraints = 0;
    std::size_t num_phases = 1;
    bool is_condensed = false;
};

struct PhaseAnalysisResult {
    std::size_t rank_reactions = 0;
    std::size_t gibbs_components = 0;
    int degrees_of_freedom = 0;
    Status status = Status::Success;
    std::string description;

    [[nodiscard]] bool is_valid() const noexcept {
        return degrees_of_freedom >= 0;
    }
};

class PhaseRuleCalculator {
public:
    explicit PhaseRuleCalculator(double epsilon = 1e-9) noexcept
        : m_epsilon(epsilon) {}

    [[nodiscard]] std::expected<PhaseAnalysisResult, Status>
    analyze(const PhaseSystemConfig& config) const;

    [[nodiscard]] std::size_t calculate_matrix_rank(
        const std::vector<std::vector<double>>& matrix,
        std::size_t num_cols
    ) const;

    [[nodiscard]] static std::size_t calculate_gibbs_components(
        std::size_t num_species,
        std::size_t rank,
        std::size_t constraints
    ) noexcept;

    [[nodiscard]] static int calculate_degrees_of_freedom(
        std::size_t components,
        std::size_t phases,
        bool is_condensed
    ) noexcept;

    [[nodiscard]] static std::string_view status_to_string(Status status) noexcept;

private:
    double m_epsilon = 1e-9;
};

} // namespace thermo

#endif /* LIBTHERMO_PHASE_HPP */
