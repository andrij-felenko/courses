#include <stdio.h>
#include <stdlib.h>
#include "libthermo_phase.h"

int main(void) {
    // Система парового реформінгу метану: 5 сполук, 2 реакції
    double stoich[2 * 5] = {
        -1.0, -1.0,  1.0,  0.0,  3.0,  /* CH4 + H2O ⇌ CO + 3 H2 */
         0.0, -1.0, -1.0,  1.0,  1.0   /* CO + H2O ⇌ CO2 + H2   */
    };

    PhaseSystemSpecC spec;
    spec.num_species = 5;
    spec.num_reactions = 2;
    spec.num_constraints = 0;
    spec.num_phases = 1;
    spec.is_condensed = false;
    spec.stoich_matrix_flat = stoich;

    PhaseResultSpecC result;
    ThermoStatusCodeC code = thermo_analyze_phase_system(&spec, &result);

    if (code == THERMO_SUCCESS) {
        printf("--- Аналіз фазової рівноваги (C-API) ---\n");
        printf("Ранг реакцій R: %zu\n", result.rank_reactions);
        printf("Компоненти Гіббса K: %zu\n", result.gibbs_components);
        printf("Ступені вільності F: %d\n", result.degrees_of_freedom);
        printf("Статус: %s\n", result.status_message);
    } else {
        printf("Помилка обчислення: %s\n", thermo_status_to_string(code));
    }

    return 0;
}
