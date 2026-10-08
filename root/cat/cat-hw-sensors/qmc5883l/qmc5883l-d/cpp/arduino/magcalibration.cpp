#include <Arduino.h>
#include <Wire.h>

struct MagCalibration {
    float offset_x = 0.0f;
    float offset_y = 0.0f;
    float offset_z = 0.0f;
    float scale_x  = 1.0f;
    float scale_y  = 1.0f;
    float scale_z  = 1.0f;
};

class QMC5883LCalibrator {
public:
    static void apply(int16_t rx, int16_t ry, int16_t rz, 
                      const MagCalibration& cal, 
                      float& cx, float& cy, float& cz) {
        // Корегування зсуву та деформації
        cx = (static_cast<float>(rx) - cal.offset_x) * cal.scale_x;
        cy = (static_cast<float>(ry) - cal.offset_y) * cal.scale_y;
        cz = (static_cast<float>(rz) - cal.offset_z) * cal.scale_z;
    }

    static float computeHeadingDeg(float cx, float cy, float declinationDeg = 0.0f) {
        float declinationRad = declinationDeg * (PI / 180.0f);
        float heading = atan2(cy, cx) + declinationRad;
        
        if (heading < 0.0) heading += 2.0 * PI;
        if (heading >= 2.0 * PI) heading -= 2.0 * PI;

        return heading * (180.0 / PI);
    }
};
