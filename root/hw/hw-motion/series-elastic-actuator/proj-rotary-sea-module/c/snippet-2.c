/* Цикл переривання 1 кГц: замкнене ПІД-регулювання крутного моменту */
void Sea_UpdateController_1kHz(void) {
    uint16_t raw_m = Sea_ReadEncoderSPI(cs_port_m, cs_pin_m);
    uint16_t raw_o = Sea_ReadEncoderSPI(cs_port_o, cs_pin_o);
    
    float th_m = ((float)raw_m * 2.0f * 3.14159265f) / 16384.0f;
    float th_o = ((float)raw_o * 2.0f * 3.14159265f) / 16384.0f;
    
    current_state.deflection_rad = (th_o - th_m) - zero_offset;
    current_state.torque_nm = SPRING_STIFFNESS_NM_RAD * current_state.deflection_rad;
    
    /* Захист від механічного перевантаження пружини */
    if (fabsf(current_state.torque_nm) > MAX_TORQUE_LIMIT_NM) {
        current_state.is_overloaded = true;
        Sea_SetMotorCurrentQ(0.0f);
        return;
    }
    
    float error = desired_torque - current_state.torque_nm;
    torque_integral += error * 0.001f;
    /* Anti-windup обмеження інтегратора */
    if (torque_integral > 5.0f) torque_integral = 5.0f;
    if (torque_integral < -5.0f) torque_integral = -5.0f;
    
    float deriv = (error - prev_torque_error) / 0.001f;
    prev_torque_error = error;
    
    float cmd_torque = (KP_TORQUE * error) + (KI_TORQUE * torque_integral) + (KD_TORQUE * deriv);
    float i_q_target = cmd_torque / (TORQUE_CONSTANT_KT * GEAR_RATIO);
    
    Sea_SetMotorCurrentQ(i_q_target);
}
