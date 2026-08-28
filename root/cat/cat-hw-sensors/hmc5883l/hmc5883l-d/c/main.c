#include <math.h>

// mx, my — сирі відліки магнетометра по X та Y (з поправкою калібрування)
float heading_deg(int16_t mx, int16_t my, float declination_deg) {
    float heading = atan2f((float)my, (float)mx);   // радіани
    heading += declination_deg * (float)M_PI / 180.0f;   // магнітне схилення

    // Загорнути в діапазон 0 … 2π
    if (heading < 0)            heading += 2.0f * (float)M_PI;
    if (heading > 2*M_PI)       heading -= 2.0f * (float)M_PI;

    return heading * 180.0f / (float)M_PI;   // градуси 0 … 360
}
