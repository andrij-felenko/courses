#include <util/delay.h>

#define I2C_RISE_TIMEOUT_US 1000u    /* стеля очікування підйому SCL */

static bool i2c_fault;               /* «липкий» прапорець: SCL не піднявся вчасно */

static inline void qd(void) { _delay_us(2.5); }   /* чверть такту */

/* Відпустити SCL і дочекатися, поки лінія СПРАВДІ піднялася. */
static void scl_high(void) {
    scl_release();
    for (uint16_t t = 0; t < I2C_RISE_TIMEOUT_US; t++) {
        if (scl_read()) return;      /* фронт відбувся, високий такт пішов */
        _delay_us(1);
    }
    i2c_fault = true;                /* лінію хтось тримає внизу — далі все марно */
}

/* ── біт ────────────────────────────────────────────────────────────────── */

static void write_bit(bool b) {
    qd();                                   /* чверть 1: хвіст низького такту */
    if (b) sda_release(); else sda_low();   /* SDA міняємо лише при низькому SCL */
    qd();                                   /* чверть 2: дані встоялися до фронту */
    scl_high();
    qd(); qd();                             /* чверті 3 і 4: тут ведений читає */
    scl_low();
}

static bool read_bit(void) {
    qd();
    sda_release();          /* лінію віддано веденому: рівень задає він */
    qd();
    scl_high();
    qd();
    bool b = sda_read();    /* середина високого такту */
    qd();
    scl_low();
    return b;
}

/* ── рамка повідомлення ─────────────────────────────────────────────────── */

/* START: ↓SDA при високому SCL. Ця сама функція дає й повторний START —
   різниця між ними лише в тому, чи стояв перед нею STOP. */
bool i2c_start(void) {
    qd();
    sda_release();          /* SDA відпускаємо при низькому SCL: інакше вийшов би STOP */
    qd();
    scl_high();
    qd();
    if (!sda_read()) return false;   /* SDA внизу — шину тримає хтось інший */
    qd();                            /* разом дві чверті: t_SU;STA */
    sda_low();                       /* ← власне START */
    qd(); qd();                      /* t_HD;STA */
    scl_low();
    return !i2c_fault;
}

/* STOP: ↑SDA при високому SCL. */
void i2c_stop(void) {
    qd();
    sda_low();              /* SDA має бути внизу ще до підйому SCL */
    qd();
    scl_high();
    qd(); qd();             /* t_SU;STO */
    sda_release();          /* ← власне STOP */
    qd(); qd();             /* t_BUF: шина мусить постояти вільною */
}

/* ── байт ───────────────────────────────────────────────────────────────── */

/* Передати байт старшим бітом уперед; true — ведений підтвердив. */
bool i2c_write_byte(uint8_t b) {
    for (uint8_t i = 0; i < 8; i++) {
        write_bit((b & 0x80u) != 0);
        b = (uint8_t)(b << 1);
    }
    return !read_bit() && !i2c_fault;   /* дев'ятий такт: «0» на SDA = ACK */
}

/* Прийняти байт; ack = true — просимо ще, false — це був останній. */
uint8_t i2c_read_byte(bool ack) {
    uint8_t b = 0;
    for (uint8_t i = 0; i < 8; i++)
        b = (uint8_t)((b << 1) | (read_bit() ? 1u : 0u));
    write_bit(!ack);        /* ACK — притягнути SDA до землі; NACK — відпустити */
    return b;
}
