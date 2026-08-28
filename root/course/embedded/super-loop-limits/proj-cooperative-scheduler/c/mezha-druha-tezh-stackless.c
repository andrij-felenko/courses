// Дочірній протопотік: сам собі switch, тож паузи всередині — законні
static int pt_read_i2c(pt_t *pt, uint8_t reg, int *out) {
    PT_BEGIN(pt);
    i2c_start(reg);
    PT_WAIT_UNTIL(pt, i2c_ready());    // тепер це в СВОЄМУ switch — ок
    *out = i2c_data();
    PT_END(pt);
}

// Батьківський: чекає на дочірній як на під-протопотік
static int pt_sensor2(pt_t *pt, pt_t *child, int *val) {
    PT_BEGIN(pt);
    for (;;) {
        // PT_WAIT_THREAD: крути дочірній, доки не завершиться
        PT_INIT(child);
        PT_WAIT_UNTIL(pt, pt_read_i2c(child, 0x40, val) == PT_DONE);
        publish(*val);
        PT_WAIT_UNTIL(pt, /* свій період */ 1);
    }
    PT_END(pt);
}
