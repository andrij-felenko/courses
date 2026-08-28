#include <vector>
#include <string>
#include <cmath>
#include <optional>
#include <algorithm>
#include <stdexcept>

namespace thermo {

struct PhaseSystem {
    std::vector<std::string> species_names;
    std::vector<std::vector<double>> stoich_matrix;
    int num_constraints = 0;
    int num_phases = 1;
    bool is_condensed = false;
};

struct PhaseResult {
    int independent_reactions = 0;
    int gibbs_components = 0;
    int degrees_of_freedom = 0;
    bool is_valid_equilibrium = false;
    std::string equilibrium_type;
};

class PhaseEquilibriumSolver {
public:
    static std::optional<PhaseResult> analyze(const PhaseSystem& sys) {
        if (sys.species_names.empty() || sys.num_phases < 1) {
            return std::nullopt;
        }

        const int num_species = static_cast<int>(sys.species_names.size());
        const int num_reactions = static_cast<int>(sys.stoich_matrix.size());

        int rank = calculate_rank(sys.stoich_matrix, num_species);

        PhaseResult res;
        res.independent_reactions = rank;
        res.gibbs_components = std::max(1, num_species - rank - sys.num_constraints);

        const int env_params = sys.is_condensed ? 1 : 2;
        res.degrees_of_freedom = res.gibbs_components - sys.num_phases + env_params;
        res.is_valid_equilibrium = (res.degrees_of_freedom >= 0);

        if (res.degrees_of_freedom < 0) {
            res.equilibrium_type = "Перевизначена (термодинамічно неможлива рівновага)";
        } else if (res.degrees_of_freedom == 0) {
            res.equilibrium_type = "Нонваріантна (F = 0, інваріантна точка)";
        } else if (res.degrees_of_freedom == 1) {
            res.equilibrium_type = "Моноваріантна (F = 1, моноваріантна лінія)";
        } else if (res.degrees_of_freedom == 2) {
            res.equilibrium_type = "Диваріантна (F = 2, двовимірна область)";
        } else {
            res.equilibrium_type = "Поліваріантна (F > 2)";
        }

        return res;
    }

private:
    static constexpr double EPSILON = 1e-9;

    static int calculate_rank(std::vector<std::vector<double>> matrix, int num_cols) {
        if (matrix.empty()) return 0;
        const int num_rows = static_cast<int>(matrix.size());

        int rank = 0;
        std::vector<bool> row_selected(num_rows, false);

        for (int col = 0; col < num_cols; ++col) {
            int pivot_row = -1;
            double max_val = EPSILON;

            for (int row = 0; row < num_rows; ++row) {
                if (!row_selected[row] && std::abs(matrix[row][col]) > max_val) {
                    max_val = std::abs(matrix[row][col]);
                    pivot_row = row;
                }
            }

            if (pivot_row != -1) {
                row_selected[pivot_row] = true;
                rank++;

                for (int row = 0; row < num_rows; ++row) {
                    if (row != pivot_row && std::abs(matrix[row][col]) > EPSILON) {
                        double factor = matrix[row][col] / matrix[pivot_row][col];
                        for (int c = col; c < num_cols; ++c) {
                            matrix[row][c] -= factor * matrix[pivot_row][c];
                        }
                    }
                }
            }
        }
        return rank;
    }
};

} // namespace thermo
