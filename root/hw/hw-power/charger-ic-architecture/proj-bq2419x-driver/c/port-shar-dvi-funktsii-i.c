extern I2C_HandleTypeDef hi2c1;

int bq_i2c_write(uint8_t reg, uint8_t val) {
    return HAL_I2C_Mem_Write(&hi2c1, BQ_ADDR << 1, reg,
                             I2C_MEMADD_SIZE_8BIT, &val, 1, 50) == HAL_OK ? 0 : -1;
}
int bq_i2c_read(uint8_t reg, uint8_t *val) {
    return HAL_I2C_Mem_Read(&hi2c1, BQ_ADDR << 1, reg,
                            I2C_MEMADD_SIZE_8BIT, val, 1, 50) == HAL_OK ? 0 : -1;
}
