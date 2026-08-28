/* Bringup SWD Low-Level Master Driver (C99) */
#include <stdint.h>
#include <stdbool.h>

#define SWD_ACK_OK    0x01
#define SWD_ACK_WAIT  0x02
#define SWD_ACK_FAULT 0x04

typedef struct {
    void (*set_swclk)(bool level);
    void (*set_swdio)(bool level);
    bool (*get_swdio)(void);
    void (*set_swdio_dir_out)(bool is_output);
    void (*delay_cycles)(uint32_t cycles);
} swd_port_ops_t;

static void swd_clock_pulse(const swd_port_ops_t *ops) {
    ops->set_swclk(false);
    ops->delay_cycles(2);
    ops->set_swclk(true);
    ops->delay_cycles(2);
}

void swd_line_reset(const swd_port_ops_t *ops) {
    ops->set_swdio_dir_out(true);
    ops->set_swdio(true);
    /* Мінімум 50 тактів логічної 1 для скидання автомата DP */
    for (int i = 0; i < 56; ++i) {
        swd_clock_pulse(ops);
    }
}

void swd_send_switch_sequence(const swd_port_ops_t *ops) {
    /* 16-бітна послідовність перемикання JTAG-to-SWD: 0x79E7 (LSB-first: 0xE79E) */
    uint16_t seq = 0xE79E;
    ops->set_swdio_dir_out(true);
    for (int i = 0; i < 16; ++i) {
        ops->set_swdio((seq >> i) & 1);
        swd_clock_pulse(ops);
    }
}

static uint8_t calculate_parity32(uint32_t val) {
    val ^= val >> 16;
    val ^= val >> 8;
    val ^= val >> 4;
    val ^= val >> 2;
    val ^= val >> 1;
    return (uint8_t)(val & 1);
}

bool swd_read_dp_register(const swd_port_ops_t *ops, uint8_t addr_reg, uint32_t *out_val) {
    uint8_t req = 0x81 | ((addr_reg & 0x0C) << 1); /* Start=1, APnDP=0, RnW=1, Stop=0, Park=1 */
    uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
    req |= (parity << 5);

    /* 1. Відправка 8-бітного запиту Host Request */
    ops->set_swdio_dir_out(true);
    for (int i = 0; i < 8; ++i) {
        ops->set_swdio((req >> i) & 1);
        swd_clock_pulse(ops);
    }

    /* 2. Turnaround: зміна напрямку шини (1 такт) */
    ops->set_swdio_dir_out(false);
    ops->set_swclk(false);
    ops->delay_cycles(2);
    ops->set_swclk(true);
    ops->delay_cycles(2);

    /* 3. Читання 3-бітного ACK відповіді таргета */
    uint8_t ack = 0;
    for (int i = 0; i < 3; ++i) {
        ops->set_swclk(false);
        ops->delay_cycles(2);
        if (ops->get_swdio()) {
            ack |= (1 << i);
        }
        ops->set_swclk(true);
        ops->delay_cycles(2);
    }

    if (ack != SWD_ACK_OK) {
        return false;
    }

    /* 4. Читання 32-бітного значення даних */
    uint32_t data = 0;
    for (int i = 0; i < 32; ++i) {
        ops->set_swclk(false);
        ops->delay_cycles(2);
        if (ops->get_swdio()) {
            data |= (1UL << i);
        }
        ops->set_swclk(true);
        ops->delay_cycles(2);
    }

    /* 5. Читання 1 біта парності */
    ops->set_swclk(false);
    ops->delay_cycles(2);
    bool rcv_parity = ops->get_swdio();
    ops->set_swclk(true);
    ops->delay_cycles(2);

    /* 6. Turnaround та холості такти (Idle) */
    ops->set_swdio_dir_out(true);
    ops->set_swdio(false);
    for (int i = 0; i < 4; ++i) {
        swd_clock_pulse(ops);
    }

    if (rcv_parity != calculate_parity32(data)) {
        return false;
    }

    *out_val = data;
    return true;
}
