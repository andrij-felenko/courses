#include <math.h>

// Радіус Землі — середній (IUGG), метри. Він мінімізує середньоквадратичну
// похибку дуги проти реального геоїда; для навігації цієї точності з надлишком.
#define EARTH_RADIUS_M   6371000.0

static inline double deg2rad(double d) { return d * (M_PI / 180.0); }

// haversin(x) = sin²(x/2). Виносимо окремо — так формула читається один-в-один.
static inline double haversin(double x_rad) {
    double s = sin(x_rad * 0.5);
    return s * s;
}

// Відстань по поверхні (метри) між (lat1,lon1) і (lat2,lon2) за гаверсинусами.
double great_circle_m(double lat1, double lon1, double lat2, double lon2) {
    double phi1 = deg2rad(lat1);
    double phi2 = deg2rad(lat2);
    double dphi = deg2rad(lat2 - lat1);   // Δφ
    double dlam = deg2rad(lon2 - lon1);   // Δλ

    // a = sin²(Δφ/2) + cosφ₁·cosφ₂·sin²(Δλ/2)  — гаверсинус центрального кута.
    double a = haversin(dphi)
             + cos(phi1) * cos(phi2) * haversin(dlam);

    // c = 2·atan2(√a, √(1−a)) — сам кут θ, стійко на всьому діапазоні.
    double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));

    return EARTH_RADIUS_M * c;             // d = R·θ
}
