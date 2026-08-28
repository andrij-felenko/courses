// Кожен давач: адреса на шині, регістр підпису й очікуване значення підпису.
typedef struct {
    uint8_t i2c_addr;
    uint8_t whoami_reg;
    uint8_t whoami_expected;
} sensor_t;

static const sensor_t sensors[] = {
    { .i2c_addr = 0x68, .whoami_reg = 0x75, .whoami_expected = 0x71 },  // напр. IMU
    { .i2c_addr = 0x76, .whoami_reg = 0xD0, .whoami_expected = 0x60 },  // напр. барометр
};
#define N_SENSORS (sizeof(sensors) / sizeof(sensors[0]))

// Прочитати підпис одного давача. Повертає прочитаний байт,
// а через *ok — чи збігся він з очікуваним (і чи взагалі відповіла шина).
uint8_t sensor_probe(const sensor_t *s, bool *ok) {
    uint8_t id = 0xFF;
    if (i2c_read_reg(s->i2c_addr, s->whoami_reg, &id) != I2C_OK) {
        *ok = false;              // шина не відповіла (NACK) — давача нема на лінії
        return 0xFF;
    }
    *ok = (id == s->whoami_expected);
    return id;                    // сам байт кладемо в рапорт — видно, ХТО відповів
}
