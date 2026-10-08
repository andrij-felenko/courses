// Застосування обчислених коефіцієнтів калібрування до сирих показів
void apply_magnetometer_calibration(const float raw[3], const float offset[3],
                                     const float soft_iron_matrix[3][3],
                                     float calibrated[3]) {
    // Крок 1: Усунення постійного зсуву Hard Iron
    float centered[3] = {
        raw[0] - offset[0],
        raw[1] - offset[1],
        raw[2] - offset[2]
    };

    // Крок 2: Множення на матрицю компенсації Soft Iron
    for (int i = 0; i < 3; i++) {
        calibrated[i] = 0.0f;
        for (int j = 0; j < 3; j++) {
            calibrated[i] += soft_iron_matrix[i][j] * centered[j];
        }
    }
}
