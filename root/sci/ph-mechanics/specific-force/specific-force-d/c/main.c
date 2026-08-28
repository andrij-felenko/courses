// Один крок strapdown-механізації з кроком часу dt (напр. 1/500 с).
// q — орієнтація «тіло → світ» (кватерніон); v — швидкість, p — позиція у світі.
// gyro[] — кутова швидкість тіла (рад/с); acc[] — питома сила (м/с²) в осях тіла.
static const float g_world[3] = {0.0f, 0.0f, -9.81f};   // гравітація вниз (вісь Z угору)

void strapdown_step(Quat *q, float v[3], float p[3],
                    const float gyro[3], const float acc[3], float dt)
{
    // 1. Орієнтація: докрутити кватерніон на малий поворот gyro·dt і нормувати
    quat_integrate(q, gyro, dt);          // q ← q ⊗ Δq(gyro·dt)

    // 2. Питому силу з осей тіла — у світові осі
    float f_world[3];
    quat_rotate(q, acc, f_world);         // f_world = q · acc · q*

    // 3. Додати гравітацію, якої акселерометр «не відчув»
    float a_world[3] = {
        f_world[0] + g_world[0],
        f_world[1] + g_world[1],
        f_world[2] + g_world[2],
    };

    // 4. Проінтегрувати: прискорення → швидкість → положення
    for (int i = 0; i < 3; i++) {
        p[i] += v[i] * dt + 0.5f * a_world[i] * dt * dt;
        v[i] += a_world[i] * dt;
    }
}
