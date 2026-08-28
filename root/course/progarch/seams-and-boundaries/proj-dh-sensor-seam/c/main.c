/* sensor.h — заголовок чужої бібліотеки (єдине, що ти маєш) */
double sensor_read(void);        /* повертає °C; тіло — у закритій libsensor.so */

/* hub.c — твій код. Давач кличеться НАПРЯМУ, без параметра-інтерфейса. */
#include <stdio.h>
#include "sensor.h"

int main(void) {
    double t = sensor_read();                    /* ← прямий виклик у чужу бібліотеку */
    printf("%.1f°C → %s\n", t, t < 20.0 ? "гріти" : "не гріти");
    return 0;
}
