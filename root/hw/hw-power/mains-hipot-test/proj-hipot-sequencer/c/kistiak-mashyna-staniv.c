#include <stdint.h>
#include <stdbool.h>

typedef enum {
    ST_IDLE, ST_GROUND_BOND, ST_INSUL_RES,
    ST_HIPOT_RAMP, ST_HIPOT_DWELL, ST_DISCHARGE, ST_PASS, ST_FAIL
} state_t;

typedef enum { V_NONE, V_PASS, V_FAIL } verdict_t;

typedef struct {
    state_t   state;
    verdict_t verdict;
    uint32_t  t_ms;        // час у поточному стані, мс
    uint16_t  dac_code;    // поточний код ЦАП (команда напруги джерела)
    uint16_t  dac_target;  // код на кінець наростання
    uint16_t  dac_step;    // приріст коду за один 1-мс такт
    const char *fail_reason;
} hipot_t;

// Прапорці, спільні з обробником переривання (тому volatile):
volatile bool     g_arc_armed   = false;  // детектор дуги активний (уся HV-фаза)
volatile bool     g_level_armed = false;  // абсолютний поріг активний (лише витримка)
volatile uint16_t g_i_limit     = 0;      // поріг струму в кодах АЦП
volatile uint8_t  g_trip        = 0;      // 1 = тригер спрацював (ставить ISR)

// Межа апаратури — реалізує плата (contactor, ЦАП, шунт, реле баласту):
extern bool  hv_is_live(void);
extern void  hv_off(void);           // мʼяко зняти джерело
extern void  hv_off_hard(void);      // найшвидший розрив, безпечно з ISR
extern void  hv_enable(void);
extern void  dac_write(uint16_t code);
extern uint16_t hv_meas_volts(void); // зчитати вихідну напругу (для розряду)
extern void  bleed_on(void);
extern void  bleed_off(void);
extern bool  enclosure_open(void);
extern bool  button_l(void), button_r(void);
extern float ground_bond_ohms(void);
extern float insul_res_megohm(void);
extern uint16_t volts_to_code(uint16_t v);
extern void  latch_fault(const char *why);
extern void  log_result(const hipot_t *h);

#define DWELL_MS              1000     // витримка гіпоту (конвеєр: 1 с)
#define DISCHARGE_TIMEOUT_MS  500

static void enter(hipot_t *h, state_t s) { h->state = s; h->t_ms = 0; }

static void abort_test(hipot_t *h, const char *why) {
    hv_off_hard();
    h->verdict = V_FAIL;
    h->fail_reason = why;
    g_trip = 0;                 // прапорець спожито
    enter(h, ST_DISCHARGE);     // навіть у провалі — СПЕРШУ розрядити
}
