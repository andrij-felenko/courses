static const Vec3 G_WORLD = { 0.0f, 0.0f, -9.81f };   // гравітація вниз, вісь Z угору

// Один крок strapdown-механізації.
// q — орієнтація «тіло → світ»; v, p — швидкість і положення у світі;
// a_prev — світове прискорення з попереднього кроку (для трапеції);
// gyro — кутова швидкість тіла (рад/с); acc — питома сила тіла (м/с²).
void strapdown_step(Quat *q, Vec3 *v, Vec3 *p, Vec3 *a_prev,
                    Vec3 gyro, Vec3 acc, float dt)
{
    // 1. Орієнтація: докрутити точним приростом і ОБОВ'ЯЗКОВО нормувати.
    Vec3 rotvec = { gyro.x*dt, gyro.y*dt, gyro.z*dt };
    *q = quat_unit(quat_mul(*q, quat_delta(rotvec)));

    // 2. Питому силу з осей тіла — у світ.   3. Додати гравітацію.
    Vec3 fw = quat_rotate(*q, acc);
    Vec3 aw = { fw.x + G_WORLD.x, fw.y + G_WORLD.y, fw.z + G_WORLD.z };

    // 4. Трапеція: швидкість — середнім прискоренням, позиція — середньою швидкістю.
    Vec3 vn = {
        v->x + 0.5f*(a_prev->x + aw.x)*dt,
        v->y + 0.5f*(a_prev->y + aw.y)*dt,
        v->z + 0.5f*(a_prev->z + aw.z)*dt
    };
    p->x += 0.5f*(v->x + vn.x)*dt;
    p->y += 0.5f*(v->y + vn.y)*dt;
    p->z += 0.5f*(v->z + vn.z)*dt;
    *v = vn;
    *a_prev = aw;
}
