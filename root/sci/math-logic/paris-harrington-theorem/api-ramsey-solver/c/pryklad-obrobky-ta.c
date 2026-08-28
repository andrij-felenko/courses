ph_config_t config;
ph_config_init(&config);
config.target_m = 3;
config.num_colors = 2;

ph_result_t result;
ph_status_t st = ph_compute_bound(&config, &result);

if (st == PH_SUCCESS) {
    printf("Обчислено поріг PH: %u за %.3f сек.\n", 
           result.computed_N, result.execution_time_sec);
} else if (st == PH_ERROR_TIMEOUT) {
    fprintf(stderr, "Обчислення перервано за тайм-аутом.\n");
}
