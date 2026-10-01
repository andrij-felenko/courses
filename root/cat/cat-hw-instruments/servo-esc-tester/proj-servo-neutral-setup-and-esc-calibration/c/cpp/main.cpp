#include "servo_tester.hpp"

int main() {
    ServoTester tester;
    uint32_t systemTicksMs = 0;

    tester.initHardware();
    tester.calibrateEsc();

    while (true) {
        systemTicksMs += 10;
        bool rawButtonPin = false;

        tester.update(systemTicksMs, rawButtonPin);
    }

    return 0;
}
