#include "servo_tester.h"

int main(void) {
    servo_tester_t tester;
    uint32_t system_ticks_ms = 0;

    servo_tester_hw_init();
    servo_tester_init(&tester);

    servo_tester_calibrate_esc(&tester);

    while (1) {
        system_ticks_ms += 10;
        bool raw_button_pin = false;
        
        servo_tester_update(&tester, system_ticks_ms, raw_button_pin);
    }

    return 0;
}
