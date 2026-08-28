#define AS5048A_CMD_READ_ANGLE 0x3FFF
#define AS5048A_PARITY_BIT     0x8000
#define AS5048A_ERROR_FLAG     0x4000
#define AS5048A_DATA_MASK      0x3FFF

/* Розрахунок біта парності (Even Parity) */
static uint16_t as5048a_calc_even_parity(uint16_t value) {
    uint16_t count = 0;
    for (uint8_t i = 0; i < 16; ++i) {
        if (value & (1 << i)) count++;
    }
    return (count & 1) ? AS5048A_PARITY_BIT : 0;
}

/* Декодування пакета кута з енкодера AS5048A */
bool as5048a_parse_response(uint16_t raw_response, float *angle_rad_out) {
    uint16_t parity = as5048a_calc_even_parity(raw_response & ~AS5048A_PARITY_BIT);
    if ((raw_response & AS5048A_PARITY_BIT) != parity) {
        return false; /* Помилка парності кадру SPI */
    }
    
    if (raw_response & AS5048A_ERROR_FLAG) {
        return false; /* Помилка сенсора: втрата магніту або вихід за межі поля */
    }
    
    uint16_t raw_data = raw_response & AS5048A_DATA_MASK;
    *angle_rad_out = ((float)raw_data / 16384.0f) * TWO_PI;
    return true;
}
