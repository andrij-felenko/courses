typedef struct {
    GimbalAxis yaw_axis;
    GimbalAxis roll_axis;
    GimbalAxis pitch_axis;
    
    float target_yaw_rad;
    float target_roll_rad;
    float target_pitch_rad;
    
    float est_yaw_rad;
    float est_roll_rad;
    float est_pitch_rad;
    
    /* Пряма гравітаційна компенсація (Feedforward) */
    float pitch_gravity_ff_v;
} TriaxialGimbalController;

/* Крок швидкісного контуру FOC */
void gimbal_controller_foc_step(GimbalAxis *axis) {
    float s_e = sinf(axis->elec_angle_rad);
    float c_e = cosf(axis->elec_angle_rad);
    
    float u_alpha = -axis->u_q * s_e + axis->u_d * c_e;
    float u_beta  =  axis->u_q * c_e + axis->u_d * s_e;
    
    axis->svpwm = svpwm_generate(u_alpha, u_beta, axis->v_bus);
}

/* Крок каскадного регулятора осі */
void gimbal_axis_cascade_update(GimbalAxis *axis, float target_angle, float current_angle, 
                                float gyro_rate, float feedforward_voltage, float dt) {
    float error_angle = target_angle - current_angle;
    
    while (error_angle > PI_CONST)  error_angle -= TWO_PI;
    while (error_angle < -PI_CONST) error_angle += TWO_PI;
    
    float des_rate = axis->pos_pid.kp * error_angle;
    if (des_rate > axis->pos_pid.out_max) des_rate = axis->pos_pid.out_max;
    if (des_rate < -axis->pos_pid.out_max) des_rate = -axis->pos_pid.out_max;
    
    /* Фільтрація сигналу швидкості від структурного резонансу */
    float filtered_gyro = notch_filter_update(&axis->notch, gyro_rate);
    float rate_error = des_rate - filtered_gyro;
    
    float p_term = axis->rate_pid.kp * rate_error;
    
    axis->rate_pid.integral += rate_error * dt;
    if (axis->rate_pid.integral > axis->rate_pid.i_max) axis->rate_pid.integral = axis->rate_pid.i_max;
    if (axis->rate_pid.integral < -axis->rate_pid.i_max) axis->rate_pid.integral = -axis->rate_pid.i_max;
    float i_term = axis->rate_pid.ki * axis->rate_pid.integral;
    
    float raw_d = (rate_error - axis->rate_pid.prev_error) / dt;
    axis->rate_pid.prev_error = rate_error;
    axis->rate_pid.prev_d_filtered = axis->rate_pid.d_filter_alpha * axis->rate_pid.prev_d_filtered + 
                                     (1.0f - axis->rate_pid.d_filter_alpha) * raw_d;
    float d_term = axis->rate_pid.kd * axis->rate_pid.prev_d_filtered;
    
    float u_q_cmd = p_term + i_term + d_term + feedforward_voltage;
    
    if (u_q_cmd > axis->u_limit) u_q_cmd = axis->u_limit;
    if (u_q_cmd < -axis->u_limit) u_q_cmd = -axis->u_limit;
    
    axis->u_d = 0.0f;
    axis->u_q = u_q_cmd;
}

/* Оновлення всіх трьох осей */
void triaxial_gimbal_update(TriaxialGimbalController *gimbal, Vec3 gyro_rad_s, float dt) {
    /* Гравітаційна компенсація зміщення центру мас камери для осі Pitch */
    float pitch_ff = gimbal->pitch_gravity_ff_v * cosf(gimbal->est_pitch_rad);
    
    gimbal_axis_cascade_update(&gimbal->yaw_axis, gimbal->target_yaw_rad, gimbal->est_yaw_rad, gyro_rad_s.z, 0.0f, dt);
    gimbal_controller_foc_step(&gimbal->yaw_axis);
    
    gimbal_axis_cascade_update(&gimbal->roll_axis, gimbal->target_roll_rad, gimbal->est_roll_rad, gyro_rad_s.x, 0.0f, dt);
    gimbal_controller_foc_step(&gimbal->roll_axis);
    
    gimbal_axis_cascade_update(&gimbal->pitch_axis, gimbal->target_pitch_rad, gimbal->est_pitch_rad, gyro_rad_s.y, pitch_ff, dt);
    gimbal_controller_foc_step(&gimbal->pitch_axis);
}
