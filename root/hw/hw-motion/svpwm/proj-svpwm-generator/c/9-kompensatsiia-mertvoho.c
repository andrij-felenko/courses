// Програмна компенсація мертвого часу
float dt_volt = (dead_time_sec / pwm_period_sec) * v_dc;

if (i_a > current_threshold)       v_a_comp += dt_volt;
else if (i_a < -current_threshold) v_a_comp -= dt_volt;

if (i_b > current_threshold)       v_b_comp += dt_volt;
else if (i_b < -current_threshold) v_b_comp -= dt_volt;

if (i_c > current_threshold)       v_c_comp += dt_volt;
else if (i_c < -current_threshold) v_c_comp -= dt_volt;
