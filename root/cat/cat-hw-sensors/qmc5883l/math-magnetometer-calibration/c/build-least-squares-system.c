#include <stddef.h>

// Накопичення елементів матриці DᵀD (9x9) та вектора Dᵀy (9x1)
// за масивом сирих тривимірних вимірювань магнітометра
void build_least_squares_system(const float raw_points[][3], size_t count,
                                double dtd[9][9], double dty[9]) {
    for (int i = 0; i < 9; i++) {
        dty[i] = 0.0;
        for (int j = 0; j < 9; j++) {
            dtd[i][j] = 0.0;
        }
    }

    for (size_t k = 0; k < count; k++) {
        double x = raw_points[k][0];
        double y = raw_points[k][1];
        double z = raw_points[k][2];

        // Рядок D_k для k-ї точки: [x², y², z², 2xy, 2xz, 2yz, 2x, 2y, 2z]
        double row[9] = {
            x * x,
            y * y,
            z * z,
            2.0 * x * y,
            2.0 * x * z,
            2.0 * y * z,
            2.0 * x,
            2.0 * y,
            2.0 * z
        };

        // Накопичення добутків для формування нормальних рівнянь
        for (int i = 0; i < 9; i++) {
            dty[i] += row[i];
            for (int j = 0; j < 9; j++) {
                dtd[i][j] += row[i] * row[j];
            }
        }
    }
}
