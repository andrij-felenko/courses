#ifndef SAFE_ACTUATOR_H
#define SAFE_ACTUATOR_H

#include <stdbool.h>
#include <stdint.h>

/* Магічний токен запиту на взяття під силу. Випадкове значення з високою
 * вагою Геммінга: зіпсований покажчик або обнулена пам'ять його не дадуть. */
#define SAFE_ARM_TOKEN 0x5A3C96E1U

#define PWM_MAX_DUTY        1000U
#define MIN_SAFE_VOLTAGE_MV 11000U
#define MAX_SAFE_VOLTAGE_MV 14500U

/* Півперіод меандру серцебиття: 500 мкс дають 1 кГц на виводі. */
#define HEARTBEAT_HALF_PERIOD_US 500U

/* Найбільша пауза між перемиканнями, яку помпа заряду ще переживає.
 * Далі ємність фільтра просідає й ключ розмикається сам — драйвер мусить
 * побачити це раніше, ніж побачить силова частина. */
#define HEARTBEAT_STALL_US 1500U

/* Скільки часу дозволено на всю послідовність узяття під силу. */
#define ARM_SEQUENCE_TIMEOUT_US 200000U

/* Вікно сторожа: більше за період циклу, менше за час вибігу мотора. */
#define WATCHDOG_TIMEOUT_MS 50U

typedef enum {
    ACTUATOR_DISARMED = 0,   /* сила знята, помпа стоїть, ШІМ у нулі */
    ACTUATOR_ARM_REQUESTED,  /* запит із валідним токеном прийнято */
    ACTUATOR_PRE_ARM_CHECK,  /* самодіагностика перед подачею сили */
    ACTUATOR_ARMED,          /* робочий режим */
    ACTUATOR_FAULT           /* аварія; вихід — лише повний перезапуск */
} actuator_state_t;

typedef enum {
    FAULT_NONE = 0,
    FAULT_BAD_TOKEN,      /* запит без валідного токена */
    FAULT_SEQUENCE,       /* виклик у неприпустимому стані */
    FAULT_ARM_TIMEOUT,    /* послідовність узяття під силу не завершилась */
    FAULT_VOLTAGE,        /* напруга батареї поза вікном */
    FAULT_OVERTEMP,       /* перегрів силового каскаду */
    FAULT_OVERCURRENT,    /* спрацював компаратор струму */
    FAULT_ESTOP,          /* натиснуто аварійну зупинку */
    FAULT_HEARTBEAT_STALL /* цикл спізнився, меандр розірвано */
} actuator_fault_t;

/*
 * Чекпойнти циклу валідації. Сторож отримує підтвердження лише тоді, коли
 * у циклі пройдено ВСІ чотири й саме в цьому порядку. Часткового кредиту
 * немає: зависання в середині циклу лишає сторожа голодним.
 */
typedef enum {
    CHK_ESTOP  = 1U << 0, /* лінію аварійної зупинки опитано */
    CHK_LIMITS = 1U << 1, /* напругу, температуру й струм зчитано */
    CHK_STATE  = 1U << 2, /* автомат станів відпрацював перехід */
    CHK_OUTPUT = 1U << 3  /* виходи приведено у відповідність до стану */
} actuator_checkpoint_t;

#define CHK_ALL (CHK_ESTOP | CHK_LIMITS | CHK_STATE | CHK_OUTPUT)

typedef struct {
    actuator_state_t state;
    actuator_fault_t fault;
    uint32_t arm_request_us;    /* мітка часу входу в послідовність */
    uint32_t hb_last_toggle_us; /* мітка часу останнього фронту меандру */
    uint16_t current_pwm;
    uint8_t  checkpoints;       /* набір пройдених чекпойнтів цього циклу */
    bool     hb_phase;
} safe_actuator_t;

/* Приводить виходи в нуль і структуру в стан DISARMED. Викликається до
 * дозволу периферійних виходів. */
void safe_actuator_init(safe_actuator_t *drv);

/* Запит на взяття під силу. Хибний токен або виклик не з DISARMED —
 * це порушення протоколу, і воно веде в FAULT, а не просто у відмову. */
bool safe_actuator_request_arm(safe_actuator_t *drv, uint32_t token);

/* Штатне зняття сили. Стан FAULT не скидає — з нього виходу немає. */
void safe_actuator_disarm(safe_actuator_t *drv);

/* Один цикл: опитування безпеки, перехід автомата, виходи, годування
 * сторожа. Викликати не рідше, ніж раз на HEARTBEAT_HALF_PERIOD_US. */
void safe_actuator_process_cycle(safe_actuator_t *drv, uint16_t target_pwm);

static inline actuator_state_t safe_actuator_state(const safe_actuator_t *drv)
{
    return drv->state;
}

static inline actuator_fault_t safe_actuator_fault(const safe_actuator_t *drv)
{
    return drv->fault;
}

#endif /* SAFE_ACTUATOR_H */
