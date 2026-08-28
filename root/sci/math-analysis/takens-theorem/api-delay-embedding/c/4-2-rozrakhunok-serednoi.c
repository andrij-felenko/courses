#include "takens.h"
#include <stdio.h>

void run_mi_example(const double *signal, size_t n) {
    TakensConfig config;
    takens_config_init_default(&config);
    config.max_delay = 40;

    double mi_buffer[40];
    size_t opt_delay = 0;

    TakensStatus status = takens_compute_mutual_information(signal, n, &config, mi_buffer, &opt_delay);
    if (status == TAKENS_OK) {
        printf("Оптимальна затримка tau: %zu відліків\n", opt_delay);
    } else {
        printf("Помилка обчислення MI: %s\n", takens_status_string(status));
    }
}
