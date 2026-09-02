/* На bring-up програмний ведучий зручніший за апаратний блок:
   він не має власного стану помилки шини, з якого треба виходити,
   і кожен фронт видно на логічному аналізаторі саме там, де його поставили. */
#include "i2c_bitbang.h"
#include "i2c_lines.h"

/* Півперіод 5 мкс — це приблизно 100 кГц, стандартна швидкість шини */
#define HALF_PERIOD_US 5u

/* Скільки терпимо розтягнутий веденим такт, поки не визнаємо лінію мертвою */
#define STRETCH_TIMEOUT_US 2000u

const char *i2c_status_text(i2c_status_t st) {
    switch (st) {
    case I2C_OK:              return "OK";
    case I2C_NACK:            return "NACK: адресу видано, підтвердження немає";
    case I2C_LINES_BUSY:      return "SDA лежить у нулі ще до умови START";
    case I2C_STRETCH_TIMEOUT: return "SCL не піднімається: немає підтяжки або ведений тримає такт";
    case I2C_STOP_FAILED:     return "після умови STOP лінія SDA не піднялася";
    }
    return "невідомий статус";
}

/* Відпустити SCL і дочекатися, поки лінія справді підніметься.
   Ведений має право притримати такт (clock stretching), і це нормально;
   ненормально — коли він тримає його вічно або підтяжки взагалі немає. */
static i2c_status_t scl_release_and_wait(void) {
    uint32_t waited_us = 0;

    i2c_scl_release();
    while (!i2c_scl_read()) {
        if (waited_us >= STRETCH_TIMEOUT_US) {
            return I2C_STRETCH_TIMEOUT;
        }
        i2c_delay_us(1);
        waited_us += 1;
    }
    i2c_delay_us(HALF_PERIOD_US);
    return I2C_OK;
}

/* START: перепад SDA з 1 у 0 при високому SCL */
static i2c_status_t i2c_start(void) {
    i2c_status_t st;

    i2c_sda_release();
    st = scl_release_and_wait();
    if (st != I2C_OK) {
        return st;
    }
    if (!i2c_sda_read()) {
        /* Хтось тримає SDA — умову START сформувати неможливо */
        return I2C_LINES_BUSY;
    }

    i2c_sda_drive_low();
    i2c_delay_us(HALF_PERIOD_US);
    i2c_scl_drive_low();
    i2c_delay_us(HALF_PERIOD_US);
    return I2C_OK;
}

/* STOP: перепад SDA з 0 у 1 при високому SCL */
static i2c_status_t i2c_stop(void) {
    i2c_status_t st;

    i2c_sda_drive_low();
    i2c_delay_us(HALF_PERIOD_US);
    st = scl_release_and_wait();
    if (st != I2C_OK) {
        return st;
    }
    i2c_sda_release();
    i2c_delay_us(HALF_PERIOD_US);

    /* Якщо після STOP лінія не піднялася, ведений знову завис або SDA замкнена */
    return i2c_sda_read() ? I2C_OK : I2C_STOP_FAILED;
}

/* Біт виставляємо при низькому SCL, ведений читає його на висхідному фронті */
static i2c_status_t write_bit(bool bit) {
    i2c_status_t st;

    if (bit) {
        i2c_sda_release();
    } else {
        i2c_sda_drive_low();
    }
    i2c_delay_us(HALF_PERIOD_US);

    st = scl_release_and_wait();
    if (st != I2C_OK) {
        return st;
    }
    i2c_scl_drive_low();
    i2c_delay_us(HALF_PERIOD_US);
    return I2C_OK;
}

/* Дев'ятий такт: ведучий відпускає SDA, ведений притягує її до нуля на знак ACK */
static i2c_status_t read_ack(bool *ack) {
    i2c_status_t st;

    i2c_sda_release();
    i2c_delay_us(HALF_PERIOD_US);

    st = scl_release_and_wait();
    if (st != I2C_OK) {
        return st;
    }
    *ack = !i2c_sda_read();
    i2c_scl_drive_low();
    i2c_delay_us(HALF_PERIOD_US);
    return I2C_OK;
}

i2c_idle_state_t i2c_read_idle_state(void) {
    i2c_idle_state_t state;

    i2c_scl_release();
    i2c_sda_release();
    i2c_delay_us(HALF_PERIOD_US);

    state.scl_high = i2c_scl_read();
    state.sda_high = i2c_sda_read();
    return state;
}

bool i2c_recover_bus(void) {
    unsigned i;
    bool released;

    if (i2c_sda_read()) {
        return true; /* шина вільна, виштовхувати нічого */
    }

    /* Тактуємо SCL самі: внутрішній зсувний регістр веденого дожене
       свій недоданий байт і на дев'ятому такті відпустить SDA. */
    i2c_sda_release();
    i2c_scl_release();
    i2c_delay_us(HALF_PERIOD_US);

    released = false;
    for (i = 0; i < 9 && !released; ++i) {
        i2c_scl_drive_low();
        i2c_delay_us(HALF_PERIOD_US);
        i2c_scl_release();
        i2c_delay_us(HALF_PERIOD_US);
        released = i2c_sda_read();
    }

    if (!released) {
        /* Дев'яти тактів не вистачило — це вже не зависання, а залізо:
           коротке замикання SDA на землю або пробитий вхід. */
        return false;
    }

    /* Примусовий STOP, щоб ведений повернувся у вихідний стан */
    i2c_sda_drive_low();
    i2c_delay_us(HALF_PERIOD_US);
    i2c_scl_release();
    i2c_delay_us(HALF_PERIOD_US);
    i2c_sda_release();
    i2c_delay_us(HALF_PERIOD_US);

    return i2c_sda_read();
}

i2c_status_t i2c_probe(uint8_t addr7) {
    i2c_status_t st;
    i2c_status_t stop_st;
    uint8_t frame;
    int8_t bit;
    bool ack = false;

    st = i2c_start();
    if (st != I2C_OK) {
        return st;
    }

    /* Молодший біт кадру — напрямок; нуль означає запис */
    frame = (uint8_t)((addr7 << 1) | 0u);
    for (bit = 7; bit >= 0; --bit) {
        st = write_bit(((frame >> bit) & 1u) != 0u);
        if (st != I2C_OK) {
            (void)i2c_stop();
            return st;
        }
    }

    st = read_ack(&ack);
    if (st != I2C_OK) {
        (void)i2c_stop();
        return st;
    }

    stop_st = i2c_stop();
    if (stop_st != I2C_OK) {
        return stop_st;
    }
    return ack ? I2C_OK : I2C_NACK;
}
