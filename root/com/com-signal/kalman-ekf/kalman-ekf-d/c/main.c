// скалярний EKF-такт із нелінійним виміром z = h/cos(theta)
float h = 40.0f, P = 4.0f;               // оцінка висоти та її дисперсія
const float R = 0.25f;                    // шум далекоміра, м²
const float theta = 30.0f * 3.14159265f / 180.0f;

void ekf_range_update(float z_meas) {
    float c  = cosf(theta);
    float H  = 1.0f / c;                  // якобіан виміру в точці оцінки
    float z_hat = h / c;                  // очікуваний вимір — через ТОЧНУ модель
    float S  = H * P * H + R;             // невпевненість інновації
    float K  = P * H / S;                 // підсилення Калмана
    h += K * (z_meas - z_hat);            // корекція стану
    P  = (1.0f - K * H) * P;              // невпевненість падає
}
