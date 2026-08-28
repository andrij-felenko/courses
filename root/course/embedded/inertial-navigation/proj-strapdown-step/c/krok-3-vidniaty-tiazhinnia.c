/* Прискорення руху = повернутий у світ акселерометр мінус тяжіння.
   Світові осі: x — північ, y — схід, z — ВГОРУ (тоді тяжіння = −g по z). */
static const float G = 9.81f;     /* м/с² */

static vec3 remove_gravity(vec3 a_world) {
    vec3 a;
    a.x = a_world.x;
    a.y = a_world.y;
    a.z = a_world.z - G;          /* акселерометр у спокої дає +G по вгору → віднімаємо */
    return a;
}
