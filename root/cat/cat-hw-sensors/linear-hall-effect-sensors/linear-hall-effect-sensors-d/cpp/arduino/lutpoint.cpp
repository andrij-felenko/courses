#include <Arduino.h>

struct LutPoint {
    float field_mt;
    float distance_mm;
};

const int LUT_SIZE = 5;
const LutPoint calibLUT[LUT_SIZE] = {
    {100.0f,  1.0f},
    { 60.0f,  3.0f},
    { 35.0f,  6.0f},
    { 20.0f, 10.0f},
    { 10.0f, 15.0f}
};

// Polynomial coefficients: d(B) = c0 + c1*B + c2*B^2
const float c0 = 22.45f;
const float c1 = -0.385f;
const float c2 = 0.0017f;

float interpolateLutDistance(float field_mt) {
    if (field_mt >= calibLUT[0].field_mt) return calibLUT[0].distance_mm;
    if (field_mt <= calibLUT[LUT_SIZE - 1].field_mt) return calibLUT[LUT_SIZE - 1].distance_mm;

    for (int i = 0; i < LUT_SIZE - 1; i++) {
        if (field_mt <= calibLUT[i].field_mt && field_mt >= calibLUT[i + 1].field_mt) {
            float b1 = calibLUT[i].field_mt;
            float b2 = calibLUT[i + 1].field_mt;
            float d1 = calibLUT[i].distance_mm;
            float d2 = calibLUT[i + 1].distance_mm;
            return d1 + (field_mt - b1) * (d2 - d1) / (b2 - b1);
        }
    }
    return 0.0f;
}

float polynomialDistance(float field_mt) {
    return c0 + (c1 * field_mt) + (c2 * field_mt * field_mt);
}

void setup() {
    Serial.begin(115200);
    float test_field = 45.0f; // 45 mT test input
    float dist_lut = interpolateLutDistance(test_field);
    float dist_poly = polynomialDistance(test_field);

    Serial.print("Field: "); Serial.print(test_field); Serial.println(" mT");
    Serial.print("LUT Distance: "); Serial.print(dist_lut); Serial.println(" mm");
    Serial.print("Poly Distance: "); Serial.print(dist_poly); Serial.println(" mm");
}

void loop() {}
