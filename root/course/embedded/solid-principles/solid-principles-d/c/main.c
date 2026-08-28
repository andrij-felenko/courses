// baro.h — інтерфейс: абстракція, від якої залежать обидві сторони
typedef struct baro baro_t;
struct baro {
    int (*read_pressure)(baro_t *self, uint32_t *out_pa);  // повертає 0 або код помилки
};

// політика залежить ЛИШЕ від baro_t — не від жодного драйвера (DIP)
int altitude_step(baro_t *baro, float *out_m) {
    uint32_t pa;
    int err = baro->read_pressure(baro, &pa);   // не знає, хто за інтерфейсом
    if (err) return err;
    *out_m = pressure_to_altitude(pa);
    return 0;
}
