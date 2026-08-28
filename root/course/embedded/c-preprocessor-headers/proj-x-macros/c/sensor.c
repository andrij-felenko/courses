// sensor.c
#include "sensor_regs.h"

// Адреси регістрів: REG_##name = addr,
#define X(name, addr, def)   REG_##name = addr,
typedef enum { SENSOR_REGS(X) } sensor_reg_t;
#undef X

// Імена — стрингізуємо САМ ідентифікатор через #, дублювати рядок не треба:
#define X(name, addr, def)   [REG_##name] = #name,
static const char *const REG_NAME[] = { SENSOR_REGS(X) };
#undef X
