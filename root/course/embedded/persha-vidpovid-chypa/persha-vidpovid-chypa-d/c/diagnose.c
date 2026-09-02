/* Код помилки інженерові на столі не допомагає — потрібен перший крок
 * перевірки. Тут і живе розшифрування звіту разом із таблицею відомих
 * заводських ідентифікаторів. */
#include "bringup.h"

#include <stdio.h>

typedef struct {
    uint8_t     id_reg;
    uint8_t     id;
    const char *name;
} known_chip_t;

static const known_chip_t KNOWN_CHIPS[] = {
    { 0x75u, 0x68u, "InvenSense MPU-6050" },
    { 0x75u, 0x71u, "InvenSense MPU-9250" },
    { 0x75u, 0x73u, "InvenSense MPU-9255" },
    { 0xD0u, 0x60u, "Bosch BME280"        },
    { 0xD0u, 0x58u, "Bosch BMP280"        },
    { 0x0Fu, 0x33u, "ST LIS3DH"           },
    { 0x0Fu, 0x69u, "ST LSM6DS3"          },
    { 0x00u, 0xE5u, "Analog Devices ADXL345" },
};

const char *bringup_known_chip(uint8_t id_reg, uint8_t id)
{
    unsigned i;

    for (i = 0u; i < sizeof KNOWN_CHIPS / sizeof KNOWN_CHIPS[0]; ++i) {
        if (KNOWN_CHIPS[i].id_reg == id_reg && KNOWN_CHIPS[i].id == id) {
            return KNOWN_CHIPS[i].name;
        }
    }
    return NULL;
}

const char *bringup_status_text(bringup_status_t status)
{
    switch (status) {
    case BRINGUP_OK:               return "чип живий, обидва напрями шини перевірено";
    case BRINGUP_NO_ANSWER:        return "відповіді немає: NACK або тайм-аут на фізичному рівні";
    case BRINGUP_BUS_STUCK_HIGH:   return "0xFF: лінія весь кадр трималася на рівні підтяжки";
    case BRINGUP_BUS_STUCK_LOW:    return "0x00: лінія весь кадр трималася на землі";
    case BRINGUP_BIT_SHIFT:        return "ID зсунуто на один розряд: пайка ціла, збита фаза шини";
    case BRINGUP_FOREIGN_ID:       return "відповів не той кремній, якого ми чекали";
    case BRINGUP_WRITE_PATH_DEAD:  return "читання працює, запис до кристала не доходить";
    case BRINGUP_SCRATCHPAD_BAD:   return "запис доходить, але біти спотворюються";
    default:                       return "невідомий стан";
    }
}

const char *bringup_first_step(const diagnostic_report_t *report)
{
    switch (report->status) {
    case BRINGUP_OK:
        return "можна писати драйвер: фізичний рівень перевірено";
    case BRINGUP_NO_ANSWER:
        return "виміряти VDD просто на блокувальному конденсаторі чипа; перевірити вивід "
               "RESET/NRST і чи витримано паузу t_POR після подачі живлення";
    case BRINGUP_BUS_STUCK_HIGH:
        return "логічним аналізатором подивитися CS і SCK: чи падає CS у нуль і чи є такти; "
               "на I2C — чи не зсунуто 7-бітну адресу на біт R/W";
    case BRINGUP_BUS_STUCK_LOW:
        return "знеструмити плату й виміряти опір SDA/MISO до GND; якщо більше за 10 кОм — "
               "видати 9 тактів SCL, щоб розчепити завислий автомат слейва";
    case BRINGUP_BIT_SHIFT:
        return "звірити CPOL/CPHA з даташитом і знизити частоту SCK удвічі; на I2C — "
               "перевірити, чи не подано 8-бітну адресу замість 7-бітної";
    case BRINGUP_FOREIGN_ID:
        return "прочитати маркування SMD на корпусі та перевірити адресний вивід AD0/SDO — "
               "можливо, відповідає сусідній чип на тій самій адресі";
    case BRINGUP_WRITE_PATH_DEAD:
        return "продзвонити MOSI (або SDA) від ніжки мікроконтролера до ніжки чипа; "
               "перевірити, чи обраний регістр не Read-Only і чи чип не в режимі Sleep";
    case BRINGUP_SCRATCHPAD_BAD:
        return "оглянути сусідні ніжки під мікроскопом на містки припою; перевірити довжину "
               "шлейфа й узгодження ліній, знизити частоту шини";
    default:
        return "перечитати звіт";
    }
}

static void to_bits(uint8_t value, char out[9])
{
    unsigned i;

    for (i = 0u; i < 8u; ++i) {
        out[i] = ((value >> (7u - i)) & 1u) ? '1' : '0';
    }
    out[8] = '\0';
}

void bringup_print_report(const diagnostic_report_t *report, const chip_config_t *cfg)
{
    char bits[9];

    printf("  статус       : %s\n", bringup_status_text(report->status));

    if (report->status != BRINGUP_NO_ANSWER) {
        to_bits(report->received_id, bits);
        printf("  WHO_AM_I[0x%02X]: очікували 0x%02X, прочитали 0x%02X (0b%s), спроб %u\n",
               cfg->id_reg, cfg->expected_id, report->received_id, bits, report->attempts);
    } else {
        printf("  WHO_AM_I[0x%02X]: жодна з %u спроб не дочекалася підтвердження\n",
               cfg->id_reg, report->attempts);
    }

    if (report->status == BRINGUP_BIT_SHIFT) {
        printf("  зсув         : %s (0x%02X %s 1 = 0x%02X) — кремній оригінальний\n",
               report->shift == BRINGUP_SHIFT_LEFT ? "вліво, ведучий запізнюється на пів такту"
                                                   : "вправо, ведучий стробує зарано",
               cfg->expected_id,
               report->shift == BRINGUP_SHIFT_LEFT ? "<<" : ">>",
               report->received_id);
    }

    if (report->status == BRINGUP_FOREIGN_ID) {
        const char *neighbour = bringup_known_chip(cfg->id_reg, report->received_id);
        if (neighbour != NULL) {
            printf("  за таблицею  : 0x%02X — це %s, на платі не той компонент\n",
                   report->received_id, neighbour);
        } else {
            printf("  за таблицею  : 0x%02X не належить жодному відомому чипу\n",
                   report->received_id);
        }
    }

    if (report->status == BRINGUP_WRITE_PATH_DEAD) {
        printf("  Scratchpad[0x%02X]: писали 0x%02X, читається старе 0x%02X — байт до кристала не дійшов\n",
               cfg->scratchpad_reg, report->written, report->readback);
    }

    if (report->status == BRINGUP_SCRATCHPAD_BAD) {
        char written_bits[9];
        char readback_bits[9];

        to_bits(report->written, written_bits);
        to_bits(report->readback, readback_bits);
        printf("  Scratchpad[0x%02X]: 0b%s → 0b%s\n",
               cfg->scratchpad_reg, written_bits, readback_bits);

        if (report->bridged != 0u) {
            to_bits(report->bridged, bits);
            printf("  містки       : 0b%s (сусідні розряди злиті між собою)\n", bits);
        }
        if (report->stuck_high != 0u) {
            to_bits(report->stuck_high, bits);
            printf("  залипання в 1: 0b%s\n", bits);
        }
        if (report->stuck_low != 0u) {
            to_bits(report->stuck_low, bits);
            printf("  залипання в 0: 0b%s\n", bits);
        }
    }

    printf("  перший крок  : %s\n", bringup_first_step(report));
}
