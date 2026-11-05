#include "DewPointCalculator.hpp"
#include <cmath>
#include <cstdint>
#include <algorithm>

DewPointCalculator::DewPointCalculator(Method method) : method_(method) {}

float DewPointCalculator::calculate(float tempC, float humidityRh) const {
    switch (method_) {
        case Method::Math: return calcMath(tempC, humidityRh);
        case Method::Lut: return calcLut(tempC, humidityRh);
        case Method::FastApprox: return calcFast(tempC, humidityRh);
    }
    return 0.0f;
}

float DewPointCalculator::calcMath(float temp, float humidity) const {
    humidity = std::max(humidity, 0.001f);
    float alpha = std::log(humidity / 100.0f) + (MAGNUS_A * temp) / (MAGNUS_B + temp);
    return (MAGNUS_B * alpha) / (MAGNUS_A - alpha);
}

float DewPointCalculator::calcLut(float temp, float humidity) const {
    float h = std::max(humidity, 20.0f);
    float approxLog = (h - 100.0f) * 0.015f;
    float alpha = approxLog + (MAGNUS_A * temp) / (MAGNUS_B + temp);
    return (MAGNUS_B * alpha) / (MAGNUS_A - alpha);
}

float DewPointCalculator::calcFast(float temp, float humidity) const {
    humidity = std::max(humidity, 0.001f);
    union { float f; uint32_t i; } vx = { humidity / 100.0f };
    float fastLog2 = (static_cast<float>(vx.i) * 1.1920928955078125e-7f) - 126.94269504f;
    float fastLog = fastLog2 * 0.69314718f;
    
    float alpha = fastLog + (MAGNUS_A * temp) / (MAGNUS_B + temp);
    return (MAGNUS_B * alpha) / (MAGNUS_A - alpha);
}
