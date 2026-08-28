#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_SPECIES 16
#define MAX_REACTIONS 16
#define EPSILON 1e-9

typedef struct {
    int num_species;
    int num_reactions;
    int num_constraints;
    int num_phases;
    bool is_condensed;
    double stoich_matrix[MAX_REACTIONS][MAX_SPECIES];
} PhaseSystemC;

typedef struct {
    int rank_reactions;
    int gibbs_components;
    int degrees_of_freedom;
    bool is_valid_equilibrium;
} PhaseResultC;

static int compute_matrix_rank(double matrix[MAX_REACTIONS][MAX_SPECIES], int rows, int cols) {
    double temp[MAX_REACTIONS][MAX_SPECIES];
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            temp[i][j] = matrix[i][j];
        }
    }

    int rank = 0;
    bool row_selected[MAX_REACTIONS] = { false };

    for (int col = 0; col < cols; ++col) {
        int pivot_row = -1;
        double max_val = EPSILON;

        for (int row = 0; row < rows; ++row) {
            if (!row_selected[row] && fabs(temp[row][col]) > max_val) {
                max_val = fabs(temp[row][col]);
                pivot_row = row;
            }
        }

        if (pivot_row != -1) {
            row_selected[pivot_row] = true;
            rank++;

            for (int row = 0; row < rows; ++row) {
                if (row != pivot_row && fabs(temp[row][col]) > EPSILON) {
                    double factor = temp[row][col] / temp[pivot_row][col];
                    for (int c = col; c < cols; ++c) {
                        temp[row][c] -= factor * temp[pivot_row][c];
                    }
                }
            }
        }
    }
    return rank;
}

PhaseResultC analyze_phase_system_c(const PhaseSystemC* sys) {
    PhaseResultC res;
    if (sys == NULL || sys->num_species <= 0) {
        res.is_valid_equilibrium = false;
        return res;
    }

    res.rank_reactions = compute_matrix_rank(
        (double(*)[MAX_SPECIES])sys->stoich_matrix, 
        sys->num_reactions, 
        sys->num_species
    );

    res.gibbs_components = sys->num_species - res.rank_reactions - sys->num_constraints;
    if (res.gibbs_components < 1) {
        res.gibbs_components = 1;
    }

    int env_params = sys->is_condensed ? 1 : 2;
    res.degrees_of_freedom = res.gibbs_components - sys->num_phases + env_params;
    res.is_valid_equilibrium = (res.degrees_of_freedom >= 0);

    return res;
}
