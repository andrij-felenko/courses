// Ініціалізація та головний цикл C-версії компаса
int main(void) {
    qmc5883l_t mag;
    ssd1306_t disp;
    i2c_init(I2C_SPEED_FAST);
    ssd1306_init(&disp, SSD1306_I2C_ADDR_DEFAULT);
    qmc5883l_init(&mag, QMC5883L_I2C_ADDR, QMC5883L_MODE_CONTINUOUS,
                  QMC5883L_ODR_100HZ, QMC5883L_RNG_8G, QMC5883L_OSR_512);
    while (1) {
        if (qmc5883l_is_data_ready(&mag)) {
            qmc5883l_raw_t raw;
            qmc5883l_read_raw(&mag, &raw);
            float cx, cy, cz;
            qmc5883l_calib_apply(&mag.calib, &raw, &cx, &cy, &cz);
            float heading = qmc5883l_compute_heading(cx, cy, 6.5f);
            ssd1306_clear(&disp);
            ssd1306_draw_compass(&disp, 32, 32, 26, heading);
            ssd1306_update(&disp);
        }
    }
}
