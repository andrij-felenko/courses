#include <stdio.h>
#include <math.h>

typedef enum {
    DIPOLE_SUCCESS = 0,
    DIPOLE_ERR_NULL_PTR = -1,
    DIPOLE_ERR_SINGULARITY = -2,
    DIPOLE_ERR_INVALID_PARAM = -3
} dipole_error_t;

typedef struct {
    double x, y, z;
} dipole_vec3_t;

typedef struct {
    dipole_vec3_t pos;
    dipole_vec3_t p;
    double cutoff;
} dipole_state_t;

dipole_error_t dipole_calc_potential(
    const dipole_state_t* dipole,
    dipole_vec3_t point,
    double* out_potential
) {
    if (!dipole || !out_potential) {
        return DIPOLE_ERR_NULL_PTR;
    }
    if (dipole->cutoff < 0.0) {
        return DIPOLE_ERR_INVALID_PARAM;
    }

    double dx = point.x - dipole->pos.x;
    double dy = point.y - dipole->pos.y;
    double dz = point.z - dipole->pos.z;

    double r_sq = dx * dx + dy * dy + dz * dz + dipole->cutoff * dipole->cutoff;
    double r_len = sqrt(r_sq);
    double r_pow3 = r_len * r_sq;

    double dot_pR = dipole->p.x * dx + dipole->p.y * dy + dipole->p.z * dz;
    const double k_e = 8.9875517923e9; // 1 / (4*pi*eps0)

    *out_potential = k_e * dot_pR / r_pow3;
    return DIPOLE_SUCCESS;
}

dipole_error_t dipole_calc_interaction(
    const dipole_state_t* dipole,
    dipole_vec3_t ext_field,
    dipole_vec3_t* out_torque,
    double* out_energy
) {
    if (!dipole) {
        return DIPOLE_ERR_NULL_PTR;
    }

    if (out_torque) {
        out_torque->x = dipole->p.y * ext_field.z - dipole->p.z * ext_field.y;
        out_torque->y = dipole->p.z * ext_field.x - dipole->p.x * ext_field.z;
        out_torque->z = dipole->p.x * ext_field.y - dipole->p.y * ext_field.x;
    }

    if (out_energy) {
        *out_energy = -(dipole->p.x * ext_field.x + 
                        dipole->p.y * ext_field.y + 
                        dipole->p.z * ext_field.z);
    }

    return DIPOLE_SUCCESS;
}

int main(void) {
    dipole_state_t state = {
        .pos = {0.0, 0.0, 0.0},
        .p = {0.0, 0.0, 3.33564e-30}, // 1 Debye
        .cutoff = 1e-9
    };

    dipole_vec3_t pt = {1e-9, 0.0, 0.0};
    double pot = 0.0;

    if (dipole_calc_potential(&state, pt, &pot) == DIPOLE_SUCCESS) {
        printf("Потенціал диполя в 1D на 1 нм: %.6e V\n", pot);
    }

    return 0;
}
