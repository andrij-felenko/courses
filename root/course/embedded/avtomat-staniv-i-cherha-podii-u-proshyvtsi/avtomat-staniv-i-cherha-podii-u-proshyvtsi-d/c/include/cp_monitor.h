#ifndef EVSE_CP_MONITOR_H
#define EVSE_CP_MONITOR_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Класифікація лінії Control Pilot за стандартом IEC 61851-1 / SAE J1772.
 * Модуль перетворює сирі мілівольти АЦП на подію зміни класу — і тільки на
 * зміну: доки автомобіль тримає ті самі +6 В, черга лишається порожньою.
 */
typedef enum {
    CP_UNKNOWN = 0, /* ще не набрано достатньо однакових вимірів */
    CP_A,           /* +12 В, кабель не підключено */
    CP_B,           /* +9 В, штекер у гнізді, енергії не просять */
    CP_C,           /* +6 В, автомобіль замкнув ключ і просить струм */
    CP_INVALID      /* обрив, коротке, зниклий діод, збита частота */
} cp_class_t;

void cp_monitor_init(void);

/*
 * Один вимір. Викликається з головного циклу по EVT_TICK_10MS, а не з
 * переривання: усередині кілька читань АЦП і арифметика, тобто десятки
 * мікросекунд — забагато для обробника.
 */
void cp_monitor_sample(void);

cp_class_t  cp_monitor_class(void);
const char *cp_class_name(cp_class_t c);

#endif /* EVSE_CP_MONITOR_H */
