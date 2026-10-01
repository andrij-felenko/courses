#include <Arduino.h>

enum class Pt100WireMode { TwoWire = 2, ThreeWire = 3, FourWire = 4 };
enum class Pt100Class { ClassA, ClassB };

struct Pt100Config {
    Pt100WireMode wireMode;
    Pt100Class sensorClass;
    float rRefOhms;
    float excitationCurrentUa;
    uint8_t adcBits;
};

class Pt100Driver {
private:
    Pt100Config config;
    bool initialized;

public:
    Pt100Driver() : initialized(false) {}

    bool begin(const Pt100Config& cfg) {
        if (cfg.rRefOhms <= 0.0f) return false;
        config = cfg;
        initialized = true;
        return true;
    }
};
