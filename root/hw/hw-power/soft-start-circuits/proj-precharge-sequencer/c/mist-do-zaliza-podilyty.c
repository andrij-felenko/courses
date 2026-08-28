#include <stdint.h>
#include <stdbool.h>

// ── Параметри під конкретну шину ──────────────────────────────────────
#define VBUS_NOMINAL_mV     400000u   // очікувана напруга входу (400 В)
#define PRECHARGE_TARGET_pct    95u   // поріг «заряджено», % від Uвх
#define PRECHARGE_TIMEOUT_ms   500u   // не дійшло за цей час -> аварія
#define CONTACTOR_SETTLE_ms     40u   // час на злипання головного контактора
#define TICK_ms                  5u   // період виклику precharge_tick()

// Вимірювальний тракт: дільник 400 В -> трохи менше 3.3 В на 12-біт АЦП.
#define ADC_VREF_mV           3300u
#define ADC_FULLSCALE         4095u   // 2^12 − 1
#define DIV_RTOP_ohm        990000u   // верхнє плече дільника
#define DIV_RBOT_ohm          8200u   // нижнє плече

// Найбільша правдоподібна напруга: вище -> несправність давача/дільника.
#define VBUS_MAX_PLAUSIBLE_mV (VBUS_NOMINAL_mV + VBUS_NOMINAL_mV / 4u)
