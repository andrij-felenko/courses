typedef struct {
    uint32_t crc_errors;
    uint32_t overrun_errors;
    uint32_t mode_fault_errors;
    bool     continuous_dead_data; // Постійні 0x00 або 0xFF
} health_spi_diag_t;

uint16_t health_evaluate_spi(const health_spi_diag_t *diag) {
    if (!diag) return 0;

    if (diag->mode_fault_errors > 0 || diag->continuous_dead_data) {
        return 100; // Критичний збій лінії або сенсора
    }

    uint32_t total_err = diag->crc_errors + diag->overrun_errors;
    if (total_err == 0) {
        return 1000;
    }
    if (total_err >= 20) {
        return 300;
    }

    return (uint16_t)(1000 - (total_err * 700) / 20);
}
