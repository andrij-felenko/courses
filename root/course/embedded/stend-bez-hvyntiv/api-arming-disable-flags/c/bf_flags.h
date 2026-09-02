#ifndef BF_FLAGS_H
#define BF_FLAGS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

/* Скільки бітів armingDisableFlags знає цей довідник.
 * Прошивка віддає своє число окремим байтом у відповіді MSP_STATUS:
 * якщо воно більше за наше, плата новіша за довідник і частину піднятих
 * бітів ми назвати не зможемо — саме тому лічильник і передається. */
#define BF_FLAG_COUNT 24u

typedef enum {
    BF_NO_GYRO = 0,
    BF_FAILSAFE,
    BF_RX_FAILSAFE,
    BF_BAD_RX_RECOVERY,
    BF_BOXFAILSAFE,
    BF_THROTTLE,
    BF_CLI,
    BF_CMS_MENU,
    BF_OSD_MENU,
    BF_ROLLPITCH_CLIPPED,
    BF_SERVO_INIT,
    BF_MOTOR_PROTOCOL,
    BF_ACC_CAL,
    BF_MOTOR_TEST,
    BF_ARM_SWITCH,
    BF_MSP,
    BF_PARALYZE,
    BF_GPS,
    BF_RESC,
    BF_RPMFILTER,
    BF_REBOOT_REQUIRED,
    BF_NOPREARM,
    BF_LOAD,
    BF_CALIBRATING
} bf_flag_t;

#define BF_BIT(flag) ((uint32_t)1u << (unsigned)(flag))

typedef struct {
    const char *name;    /* так прапорець друкує CLI-команда `status` */
    const char *cause;   /* через що він піднімається на стенді */
    const char *remedy;  /* що зробити руками, щоб зняти */
} bf_flag_info_t;

/* NULL, якщо біт поза таблицею довідника. */
const bf_flag_info_t *bf_flag_info(bf_flag_t flag);

/* Пошук за назвою з CLI; len дозволяє не копіювати підрядок. */
bool bf_flag_by_name(const char *name, size_t len, bf_flag_t *out);

/* Розбір рядка `Arming disable flags: THROTTLE CLI MSP`.
 * Повертає маску; назви, яких немає в таблиці, рахує в unknown_count. */
uint32_t bf_parse_cli_status(const char *line, unsigned *unknown_count);

/* Друкує кожен піднятий біт з причиною і рецептом зняття. */
void bf_print_mask(uint32_t mask, FILE *out);

#endif /* BF_FLAGS_H */
