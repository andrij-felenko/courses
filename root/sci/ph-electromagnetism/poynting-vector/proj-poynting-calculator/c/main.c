#include <stdio.h>
#include <math.h>

typedef struct {
    double x;
    double y;
    double z;
} Vector3D;

static inline Vector3D vector3d_cross(Vector3D a, Vector3D b) {
    Vector3D res;
    res.x = a.y * b.z - a.z * b.y;
    res.y = a.z * b.x - a.x * b.z;
    res.z = a.x * b.y - a.y * b.x;
    return res;
}

static inline double vector3d_dot(Vector3D a, Vector3D b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

void poynting_coaxial_field(double r, double phi, double v, double i, double a, double b, Vector3D *e_out, Vector3D *h_out) {
    double ln_ba = log(b / a);
    double e_mag = v / (r * ln_ba);
    double h_mag = i / (2.0 * M_PI * r);

    e_out->x = e_mag * cos(phi);
    e_out->y = e_mag * sin(phi);
    e_out->z = 0.0;

    h_out->x = -h_mag * sin(phi);
    h_out->y = h_mag * cos(phi);
    h_out->z = 0.0;
}

double integrate_poynting_coaxial(double v, double i, double a, double b, int n_r, int n_phi) {
    double dr = (b - a) / n_r;
    double dphi = (2.0 * M_PI) / n_phi;
    double total_power = 0.0;

    Vector3D normal_z = {0.0, 0.0, 1.0};

    for (int ir = 0; ir < n_r; ++ir) {
        double r_mid = a + (ir + 0.5) * dr;
        double da = r_mid * dr * dphi;
        for (int ip = 0; ip < n_phi; ++ip) {
            double phi_mid = (ip + 0.5) * dphi;
            Vector3D e_vec, h_vec;
            poynting_coaxial_field(r_mid, phi_mid, v, i, a, b, &e_vec, &h_vec);
            Vector3D s_vec = vector3d_cross(e_vec, h_vec);
            total_power += vector3d_dot(s_vec, normal_z) * da;
        }
    }
    return total_power;
}

int main(void) {
    double v = 100.0, i = 2.0;
    double a = 0.002, b = 0.007;

    double power_calc = integrate_poynting_coaxial(v, i, a, b, 200, 360);
    double power_theory = v * i;

    printf("Обчислена потужність C: %.4f Вт\n", power_calc);
    printf("Теоретична потужність (V*I): %.4f Вт\n", power_theory);
    return 0;
}
