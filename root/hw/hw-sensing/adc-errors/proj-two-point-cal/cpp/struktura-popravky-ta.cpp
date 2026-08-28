#include <Preferences.h>

struct Calib {
    int   rawLo, rawHi;   // сирі коди (12-бітних, 0–4095)
    float vLo,   vHi;     // відповідні напруги у вольтах
};

// Застосувати поправку: raw → вольти
float applyCalib(const Calib& c, int raw) {
    if (c.rawHi == c.rawLo)              // захист від ділення на нуль
        return raw * (3.3f / 4095.0f);  // fallback: сира заводська шкала
    float slope = (c.vHi - c.vLo) / float(c.rawHi - c.rawLo);
    return c.vLo + slope * float(raw - c.rawLo);
}
