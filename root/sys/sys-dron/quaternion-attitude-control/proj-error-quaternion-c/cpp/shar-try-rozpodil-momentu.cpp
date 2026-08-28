#define N_MOTORS 4

// зашита наперед матриця розподілу: рядок = мотор, стовпці = внесок
// моменту по осях (roll, pitch, yaw) у команду цього мотора.
// Для симетричної квадро-X — знаки «+/−» однакової величини.
static const float ALLOC[N_MOTORS][3] = {
    // roll   pitch   yaw
    { +1.0f, +1.0f, +1.0f },   // мотор 1 (перед-право)
    { +1.0f, -1.0f, -1.0f },   // мотор 2 (зад-право)
    { -1.0f, +1.0f, -1.0f },   // мотор 3 (перед-ліво)
    { -1.0f, -1.0f, +1.0f },   // мотор 4 (зад-ліво)
};

// розкидати три компоненти моменту + спільну тягу на N моторів
void allocate(const float tau[3], float thrust_base, float motor[N_MOTORS]) {
    for (int i = 0; i < N_MOTORS; ++i) {
        motor[i] = thrust_base
                 + ALLOC[i][0]*tau[0]    // крен
                 + ALLOC[i][1]*tau[1]    // тангаж
                 + ALLOC[i][2]*tau[2];   // рискання
    }
}
