#include <stdint.h>
#include <stdbool.h>

typedef enum {
    BMS_OFF = 0,
    BMS_PRECHARGE,
    BMS_ON,
    BMS_FAULT
} bms_state_t;

// Причина відмови — щоб зафіксувати ПЕРШУ, що сталася, і не загубити її.
typedef enum {
    FAULT_NONE = 0,
    FAULT_CELL_PROTECT,     // спрацювала перша лінія (монітор комірок)
    FAULT_SECONDARY,        // спрацювала друга, незалежна лінія
    FAULT_PRECHARGE_TIMEOUT,// ємність не зарядилася вчасно (коротке в навантаженні?)
    FAULT_CONTACTOR_STUCK,  // контактор не послухався команди (зварений?)
    FAULT_POWER_FAIL        // провал живлення самого BMS під час роботи
} fault_code_t;

typedef struct {
    bms_state_t  state;
    fault_code_t fault;       // != FAULT_NONE ⇔ ми у FAULT і чому
    uint32_t     t_enter;     // мітка часу входу в поточний стан (мс)
    uint8_t      confirm_cnt; // лічильник підтвердження для дребезгу
} bms_t;

static bms_t bms = { .state = BMS_OFF, .fault = FAULT_NONE };
