#include <Arduino.h>

enum class RangeStatus {
    Ok,
    BlindZone,
    TooFar
};

struct LutNode {
    uint16_t voltage_mv;
    uint16_t distance_mm;
};

class SharpGP2Y0A21 {
private:
    static constexpr LutNode LUT[] = {
        {3100, 100}, {2500, 120}, {2000, 150}, {1550, 200},
        {1250, 250}, {1050, 300}, {800,  400}, {650,  500},
        {520,  600}, {450,  700}, {400,  800}
    };
    static constexpr size_t LUT_SIZE = sizeof(LUT) / sizeof(LUT[0]);

public:
    RangeStatus calculateDistance(uint16_t voltage_mv, uint16_t &out_distance_mm) const {
        if (voltage_mv > LUT[0].voltage_mv) {
            out_distance_mm = LUT[0].distance_mm;
            return RangeStatus::BlindZone;
        }

        if (voltage_mv < LUT[LUT_SIZE - 1].voltage_mv) {
            out_distance_mm = LUT[LUT_SIZE - 1].distance_mm;
            return RangeStatus::TooFar;
        }

        for (size_t i = 0; i < LUT_SIZE - 1; ++i) {
            if (voltage_mv <= LUT[i].voltage_mv && voltage_mv >= LUT[i + 1].voltage_mv) {
                int32_t v1 = LUT[i].voltage_mv;
                int32_t v2 = LUT[i + 1].voltage_mv;
                int32_t d1 = LUT[i].distance_mm;
                int32_t d2 = LUT[i + 1].distance_mm;

                int32_t dist = d1 + ((static_cast<int32_t>(voltage_mv) - v1) * (d2 - d1)) / (v2 - v1);
                out_distance_mm = static_cast<uint16_t>(dist);
                return RangeStatus::Ok;
            }
        }

        return RangeStatus::TooFar;
    }
};
