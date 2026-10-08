#ifndef MOTION_PROFILE_HPP
#define MOTION_PROFILE_HPP

namespace rc_servo {

/**
 * @brief Клас для розрахунку плавної траєкторії позиціонування вала сервоприводу.
 *
 * Використовує трапецеїдальний профіль швидкості з обмеженням максимальної кутової
 * швидкості та прискорення. Це запобігає зрізанню зубів пластмасових чи металевих
 * шестерень редуктора та захищає джерело живлення від просідання напруги через
 * пускові струми двигуна.
 */
class MotionProfiler {
public:
    MotionProfiler();
    MotionProfiler(float maxVelocityDegPerSec, float maxAccelDegPerSec2);

    /**
     * @brief Встановлення кінематичних обмежень руху.
     * @param maxVelocityDegPerSec Гранична кутова швидкість (град/с)
     * @param maxAccelDegPerSec2 Граничне кутове прискорення (град/с²)
     */
    void setLimits(float maxVelocityDegPerSec, float maxAccelDegPerSec2);

    /**
     * @brief Встановлення цільового кута позиціонування.
     */
    void setTargetAngle(float targetDeg);

    /**
     * @brief Розрахунок наступного проміжного кута за дискретний квант часу dtSec.
     * @param dtSec Інтервал часу з моменту попереднього розрахунку (секунди)
     * @return Поточний обчислений кут (градуси)
     */
    float update(float dtSec);

    /**
     * @brief Миттєве скидання поточного та цільового кута без генерації руху.
     */
    void reset(float currentAngleDeg);

    float getCurrentAngle() const { return m_currentAngle; }
    float getTargetAngle() const { return m_targetAngle; }
    float getCurrentVelocity() const { return m_currentVelocity; }
    bool isTargetReached() const;

private:
    float m_currentAngle{90.0f};
    float m_targetAngle{90.0f};
    float m_currentVelocity{0.0f};
    float m_maxVelocity{180.0f}; // Максимальна швидкість (°/с)
    float m_maxAccel{720.0f};    // Максимальне прискорення (°/с²)
};

} // namespace rc_servo

#endif // MOTION_PROFILE_HPP
