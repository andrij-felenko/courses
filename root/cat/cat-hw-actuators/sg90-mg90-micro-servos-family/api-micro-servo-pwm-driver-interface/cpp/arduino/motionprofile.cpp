// C++ (Arduino / Embedded C++) - Клас профілювання позиціонування
#include <cmath>

class MotionProfile {
private:
    float currentAngle_ = 0.0f;
    float targetAngle_ = 0.0f;
    float currentSpeed_ = 0.0f;
    float maxSpeed_ = 90.0f;   // град/сек
    float accel_ = 180.0f;     // град/сек^2

public:
    void setTarget(float target) { targetAngle_ = target; }
    void setLimits(float maxSpeed, float accel) {
        maxSpeed_ = maxSpeed;
        accel_ = accel;
    }

    float update(float dt) {
        float error = targetAngle_ - currentAngle_;
        if (std::abs(error) < 0.01f) {
            currentSpeed_ = 0.0f;
            return currentAngle_;
        }

        float stopDist = (currentSpeed_ * currentSpeed_) / (2.0f * accel_);
        float dir = (error > 0.0f) ? 1.0f : -1.0f;

        if (std::abs(error) <= stopDist) {
            currentSpeed_ -= accel_ * dt;
            if (currentSpeed_ < 0.0f) currentSpeed_ = 0.0f;
        } else {
            if (currentSpeed_ < maxSpeed_) {
                currentSpeed_ += accel_ * dt;
                if (currentSpeed_ > maxSpeed_) currentSpeed_ = maxSpeed_;
            }
        }

        currentAngle_ += dir * currentSpeed_ * dt;
        return currentAngle_;
    }

    float getCurrentAngle() const { return currentAngle_; }
};
