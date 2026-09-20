class ServoProfiler {
public:
    void setTarget(float target_deg, float speed_deg_s) {
        target_deg_ = target_deg;
        speed_deg_s_ = speed_deg_s;
    }

    void update(MicroServo& servo, float dt_s) {
        float current = servo.getCurrentAngle();
        float diff = target_deg_ - current;
        if (std::abs(diff) < 0.01f) return;

        float max_step = speed_deg_s_ * dt_s;
        if (std::abs(diff) <= max_step) {
            servo.setAngle(target_deg_);
        } else {
            servo.setAngle(current + std::copysign(max_step, diff));
        }
    }
private:
    float target_deg_{90.0f};
    float speed_deg_s_{60.0f};
};
