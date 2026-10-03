#include "foc_controller.hpp"

namespace foc {

FOCController::FOCController(Tim1PwmDriver& pwm, AdcOpampDriver& adc)
    : pwm_driver_(pwm), adc_driver_(adc),
      pi_d_(2.0f, 500.0f, 0.00005f, -12.0f, 12.0f),
      pi_q_(2.0f, 500.0f, 0.00005f, -12.0f, 12.0f) {}

bool FOCController::init() {
    if (!pwm_driver_.init()) return false;
    if (!adc_driver_.init()) return false;
    if (!cordic_math_.init()) return false;

    // Встановлення максимальних напруг для ПІ-регуляторів (Vdc / sqrt(3))
    float max_voltage = bus_voltage_v_ * 0.577350269f;
    pi_d_.setOutputLimits(-max_voltage, max_voltage);
    pi_q_.setOutputLimits(-max_voltage, max_voltage);

    return true;
}

void FOCController::start() {
    state_ = ControlState::CALIBRATING;

    // Виконання калібрування нулів струмових датчиків
    adc_driver_.calibrateOffsets(1024);

    pi_d_.reset();
    pi_q_.reset();

    pwm_driver_.start();
    state_ = ControlState::RUNNING;
}

void FOCController::stop() {
    pwm_driver_.stop();
    state_ = ControlState::STOPPED;
}

void FOCController::setTargetCurrents(float id_ref, float iq_ref) {
    target_id_ = id_ref;
    target_iq_ = iq_ref;
}

void FOCController::setElectricalAngle(float angle_rad) {
    electrical_angle_rad_ = angle_rad;
}

void FOCController::updateInterruptHandler() {
    if (state_ != ControlState::RUNNING) {
        return;
    }

    // 1. Отримання оцифрованих струмів фаз A та B від аналогового драйвера
    float i_a = 0.0f, i_b = 0.0f;
    adc_driver_.getPhaseCurrents(i_a, i_b);

    // 2. Апаратне обчислення sin/cos через CORDIC
    SinCos sincos = cordic_math_.calculateSinCos(electrical_angle_rad_);

    // 3. Пряме перетворення Кларка: (Ia, Ib) -> (I_alpha, I_beta)
    Vector2D i_alphabeta = cordic_math_.clarkeTransform(i_a, i_b);

    // 4. Пряме перетворення Парка: (I_alpha, I_beta) -> (I_d, I_q)
    Vector2D i_dq = cordic_math_.parkTransform(i_alphabeta.x, i_alphabeta.y,
                                                sincos.sin_val, sincos.cos_val);
    measured_id_ = i_dq.x;
    measured_iq_ = i_dq.y;

    // 5. Виконання алгоритму ПІ-регулювання струмів d та q
    float v_d = pi_d_.update(target_id_, measured_id_);
    float v_q = pi_q_.update(target_iq_, measured_iq_);

    // 6. Зворотне перетворення Парка: (V_d, V_q) -> (V_alpha, V_beta)
    Vector2D v_alphabeta = cordic_math_.invParkTransform(v_d, v_q,
                                                         sincos.sin_val, sincos.cos_val);

    // 7. Зворотне перетворення Кларка та розрахунок коефіцієнтів ШІМ (SVPWM)
    float duty_a = 0.5f, duty_b = 0.5f, duty_c = 0.5f;
    cordic_math_.invClarkeSVPWM(v_alphabeta.x, v_alphabeta.y, bus_voltage_v_,
                                duty_a, duty_b, duty_c);

    // 8. Оновлення регістрів порівняння силового ШІМ-таймера TIM1
    pwm_driver_.setDutyCycles(duty_a, duty_b, duty_c);
}

} // namespace foc
