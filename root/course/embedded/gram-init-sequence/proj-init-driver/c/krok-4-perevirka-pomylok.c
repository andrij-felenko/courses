typedef enum { DISP_OK = 0, DISP_ERR_BUS, DISP_ERR_ARGS } disp_status_t;

// Примітиви тепер звітують про збій шини.
int send_cmd_checked(uint8_t c);                        // 0 — успіх, інакше — збій
int send_data_checked(const uint8_t *buf, uint32_t n);  // 0 — успіх, інакше — збій

disp_status_t run_init_table_checked(const init_cmd_t *tab, uint32_t n) {
    for (uint32_t i = 0; i < n; i++) {
        if (send_cmd_checked(tab[i].cmd) != 0) {
            return DISP_ERR_BUS;             // команда не долетіла — далі йти безглуздо
        }
        if (tab[i].n_args > 0) {
            if (send_data_checked(tab[i].args, tab[i].n_args) != 0) {
                return DISP_ERR_BUS;         // аргументи не долетіли — теж стоп
            }
        }
        if (tab[i].delay_ms > 0) {
            delay_ms(tab[i].delay_ms);
        }
    }
    return DISP_OK;                          // уся таблиця пройшла чисто
}
