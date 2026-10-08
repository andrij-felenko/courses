#include "compass_calibrator.hpp"
#include <algorithm>
#include <cmath>

namespace {
    constexpr float PI_F = 3.14159265358979323846f;
}

CompassCalibrator::CompassCalibrator() = default;

void CompassCalibrator::startCalibration() {
    m_isCalibrating = true;
    m_minValues = {std::numeric_limits<float>::max(),
                   std::numeric_limits<float>::max(),
                   std::numeric_limits<float>::max()};
    m_maxValues = {std::numeric_limits<float>::lowest(),
                   std::numeric_limits<float>::lowest(),
                   std::numeric_limits<float>::lowest()};
}

void CompassCalibrator::stopCalibration() {
    m_isCalibrating = false;

    // Обчислення зміщення жорсткого заліза (Hard-Iron Offset):
    // offset = (max + min) / 2
    m_hardIronOffset.x = (m_maxValues.x + m_minValues.x) * 0.5f;
    m_hardIronOffset.y = (m_maxValues.y + m_minValues.y) * 0.5f;
    m_hardIronOffset.z = (m_maxValues.z + m_minValues.z) * 0.5f;

    // Обчислення радіусів осей для м'якого заліза (Soft-Iron Scale):
    float deltaX = (m_maxValues.x - m_minValues.x) * 0.5f;
    float deltaY = (m_maxValues.y - m_minValues.y) * 0.5f;
    float deltaZ = (m_maxValues.z - m_minValues.z) * 0.5f;

    // Уникаємо ділення на нуль у разі відсутності руху по осях
    if (deltaX <= 1e-5f) deltaX = 1.0f;
    if (deltaY <= 1e-5f) deltaY = 1.0f;
    if (deltaZ <= 1e-5f) deltaZ = 1.0f;

    // Середній радіус вимірювальної сфери
    float avgDelta = (deltaX + deltaY + deltaZ) / 3.0f;

    // Нормалізовані масштаби м'якого заліза
    m_softIronScale.x = avgDelta / deltaX;
    m_softIronScale.y = avgDelta / deltaY;
    m_softIronScale.z = avgDelta / deltaZ;
}

void CompassCalibrator::setHardIronOffset(const Vector3D& offset) {
    m_hardIronOffset = offset;
}

void CompassCalibrator::setSoftIronScale(const Vector3D& scale) {
    m_softIronScale = scale;
}

void CompassCalibrator::setDeclinationDegrees(float declinationDeg) {
    m_declinationRad = declinationDeg * (PI_F / 180.0f);
}

void CompassCalibrator::updateCalibration(const Vector3D& raw) {
    if (!m_isCalibrating) return;

    m_minValues.x = std::min(m_minValues.x, raw.x);
    m_minValues.y = std::min(m_minValues.y, raw.y);
    m_minValues.z = std::min(m_minValues.z, raw.z);

    m_maxValues.x = std::max(m_maxValues.x, raw.x);
    m_maxValues.y = std::max(m_maxValues.y, raw.y);
    m_maxValues.z = std::max(m_maxValues.z, raw.z);
}

Vector3D CompassCalibrator::correct(const Vector3D& raw) const {
    Vector3D corrected;
    // Формула корекції: (raw - hard_iron_offset) * soft_iron_scale
    corrected.x = (raw.x - m_hardIronOffset.x) * m_softIronScale.x;
    corrected.y = (raw.y - m_hardIronOffset.y) * m_softIronScale.y;
    corrected.z = (raw.z - m_hardIronOffset.z) * m_softIronScale.z;
    return corrected;
}

float CompassCalibrator::calculateHeading(const Vector3D& corrected) const {
    // Математичне обчислення кута напрямку в 2D площині (X-Y)
    // У QMC5883L кут обчислюється через atan2(y, x)
    float headingRad = std::atan2(corrected.y, corrected.x);

    // Додаємо локальне географічне магнітне схилення
    headingRad += m_declinationRad;

    // Зведення до діапазону [0, 2*PI)
    if (headingRad < 0.0f) {
        headingRad += 2.0f * PI_F;
    } else if (headingRad >= 2.0f * PI_F) {
        headingRad -= 2.0f * PI_F;
    }

    // Переведення в градуси [0, 360°)
    float headingDeg = headingRad * (180.0f / PI_F);
    return headingDeg;
}

float CompassCalibrator::process(const Vector3D& raw, Vector3D& corrected) {
    if (m_isCalibrating) {
        updateCalibration(raw);
    }
    corrected = correct(raw);
    return calculateHeading(corrected);
}
