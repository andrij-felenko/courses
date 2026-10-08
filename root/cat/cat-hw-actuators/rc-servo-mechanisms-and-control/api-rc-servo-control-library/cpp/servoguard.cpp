#include <Servo.h>

class ServoGuard {
private:
    Servo servo;
    int pin;
    bool attached;

public:
    ServoGuard(int pinNum) : pin(pinNum), attached(false) {}

    ~ServoGuard() {
        release();
    }

    bool begin(int minUs = 1000, int maxUs = 2000) {
        if (servo.attach(pin, minUs, maxUs)) {
            attached = true;
            return true;
        }
        return false;
    }

    void moveTo(int angle) {
        if (attached) {
            servo.write(angle);
        }
    }

    void release() {
        if (attached) {
            servo.detach(); // Зупинка ШІМ та вивільнення таймера
            attached = false;
        }
    }
};
