static float meas_prev = 0.0f;
static float deriv_filt = 0.0f;

float d_raw = -(measurement - meas_prev) / dt;   // сира похідна від виміру
meas_prev = measurement;

// одно-полюсний ФНЧ: alpha = dt / (dt + tau_d),  tau_d = (Kd/Kp)/N
float tau_d = (Kd / Kp) / N_FILT;                // стала часу фільтра похідної
float alpha = dt / (dt + tau_d);
deriv_filt += alpha * (d_raw - deriv_filt);      // згладжуємо
// далі: ... + Kd * deriv_filt
