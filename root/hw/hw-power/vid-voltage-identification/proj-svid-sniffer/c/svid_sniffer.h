/* svid_sniffer.h - Декодер шини SVID для вбудованих систем (C99/C11) */
#ifndef SVID_SNIFFER_H
#define SVID_SNIFFER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SVID_CMD_SETVID_FAST  = 0x00,
    SVID_CMD_SETVID_SLOW  = 0x01,
    SVID_CMD_SETVID_DECAY = 0x02,
    SVID_CMD_SET_REG      = 0x03,
    SVID_CMD_GET_REG      = 0x04,
    SVID_CMD_SET_OFFSET   = 0x07,
    SVID_CMD_UNKNOWN      = 0x1F
} svid_cmd_t;

typedef enum {
    SVID_ACK_OK   = 0x00,
    SVID_ACK_NACK = 0x01,
    SVID_ACK_BUSY = 0x02
} svid_ack_t;

typedef enum {
    SVID_STATE_IDLE,
    SVID_STATE_ADDR,
    SVID_STATE_CMD,
    SVID_STATE_DATA,
    SVID_STATE_PARITY,
    SVID_STATE_TURN_AROUND,
    SVID_STATE_ACK,
    SVID_STATE_SLAVE_DATA,
    SVID_STATE_SLAVE_PARITY,
    SVID_STATE_COMPLETE
} svid_fsm_state_t;

typedef struct {
    uint8_t address;          /* 4 біти адреси VRM (0x0..0xF) */
    svid_cmd_t command;       /* 5 бітів команди */
    uint8_t master_data;      /* 8 бітів даних від процесора */
    bool master_parity_ok;    /* Результат перевірки непарності */
    svid_ack_t slave_ack;     /* Відповідь підпорядкованого пристрою */
    uint8_t slave_data;       /* Байт телеметрії від VRM */
    bool slave_parity_ok;     /* Паритет телеметрії */
    uint32_t timestamp_us;    /* Часова мітка захоплення пакету */
} svid_packet_t;

typedef struct {
    svid_fsm_state_t state;
    uint8_t bit_index;
    uint16_t shift_reg;
    uint8_t ones_count;
    svid_packet_t current_packet;
} svid_decoder_t;

/* Ініціалізація структури декодера */
void svid_decoder_init(svid_decoder_t *dec);

/* Обробка одного тактового імпульсу SCLK та стану лінії SDATA */
bool svid_decoder_step(svid_decoder_t *dec, bool sdata_bit, uint32_t timestamp_us, svid_packet_t *out_pkt);

/* Допоміжні функції перерахунку фізичних величин */
double svid_decode_voltage_vr12(uint8_t vid_code);
double svid_decode_current_imon(uint8_t imon_code, double max_current_a);
double svid_decode_temperature_tmon(uint8_t tmon_code);

#ifdef __cplusplus
}
#endif

#endif /* SVID_SNIFFER_H */

/* svid_sniffer.c - Реалізація логіки автомата станів */
#include "svid_sniffer.h"

void svid_decoder_init(svid_decoder_t *dec) {
    if (!dec) return;
    dec->state = SVID_STATE_IDLE;
    dec->bit_index = 0;
    dec->shift_reg = 0;
    dec->ones_count = 0;
}

static bool check_odd_parity(uint8_t count) {
    return (count & 1) == 1;
}

bool svid_decoder_step(svid_decoder_t *dec, bool sdata, uint32_t timestamp_us, svid_packet_t *out_pkt) {
    if (!dec) return false;

    switch (dec->state) {
    case SVID_STATE_IDLE:
        if (!sdata) { /* Виявлено стартовий біт (перехід у нуль) */
            dec->state = SVID_STATE_ADDR;
            dec->bit_index = 0;
            dec->shift_reg = 0;
            dec->ones_count = 0;
            dec->current_packet.timestamp_us = timestamp_us;
        }
        break;

    case SVID_STATE_ADDR:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        if (sdata) dec->ones_count++;
        dec->bit_index++;
        if (dec->bit_index == 4) {
            dec->current_packet.address = (uint8_t)(dec->shift_reg & 0x0F);
            dec->state = SVID_STATE_CMD;
            dec->bit_index = 0;
            dec->shift_reg = 0;
        }
        break;

    case SVID_STATE_CMD:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        if (sdata) dec->ones_count++;
        dec->bit_index++;
        if (dec->bit_index == 5) {
            dec->current_packet.command = (svid_cmd_t)(dec->shift_reg & 0x1F);
            dec->state = SVID_STATE_DATA;
            dec->bit_index = 0;
            dec->shift_reg = 0;
        }
        break;

    case SVID_STATE_DATA:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        if (sdata) dec->ones_count++;
        dec->bit_index++;
        if (dec->bit_index == 8) {
            dec->current_packet.master_data = (uint8_t)(dec->shift_reg & 0xFF);
            dec->state = SVID_STATE_PARITY;
        }
        break;

    case SVID_STATE_PARITY:
        if (sdata) dec->ones_count++;
        dec->current_packet.master_parity_ok = check_odd_parity(dec->ones_count);
        dec->state = SVID_STATE_TURN_AROUND;
        dec->bit_index = 0;
        break;

    case SVID_STATE_TURN_AROUND:
        dec->bit_index++;
        if (dec->bit_index == 2) { /* 2 такти перемикання напрямку шини */
            dec->state = SVID_STATE_ACK;
            dec->bit_index = 0;
            dec->shift_reg = 0;
            dec->ones_count = 0;
        }
        break;

    case SVID_STATE_ACK:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        dec->bit_index++;
        if (dec->bit_index == 2) {
            dec->current_packet.slave_ack = (svid_ack_t)(dec->shift_reg & 0x03);
            if (dec->current_packet.command == SVID_CMD_GET_REG) {
                dec->state = SVID_STATE_SLAVE_DATA;
                dec->bit_index = 0;
                dec->shift_reg = 0;
                dec->ones_count = 0;
            } else {
                /* Для команд запису транзакція завершена */
                dec->state = SVID_STATE_IDLE;
                if (out_pkt) *out_pkt = dec->current_packet;
                return true;
            }
        }
        break;

    case SVID_STATE_SLAVE_DATA:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        if (sdata) dec->ones_count++;
        dec->bit_index++;
        if (dec->bit_index == 8) {
            dec->current_packet.slave_data = (uint8_t)(dec->shift_reg & 0xFF);
            dec->state = SVID_STATE_SLAVE_PARITY;
        }
        break;

    case SVID_STATE_SLAVE_PARITY:
        if (sdata) dec->ones_count++;
        dec->current_packet.slave_parity_ok = check_odd_parity(dec->ones_count);
        dec->state = SVID_STATE_IDLE;
        if (out_pkt) *out_pkt = dec->current_packet;
        return true;

    default:
        dec->state = SVID_STATE_IDLE;
        break;
    }

    return false;
}

double svid_decode_voltage_vr12(uint8_t vid_code) {
    if (vid_code == 0x00) return 0.0; /* Вихід вимкнено */
    if (vid_code == 0xFF) return 0.0; /* Зарезервовано */
    return 0.245 + ((double)vid_code * 0.005);
}

double svid_decode_current_imon(uint8_t imon_code, double max_current_a) {
    return ((double)imon_code / 255.0) * max_current_a;
}

double svid_decode_temperature_tmon(uint8_t tmon_code) {
    return (double)tmon_code; /* 1 °C на крок квантування */
}
