#include <stdint.h>

#define PT_WAITING 0
#define PT_DONE    1

typedef struct { unsigned short line; } pt_t;

#define PT_INIT(pt)        ((pt)->line = 0)
#define PT_BEGIN(pt)       switch ((pt)->line) { case 0:
#define PT_END(pt)         } (pt)->line = 0; return PT_DONE
#define PT_WAIT_UNTIL(pt, cond)               \
    do { (pt)->line = __LINE__; case __LINE__: \
         if (!(cond)) return PT_WAITING; } while (0)

extern uint32_t millis(void);          // час від старту, мс (платформа)
extern void led_write(int on);         // увімкнути/вимкнути світлодіод
extern int  sensor_read(void);         // миттєве значення давача
extern void publish(int value);        // віддати значення далі

// таймер-помічник: «чи минуло ms від мітки t0?»
static inline int timer_expired(uint32_t t0, uint32_t ms) {
    return (uint32_t)(millis() - t0) >= ms;
}
