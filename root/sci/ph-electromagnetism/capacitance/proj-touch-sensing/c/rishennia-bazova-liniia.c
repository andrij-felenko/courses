#include <stdint.h>

#define THRESH_ON   80   // поріг увімкнення (в одиницях сирого відліку)
#define THRESH_OFF  40   // поріг вимкнення нижчий — це і є гістерезис
#define M_MATCHES   3    // стільки збігів поспіль треба на визнання натиску
#define BASE_SHIFT  6    // база повзе з темпом 1/64 = 2⁻⁶

typedef enum { RELEASED, PRESSED } touch_state_t;

static touch_state_t state    = RELEASED;
static int32_t       baseline = 0;   // «стан без дотику» — повільне середнє
static uint8_t       matches  = 0;   // лічильник збігів поспіль

// Викликати рівно раз на ~10 мс (наприклад, з таймерного переривання).
void touch_poll(void)
{
    int32_t s = (int32_t)raw_reading();

    if (state == RELEASED)
        baseline += (s - baseline) >> BASE_SHIFT;   // повзе слідом за дрейфом

    int32_t d = s - baseline;                       // відхилення від базової лінії

    if (state == RELEASED) {
        if (d > THRESH_ON) {
            if (++matches >= M_MATCHES) {           // М збігів поспіль
                state   = PRESSED;
                matches = 0;
            }
        } else {
            matches = 0;                            // поодинокий викид — лічильник скидаємо
        }
    } else {                                        // PRESSED
        if (d < THRESH_OFF)
            state = RELEASED;   // база заморожена, поки натиснуто, тож палець не «з'їдається»
    }
}
