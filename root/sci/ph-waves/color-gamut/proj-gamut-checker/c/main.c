/* C99: Перевірка та кліпінг колірного охоплення sRGB */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
    double z;
} Vector3;

typedef struct {
    double x;
    double y;
} Point2D;

static const double M_INV_SRGB[3][3] = {
    { 3.2404542, -1.5371385, -0.4985314},
    {-0.9692660,  1.8760108,  0.0415560},
    { 0.0556434, -0.2040259,  1.0572252}
};

Vector3 xyz_to_srgb(Vector3 xyz) {
    Vector3 rgb;
    rgb.x = M_INV_SRGB[0][0]*xyz.x + M_INV_SRGB[0][1]*xyz.y + M_INV_SRGB[0][2]*xyz.z;
    rgb.y = M_INV_SRGB[1][0]*xyz.x + M_INV_SRGB[1][1]*xyz.y + M_INV_SRGB[1][2]*xyz.z;
    rgb.z = M_INV_SRGB[2][0]*xyz.x + M_INV_SRGB[2][1]*xyz.y + M_INV_SRGB[2][2]*xyz.z;
    return rgb;
}

bool is_in_srgb_gamut(Vector3 xyz) {
    Vector3 rgb = xyz_to_srgb(xyz);
    const double eps = 1e-6;
    return (rgb.x >= -eps && rgb.x <= 1.0 + eps &&
            rgb.y >= -eps && rgb.y <= 1.0 + eps &&
            rgb.z >= -eps && rgb.z <= 1.0 + eps);
}

Vector3 clip_srgb_gamut(Vector3 xyz) {
    Vector3 rgb = xyz_to_srgb(xyz);
    Vector3 out;
    out.x = (rgb.x < 0.0) ? 0.0 : ((rgb.x > 1.0) ? 1.0 : rgb.x);
    out.y = (rgb.y < 0.0) ? 0.0 : ((rgb.y > 1.0) ? 1.0 : rgb.y);
    out.z = (rgb.z < 0.0) ? 0.0 : ((rgb.z > 1.0) ? 1.0 : rgb.z);
    return out;
}

int main(void) {
    Vector3 test_xyz = {0.14, 0.03, 0.85};
    bool valid = is_in_srgb_gamut(test_xyz);
    printf("Is in sRGB gamut: %s\n", valid ? "YES" : "NO");

    Vector3 clipped = clip_srgb_gamut(test_xyz);
    printf("Clipped RGB: [%.4f, %.4f, %.4f]\n", clipped.x, clipped.y, clipped.z);
    return 0;
}
