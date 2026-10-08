#include <Arduino.h>

struct MQ7Config {
    float rL_kOhm = 10.0f;
    float r0_kOhm = 33.0f;
    float vCC = 5.0f;
    float vRef = 5.0f;
    uint32_t adcMax = 1023;
    float coeffA = 19.32f;
    float coeffB = -1.52f;
};

float readPPM(uint32_t adcRaw, float temp, float hum, const MQ7Config& cfg) {
    if (adcRaw == 0 || cfg.r0_kOhm <= 0.0f) return 0.0f;

    float vOut = (static_cast<float>(adcRaw) * cfg.vRef) / static_cast<float>(cfg.adcMax);
    float rS = cfg.rL_kOhm * (cfg.vCC - vOut) / vOut;

    float kFactor = getCorrectionFactor(temp, hum);
    float rSCorr = rS / kFactor;

    float ratio = rSCorr / cfg.r0_kOhm;
    return cfg.coeffA * pow(ratio, cfg.coeffB);
}
