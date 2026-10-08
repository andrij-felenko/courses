#include <cmath>

class TiltCompensatedCompass {
public:
    static double computeTrueHeading(
        double bx, double by, double bz,
        double ax, double ay, double az,
        double declinationDeg
    ) {
        const double roll = std::atan2(ay, az);
        const double pitch = std::atan2(-ax, std::sqrt(ay * ay + az * az));

        const double sinRoll = std::sin(roll);
        const double cosRoll = std::cos(roll);
        const double sinPitch = std::sin(pitch);
        const double cosPitch = std::cos(pitch);

        const double bxH = bx * cosPitch + by * sinRoll * sinPitch + bz * cosRoll * sinPitch;
        const double byH = by * cosRoll - bz * sinRoll;

        double headingDeg = std::atan2(byH, bxH) * (180.0 / M_PI);
        if (headingDeg < 0.0) {
            headingDeg += 360.0;
        }

        double trueHeading = headingDeg + declinationDeg;
        if (trueHeading >= 360.0) {
            trueHeading -= 360.0;
        } else if (trueHeading < 0.0) {
            trueHeading += 360.0;
        }

        return trueHeading;
    }
};
