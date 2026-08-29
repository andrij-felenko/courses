#ifndef BSP_DVFS_H
#define BSP_DVFS_H

#include "clock.h"

/*
 * Динамічна зміна частоти на ходу (DVFS).
 * Униз: 168 МГц PLL -> 16 МГц HSI, напруга ядра Scale 3, Flash 0 WS.
 * Угору: дзеркально. Порядок кроків строго зворотний — усе, що дозволяє
 * швидкість, робиться до її підняття, і після її зниження.
 */

clock_status_t dvfs_enter_low_power(void);
clock_status_t dvfs_enter_full_speed(void);

#endif /* BSP_DVFS_H */
