// вхід: throttle 0..1 (спільна тяга), roll/pitch/yaw — моменти (можуть бути ±)
// вихід: m[0..3] у діапазоні 0..1, далі — на ESC
void mix_quad_x(float throttle, float roll, float pitch, float yaw,
                float m[4])
{
    // 1) сирий розклад за матрицею мікшера квадро-X
    m[0] = throttle + roll + pitch + yaw;   // передній правий, CW
    m[1] = throttle + roll - pitch - yaw;   // задній правий,  CCW
    m[2] = throttle - roll + pitch - yaw;   // передній лівий, CCW
    m[3] = throttle - roll - pitch + yaw;   // задній лівий,   CW

    // 2) знайти найбільше й найменше серед чотирьох
    float lo = m[0], hi = m[0];
    for (int i = 1; i < 4; i++) {
        if (m[i] < lo) lo = m[i];
        if (m[i] > hi) hi = m[i];
    }

    // 3) нормування зсувом УСІХ команд (зберігаємо різниці = моменти)
    if (hi > 1.0f) {            // хтось пробив стелю — опустити пакет
        float over = hi - 1.0f;
        for (int i = 0; i < 4; i++) m[i] -= over;
    } else if (lo < 0.0f) {     // хтось пірнув під нуль — підняти пакет
        float under = -lo;
        for (int i = 0; i < 4; i++) m[i] += under;
    }

    // 4) запобіжник на крайній випадок (моменти такі великі,
    //    що навіть після зсуву не влізають у коридор 0..1)
    for (int i = 0; i < 4; i++) {
        if (m[i] < 0.0f) m[i] = 0.0f;
        if (m[i] > 1.0f) m[i] = 1.0f;
    }
}
