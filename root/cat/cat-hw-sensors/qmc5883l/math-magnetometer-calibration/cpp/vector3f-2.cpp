#include <array>

struct Vector3f {
    float x;
    float y;
    float z;
};

// Застосування обчислених коефіцієнтів калібрування до сирих показів
Vector3f apply_magnetometer_calibration(const Vector3f& raw,
                                         const Vector3f& offset,
                                         const std::array<std::array<float, 3>, 3>& soft_iron_matrix) {
    const Vector3f centered = {
        raw.x - offset.x,
        raw.y - offset.y,
        raw.z - offset.z
    };

    Vector3f calibrated = {0.0f, 0.0f, 0.0f};
    const float centered_arr[3] = {centered.x, centered.y, centered.z};

    calibrated.x = soft_iron_matrix[0][0] * centered_arr[0] +
                   soft_iron_matrix[0][1] * centered_arr[1] +
                   soft_iron_matrix[0][2] * centered_arr[2];

    calibrated.y = soft_iron_matrix[1][0] * centered_arr[0] +
                   soft_iron_matrix[1][1] * centered_arr[1] +
                   soft_iron_matrix[1][2] * centered_arr[2];

    calibrated.z = soft_iron_matrix[2][0] * centered_arr[0] +
                   soft_iron_matrix[2][1] * centered_arr[1] +
                   soft_iron_matrix[2][2] * centered_arr[2];

    return calibrated;
}
