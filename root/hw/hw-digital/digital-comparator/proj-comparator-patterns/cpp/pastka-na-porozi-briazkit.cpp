#include <stdint.h>
#include <stdbool.h>

// Два пороги в одиницях коду АЦП; TH_HI > TH_LO — це і є ширина мертвої зони.
#define TH_HI  2600u
#define TH_LO  2400u

static bool tripped = false;          // пам'ять стану між викликами

bool threshold_hysteresis(uint16_t x) {
    if (!tripped) {
        if (x > TH_HI) tripped = true;    // увімкнення — лише вгорі
    } else {
        if (x < TH_LO) tripped = false;   // вимкнення — лише внизу
    }
    return tripped;
}
