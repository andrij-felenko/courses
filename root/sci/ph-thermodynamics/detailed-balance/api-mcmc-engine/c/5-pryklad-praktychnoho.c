#include "mcmc_engine.h"
#include <stdio.h>

int main(void) {
    mcmc_config_t cfg = {
        .num_states = 4,
        .temperature = 1.0,
        .burn_in_steps = 50000,
        .sampling_steps = 2000000,
        .random_seed = 12345,
        .balance_tolerance = 1e-4
    };

    mcmc_engine_t *engine = NULL;
    if (mcmc_engine_create(&cfg, &engine) != MCMC_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації MCMC двигуна\n");
        return 1;
    }

    double energies[4] = {0.0, 1.5, 3.0, 0.5};
    mcmc_engine_set_energies(engine, energies, 4);

    if (mcmc_engine_run(engine) == MCMC_SUCCESS) {
        mcmc_balance_report_t report;
        mcmc_engine_verify_balance(engine, &report);

        printf("Максимальний дисбаланс потоків: %.8f\n", report.max_imbalance_flux);
        printf("Оцінка генерації ентропії dS/dt: %.8f\n", report.entropy_prod_rate);
        printf("Детальний баланс підтверджено: %s\n", report.is_balanced ? "ТАК" : "НІ");
    }

    mcmc_engine_destroy(engine);
    return 0;
}
