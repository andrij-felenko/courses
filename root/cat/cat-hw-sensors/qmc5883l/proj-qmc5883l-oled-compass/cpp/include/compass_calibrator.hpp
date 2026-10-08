#ifndef COMPASS_CALIBRATOR_HPP
#define COMPASS_CALIBRATOR_HPP

#include "qmc5883l.hpp"
#include <limits>

/// @brief Клас для автокалібрування магнітометра та обчислення азимута
class CompassCalibrator {
public:
    CompassCalibrator();

    /// @brief Перекласти калибратор у режим збору екстремумів (початок автокалібрування)
    void startCalibration();

    /// @brief Завершити режим збору та обчислити параметри Hard-Iron і Soft-Iron
    void stopCalibration();

    /// @brief Чи перебуває модуль у процесі активного калібрування
    bool isCalibrating() const { return m_isCalibrating; }

    /// @brief Ручне встановлення коефіцієнтів зміщення жорсткого заліза (Hard-Iron)
    void setHardIronOffset(const Vector3D& offset);

    /// @brief Ручне встановлення коефіцієнтів масштабування м'якого заліза (Soft-Iron)
    void setSoftIronScale(const Vector3D& scale);

    /// @brief Встановлення локального магнітного схилення у градусах (Magnetic Declination)
    /// @param declinationDeg Схилення в градусах (наприклад, +6.5° для Києва)
    void setDeclinationDegrees(float declinationDeg);

    /// @brief Оновити межі екстремумів при виконанні обертання сенсора на 360°
    /// @param raw Сирі показники магнітометра
    void updateCalibration(const Vector3D& raw);

    /// @brief Застосувати калібрувальні коефіцієнти до сирого вектора
    /// @param raw Вхідні виміри магнітометра
    /// @return Відкалібрований вектор магнітного поля
    Vector3D correct(const Vector3D& raw) const;

    /// @brief Обчислити кут напрямку (азимут) у діапазоні [0, 360°)
    /// @param corrected Відкалібрований вектор магнітного поля
    /// @return Азимут у градусах (0° = Північ, 90° = Схід, 180° = Південь, 270° = Захід)
    float calculateHeading(const Vector3D& corrected) const;

    /// @brief Повний цикл обробки: корекція вектора та обчислення кута
    /// @param raw Сирий вектор з магнітометра
    /// @param corrected Вихідний відкалібрований вектор
    /// @return Поточний азимут у градусах
    float process(const Vector3D& raw, Vector3D& corrected);

private:
    bool m_isCalibrating{false};

    // Накопичені екстремуми для кожної з осей
    Vector3D m_minValues{std::numeric_limits<float>::max(),
                         std::numeric_limits<float>::max(),
                         std::numeric_limits<float>::max()};
    Vector3D m_maxValues{std::numeric_limits<float>::lowest(),
                         std::numeric_limits<float>::lowest(),
                         std::numeric_limits<float>::lowest()};

    // Розраховані коефіцієнти Hard-Iron та Soft-Iron
    Vector3D m_hardIronOffset{0.0f, 0.0f, 0.0f};
    Vector3D m_softIronScale{1.0f, 1.0f, 1.0f};

    // Магнітне схилення у радіанах
    float m_declinationRad{0.0f};
};

#endif // COMPASS_CALIBRATOR_HPP
