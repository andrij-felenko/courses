#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "link_budget.h"

int main(int argc, char *argv[]) {
    link_params_t params = {
        .freq_mhz = 868.0,
        .distance_km = 5.0,
        .tx_power_dbm = 14.0,
        .tx_gain_dbi = 2.15,
        .tx_loss_db = 0.5,
        .rx_gain_dbi = 2.15,
        .rx_loss_db = 0.5,
        .rx_sens_dbm = -125.0
    };

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "-f") == 0 && i + 1 < argc) {
            params.freq_mhz = atof(argv[++i]);
        } else if (strcmp(argv[i], "-d") == 0 && i + 1 < argc) {
            params.distance_km = atof(argv[++i]);
        } else if (strcmp(argv[i], "-p") == 0 && i + 1 < argc) {
            params.tx_power_dbm = atof(argv[++i]);
        } else if (strcmp(argv[i], "-s") == 0 && i + 1 < argc) {
            params.rx_sens_dbm = atof(argv[++i]);
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            printf("Використання: %s [-f freq_mhz] [-d dist_km] [-p ptx_dbm] [-s sens_dbm]\n", argv[0]);
            printf("Параметри за замовчуванням: 868 МГц, 5 км, +14 дБм Tx, -125 дБм Sens\n");
            return 0;
        }
    }

    char err_buf[128];
    if (!link_budget_validate(&params, err_buf, sizeof(err_buf))) {
        fprintf(stderr, "Помилка валідації: %s\n", err_buf);
        return 1;
    }

    link_result_t result;
    link_budget_calculate(&params, &result);
    link_budget_print_report(&params, &result);

    return 0;
}
