#include "core_cm4.h"     // CMSIS: структура MPU, біти-маски RASR/RBAR
#include <stdint.h>

#define TASK_REGIONS  3   // скільки областей віддано під одну задачу (5,6,7)

// один запис області у вже готовому для заливки вигляді:
// саме ті значення, що підуть у RBAR і RASR
typedef struct {
    uint32_t rbar;        // база + біт VALID + номер області (REGION)
    uint32_t rasr;        // ENABLE | розмір | права | XN | атрибути
} MpuRegion;

typedef struct {
    uint32_t   *sp;                    // збережений указник стека задачі
    MpuRegion   regions[TASK_REGIONS]; // ГОТОВИЙ опис її областей MPU
} TCB;

static TCB  tasks[2];        // дві задачі для прикладу
static TCB *current;         // хто біжить зараз
