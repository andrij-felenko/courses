#include <cmath>

struct Vector3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

class CompassCalculator {
public:
    static float calculateHeading(const Vector3D& magRaw, 
                                  const Vector3D& accelRaw, 
                                  const Vector3D& hardIronOffset,
                                  float declinationDegrees = 0.0f) {
        // Калібрування Hard Iron
        const float mx = magRaw.x - hardIronOffset.x;
        const float my = magRaw.y - hardIronOffset.y;
        const float mz = magRaw.z - hardIronOffset.z;

        // Кути крену та тангажу
        const float roll = std::atan2(accelRaw.y, accelRaw.z);
        const float pitch = std::atan2(-accelRaw.x, std::sqrt(accelRaw.y * accelRaw.y + accelRaw.z * accelRaw.z));

        const float cosRoll = std::cos(roll);
        const float sinRoll = std::sin(roll);
        const float cosPitch = std::cos(pitch);
        const float sinPitch = std::sin(pitch);

        // Проекція вектора
        const float xh = mx * cosPitch + mz * sinPitch;
        const float yh = mx * sinRoll * sinPitch + my * cosRoll - mz * sinRoll * cosPitch;

        float heading = std::atan2(yh, xh) * (180.0f / static_cast<float>(M_PI));
        heading += declinationDegrees;

        if (heading < 0.0f) heading += 360.0f;
        if (heading >= 360.0f) heading -= 360.0f;

        return heading;
    }
};
