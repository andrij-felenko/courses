/* C Implementation: State Validation and Matrix Transformations */
#include <math.h>
#include <stdbool.h>

rb_error_t rb_validate_state(const rb_state_t *s, const rb_mass_props_t *m, double quat_tol) {
    if (!s || !m) return RB_ERROR_NAN_OR_INF;

    /* 1. Сканування компонент на NaN / Inf */
    if (isnan(s->position.x) || isnan(s->position.y) || isnan(s->position.z) ||
        isnan(s->linear_velocity.x) || isnan(s->linear_velocity.y) || isnan(s->linear_velocity.z) ||
        isnan(s->orientation.w) || isnan(s->orientation.x) || isnan(s->orientation.y) || isnan(s->orientation.z) ||
        isnan(s->angular_velocity.x) || isnan(s->angular_velocity.y) || isnan(s->angular_velocity.z)) {
        return RB_ERROR_NAN_OR_INF;
    }

    if (m->mass <= 0.0 || isnan(m->mass) || isinf(m->mass)) return RB_ERROR_INVALID_MASS;
    if (m->inertia_diag.x <= 0.0 || m->inertia_diag.y <= 0.0 || m->inertia_diag.z <= 0.0) {
        return RB_ERROR_INVALID_INERTIA;
    }

    /* 2. Перевірка норми кватерніона */
    double q_sq = s->orientation.w * s->orientation.w +
                  s->orientation.x * s->orientation.x +
                  s->orientation.y * s->orientation.y +
                  s->orientation.z * s->orientation.z;
    if (fabs(q_sq - 1.0) > quat_tol) {
        return RB_ERROR_QUAT_NOT_NORMALIZED;
    }

    return RB_OK;
}

void rb_normalize_state(rb_state_t *s) {
    if (!s) return;
    double len = sqrt(s->orientation.w * s->orientation.w +
                      s->orientation.x * s->orientation.x +
                      s->orientation.y * s->orientation.y +
                      s->orientation.z * s->orientation.z);
    if (len < 1e-12) {
        s->orientation.w = 1.0;
        s->orientation.x = 0.0;
        s->orientation.y = 0.0;
        s->orientation.z = 0.0;
    } else {
        s->orientation.w /= len;
        s->orientation.x /= len;
        s->orientation.y /= len;
        s->orientation.z /= len;
    }
}

rb_derived_t rb_compute_derived(const rb_state_t *s, const rb_mass_props_t *m) {
    rb_derived_t d;

    /* 1. Поступальна кінетична енергія: T_trans = 0.5 * m * v² */
    double v_sq = s->linear_velocity.x * s->linear_velocity.x +
                  s->linear_velocity.y * s->linear_velocity.y +
                  s->linear_velocity.z * s->linear_velocity.z;
    d.kinetic_energy_trans = 0.5 * m->mass * v_sq;

    /* 2. Обертальна кінетична енергія: T_rot = 0.5 * (I_x w_x² + I_y w_y² + I_z w_z²) */
    d.kinetic_energy_rot = 0.5 * (
        m->inertia_diag.x * s->angular_velocity.x * s->angular_velocity.x +
        m->inertia_diag.y * s->angular_velocity.y * s->angular_velocity.y +
        m->inertia_diag.z * s->angular_velocity.z * s->angular_velocity.z
    );

    d.kinetic_energy_total = d.kinetic_energy_trans + d.kinetic_energy_rot;

    /* 3. Лінійний імпульс у світі: P = m * v */
    d.linear_momentum.x = m->mass * s->linear_velocity.x;
    d.linear_momentum.y = m->mass * s->linear_velocity.y;
    d.linear_momentum.z = m->mass * s->linear_velocity.z;

    /* 4. Момент імпульсу у власних осях: L_body = I_body * omega_body */
    rb_vec3_t L_body = {
        m->inertia_diag.x * s->angular_velocity.x,
        m->inertia_diag.y * s->angular_velocity.y,
        m->inertia_diag.z * s->angular_velocity.z
    };

    /* 5. Перетворення L_body у світову систему: L_world = R * L_body */
    double qw = s->orientation.w, qx = s->orientation.x, qy = s->orientation.y, qz = s->orientation.z;
    
    /* Елементи матриці обертання R з кватерніона */
    double R00 = 1.0 - 2.0 * (qy * qy + qz * qz);
    double R01 = 2.0 * (qx * qy - qz * qw);
    double R02 = 2.0 * (qx * qz + qy * qw);

    double R10 = 2.0 * (qx * qy + qz * qw);
    double R11 = 1.0 - 2.0 * (qx * qx + qz * qz);
    double R12 = 2.0 * (qy * qz - qx * qw);

    double R20 = 2.0 * (qx * qz - qy * qw);
    double R21 = 2.0 * (qy * qz + qx * qw);
    double R22 = 1.0 - 2.0 * (qx * qx + qy * qy);

    d.angular_momentum.x = R00 * L_body.x + R01 * L_body.y + R02 * L_body.z;
    d.angular_momentum.y = R10 * L_body.x + R11 * L_body.y + R12 * L_body.z;
    d.angular_momentum.z = R20 * L_body.x + R21 * L_body.y + R22 * L_body.z;

    /* 6. Трансформація тензора інерції у світову систему: I_world = R * I_body * Rᵀ */
    d.inertia_world.m[0][0] = R00*R00*m->inertia_diag.x + R01*R01*m->inertia_diag.y + R02*R02*m->inertia_diag.z;
    d.inertia_world.m[0][1] = R00*R10*m->inertia_diag.x + R01*R11*m->inertia_diag.y + R02*R12*m->inertia_diag.z;
    d.inertia_world.m[0][2] = R00*R20*m->inertia_diag.x + R01*R21*m->inertia_diag.y + R02*R22*m->inertia_diag.z;

    d.inertia_world.m[1][0] = d.inertia_world.m[0][1];
    d.inertia_world.m[1][1] = R10*R10*m->inertia_diag.x + R11*R11*m->inertia_diag.y + R12*R12*m->inertia_diag.z;
    d.inertia_world.m[1][2] = R10*R20*m->inertia_diag.x + R11*R21*m->inertia_diag.y + R12*R22*m->inertia_diag.z;

    d.inertia_world.m[2][0] = d.inertia_world.m[0][2];
    d.inertia_world.m[2][1] = d.inertia_world.m[1][2];
    d.inertia_world.m[2][2] = R20*R20*m->inertia_diag.x + R21*R21*m->inertia_diag.y + R22*R22*m->inertia_diag.z;

    return d;
}
