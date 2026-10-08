typedef struct {
    float pwm_a; // Коефіцієнт заповнення ШІМ фази A [0.0 ... 1.0]
    float pwm_b; // Коефіцієнт заповнення ШІМ фази B [0.0 ... 1.0]
    float pwm_c; // Коефіцієнт заповнення ШІМ фази C [0.0 ... 1.0]
} SVPWM_Duty;

SVPWM_Duty foc_svpwm(float u_alpha, float u_beta, float u_dc) {
    SVPWM_Duty duty;

    // Зсунуті проекції для визначення сектора
    float v_a = u_beta;
    float v_b = 0.8660254f * u_alpha - 0.5f * u_beta;
    float v_c = -0.8660254f * u_alpha - 0.5f * u_beta;

    // Визначення номера сектора (1..6)
    int sector = 0;
    if (v_a > 0.0f) sector += 1;
    if (v_b > 0.0f) sector += 2;
    if (v_c > 0.0f) sector += 4;

    float t1 = 0.0f, t2 = 0.0f;
    float temp_k = 1.7320508f / u_dc; // sqrt(3) / U_dc

    switch (sector) {
        case 3: // Сектор 1 (0° .. 60°)
            t1 = temp_k * (0.8660254f * u_alpha - 0.5f * u_beta);
            t2 = temp_k * u_beta;
            break;
        case 1: // Сектор 2 (60° .. 120°)
            t1 = temp_k * (0.8660254f * u_alpha + 0.5f * u_beta);
            t2 = temp_k * (-0.8660254f * u_alpha + 0.5f * u_beta);
            break;
        case 5: // Сектор 3 (120° .. 180°)
            t1 = temp_k * u_beta;
            t2 = temp_k * (-0.8660254f * u_alpha - 0.5f * u_beta);
            break;
        case 4: // Сектор 4 (180° .. 240°)
            t1 = temp_k * (-0.8660254f * u_alpha + 0.5f * u_beta);
            t2 = temp_k * (-u_beta);
            break;
        case 6: // Сектор 5 (240° .. 300°)
            t1 = temp_k * (-0.8660254f * u_alpha - 0.5f * u_beta);
            t2 = temp_k * (0.8660254f * u_alpha - 0.5f * u_beta);
            break;
        case 2: // Сектор 6 (300° .. 360°)
            t1 = temp_k * (-u_beta);
            t2 = temp_k * (0.8660254f * u_alpha + 0.5f * u_beta);
            break;
        default:
            t1 = 0.0f;
            t2 = 0.0f;
            break;
    }

    // Захист від перемодуляції
    if (t1 + t2 > 1.0f) {
        float scale = 1.0f / (t1 + t2);
        t1 *= scale;
        t2 *= scale;
    }

    float t0 = 1.0f - t1 - t2; // Час нульового вектора

    // Розподіл затримок для симетричної 7-сегментної ШІМ
    switch (sector) {
        case 3: // Сектор 1
            duty.pwm_a = t0 / 2.0f + t1 + t2;
            duty.pwm_b = t0 / 2.0f + t2;
            duty.pwm_c = t0 / 2.0f;
            break;
        case 1: // Сектор 2
            duty.pwm_a = t0 / 2.0f + t1;
            duty.pwm_b = t0 / 2.0f + t1 + t2;
            duty.pwm_c = t0 / 2.0f;
            break;
        case 5: // Сектор 3
            duty.pwm_a = t0 / 2.0f;
            duty.pwm_b = t0 / 2.0f + t1 + t2;
            duty.pwm_c = t0 / 2.0f + t2;
            break;
        case 4: // Сектор 4
            duty.pwm_a = t0 / 2.0f;
            duty.pwm_b = t0 / 2.0f + t1;
            duty.pwm_c = t0 / 2.0f + t1 + t2;
            break;
        case 6: // Сектор 5
            duty.pwm_a = t0 / 2.0f + t2;
            duty.pwm_b = t0 / 2.0f;
            duty.pwm_c = t0 / 2.0f + t1 + t2;
            break;
        case 2: // Сектор 6
            duty.pwm_a = t0 / 2.0f + t1 + t2;
            duty.pwm_b = t0 / 2.0f;
            duty.pwm_c = t0 / 2.0f + t1;
            break;
        default:
            duty.pwm_a = 0.5f;
            duty.pwm_b = 0.5f;
            duty.pwm_c = 0.5f;
            break;
    }

    return duty;
}
