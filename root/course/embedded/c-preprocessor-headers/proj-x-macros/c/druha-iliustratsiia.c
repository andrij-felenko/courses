// Проста послідовність команд запису — X розгортається в код, не в дані.
void sensor_init(void) {
    #define X(name, addr, def)   i2c_write_reg(SENSOR_ADDR, addr, def);
    SENSOR_REGS(X)
    #undef X
    // розгорнеться у:
    //   i2c_write_reg(SENSOR_ADDR, 0x20, 0x07);
    //   i2c_write_reg(SENSOR_ADDR, 0x23, 0x00);
    //   i2c_write_reg(SENSOR_ADDR, 0x30, 0x64);
    //   i2c_write_reg(SENSOR_ADDR, 0x2E, 0x80);
    //   i2c_write_reg(SENSOR_ADDR, 0x0F, 0x00);
}
