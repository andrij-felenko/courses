/* Фрагментація купи та небезпека витоку пам'яті */
sensor_result_t *get_readings_leaky(void) {
    sensor_result_t *res = (sensor_result_t *)malloc(sizeof(sensor_result_t));
    if (!res) return NULL;
    if (i2c_read_bytes(REG_DATA, res->raw, 6) != 0) {
        /* Катастрофа: забули free(res) перед аварійним виходом */
        return NULL;
    }
    return res;
}
