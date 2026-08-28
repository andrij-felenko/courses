// Стан регулятора — ЖИВЕ між викликами (поля структури стану, тут static):
static float meas_prev = 0.0f;   // попередній вимір
static float d_filt    = 0.0f;   // відфільтрований D-член (стан EMA)

// Один такт, викликається рівномірно кожні dt секунд:
float d_raw = (meas_prev - meas) / dt;   // −dy/dt: сира похідна ВІД ВИМІРУ
float alpha = dt / (dt + tau);           // tau = 1/N; коеф. згладжування 0…1
d_filt += alpha * (d_raw - d_filt);      // однополюсний ФНЧ (EMA) = N/(s+N)
float u_D = Kd * d_filt;                  // внесок диференційної складової
meas_prev = meas;                         // запам'ятати для наступного такту
