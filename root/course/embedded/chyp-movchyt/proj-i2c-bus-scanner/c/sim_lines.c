/* Ведений I2C у вигляді скінченного автомата, керованого фронтами ліній.
   Рівень лінії з відкритим стоком — це логічне І всіх, хто до неї причепився:
   високий рівень дає підтяжка, і будь-хто один може притиснути лінію в нуль. */
#include "sim_lines.h"

#include <stdio.h>

#include "i2c_lines.h"

typedef enum {
    SL_IDLE,
    SL_RX_ADDR,
    SL_ACK_SETUP,
    SL_ACK_HOLD,
    SL_WAIT_STOP
} slave_state_t;

/* Скільки тактів SCL потрібно зависшому веденому, щоб виштовхнути
   рештки свого байта й нарешті відпустити SDA. */
#define STUCK_CLOCKS_TO_RELEASE 5u

static uint8_t g_slave_addr;
static sim_fault_t g_fault;

static bool g_master_scl_low;
static bool g_master_sda_low;
static bool g_slave_sda_low;
static bool g_slave_stuck;

static bool g_prev_scl;
static bool g_prev_sda;

static slave_state_t g_state;
static uint8_t g_shift;
static uint8_t g_bits;
static unsigned g_stuck_clocks;

static bool scl_level(void) {
    if (g_fault == SIM_FAULT_NO_PULLUPS) {
        return false; /* без підтяжки відпущена лінія просто висить у нулі */
    }
    return !g_master_scl_low;
}

static bool sda_level(void) {
    if (g_fault == SIM_FAULT_NO_PULLUPS) {
        return false;
    }
    return !(g_master_sda_low || g_slave_sda_low);
}

/* Один крок автомата: викликається після кожної зміни ліній ведучим */
static void sim_step(void) {
    bool scl = scl_level();
    bool sda = sda_level();
    bool scl_rise = scl && !g_prev_scl;
    bool scl_fall = !scl && g_prev_scl;

    if (g_slave_stuck) {
        /* Поки чіп не догнав свій байт, він глухий до START і STOP */
        if (scl_rise) {
            g_stuck_clocks++;
            if (g_stuck_clocks >= STUCK_CLOCKS_TO_RELEASE) {
                g_slave_stuck = false;
                g_slave_sda_low = false;
            }
        }
    } else if (scl && g_prev_scl && sda != g_prev_sda) {
        /* Перепад SDA при високому SCL — це службова умова, а не дані */
        if (!sda) {
            g_state = SL_RX_ADDR;
            g_shift = 0;
            g_bits = 0;
        } else {
            g_state = SL_IDLE;
        }
    } else if (scl_rise && g_state == SL_RX_ADDR) {
        g_shift = (uint8_t)((g_shift << 1) | (sda ? 1u : 0u));
        g_bits++;
        if (g_bits == 8u) {
            g_state = SL_ACK_SETUP;
        }
    } else if (scl_fall) {
        switch (g_state) {
        case SL_ACK_SETUP:
            if (g_fault != SIM_FAULT_NO_POWER && (uint8_t)(g_shift >> 1) == g_slave_addr) {
                g_slave_sda_low = true; /* ACK виставляється до дев'ятого такту */
                g_state = SL_ACK_HOLD;
            } else {
                g_state = SL_WAIT_STOP; /* чужа адреса — мовчимо */
            }
            break;
        case SL_ACK_HOLD:
            g_slave_sda_low = false; /* дев'ятий такт минув, лінію віддано */
            g_state = SL_WAIT_STOP;
            break;
        default:
            break;
        }
    }

    g_prev_scl = scl;
    g_prev_sda = sda_level(); /* рівень міг змінитися просто зараз, через ACK */
}

void sim_bus_init(uint8_t slave_addr7, sim_fault_t fault) {
    g_slave_addr = slave_addr7;
    g_fault = fault;

    g_master_scl_low = false;
    g_master_sda_low = false;
    g_slave_stuck = (fault == SIM_FAULT_SDA_STUCK_LOW);
    g_slave_sda_low = g_slave_stuck;

    g_state = SL_IDLE;
    g_shift = 0;
    g_bits = 0;
    g_stuck_clocks = 0;

    g_prev_scl = scl_level();
    g_prev_sda = sda_level();
}

void i2c_lines_take(void) {
    printf("Виводи SCL/SDA переведено в GPIO (апаратний блок I2C вимкнено)\n");
}

void i2c_lines_release_to_peripheral(void) {
    printf("Виводи SCL/SDA повернуто апаратному блоку I2C\n");
}

void i2c_scl_release(void) {
    g_master_scl_low = false;
    sim_step();
}

void i2c_scl_drive_low(void) {
    g_master_scl_low = true;
    sim_step();
}

bool i2c_scl_read(void) {
    return scl_level();
}

void i2c_sda_release(void) {
    g_master_sda_low = false;
    sim_step();
}

void i2c_sda_drive_low(void) {
    g_master_sda_low = true;
    sim_step();
}

bool i2c_sda_read(void) {
    return sda_level();
}

void i2c_delay_us(uint32_t us) {
    /* На платі тут крутиться цикл затримки або читається лічильник таймера.
       Модель безчасова: автомат рухають фронти, а не мікросекунди. */
    (void)us;
}
