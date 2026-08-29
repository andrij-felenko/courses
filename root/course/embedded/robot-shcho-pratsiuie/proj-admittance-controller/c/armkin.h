#ifndef ARMKIN_H
#define ARMKIN_H

#include <stdbool.h>

#define ARM_JOINTS         6
#define CART_DOF           6
#define ARM_MAX_JOINT_RATE 2.0f /* рад/с — межа приводу */

/* Ланка у стандартній нотації Денавіта — Гартенберга. */
typedef struct {
    float a;            /* зміщення вздовж x_i, м */
    float alpha;        /* поворот навколо x_i, рад */
    float d;            /* зміщення вздовж z_{i−1}, м */
    float theta_offset; /* сталий доданок до кута суглоба, рад */
} arm_link_t;

typedef struct {
    float r_flange[9];               /* орієнтація фланця в базі, РЯДКАМИ */
    float p_flange[3];               /* положення фланця в базі, м */
    float jac[CART_DOF][ARM_JOINTS]; /* геометричний якобіан у базі */
    float manipulability;            /* w = sqrt(det(J·Jᵀ)) */
} arm_state_t;

extern const arm_link_t ARM_DEMO_LINKS[ARM_JOINTS];

void arm_forward(const arm_link_t links[ARM_JOINTS], const float q[ARM_JOINTS], arm_state_t *st);

/* Поворот шістки «трійка + трійка» з системи фланця в базову.
   Годиться і для сил із моментами, і для лінійної та кутової швидкості. */
void arm_rotate6(const float r_flange[9], const float body[CART_DOF], float base[CART_DOF]);

/* Згасаючі найменші квадрати: q' = Jᵀ·(J·Jᵀ + lambda²·I)⁻¹·v_cmd.
   lambda росте від нуля при w < w_threshold до lambda_max у сингулярності.
   Повертає false, якщо система не розкладається навіть із демпфуванням. */
bool arm_dls_joint_velocity(const arm_state_t *st, const float v_cmd[CART_DOF],
                            float lambda_max, float w_threshold,
                            float q_dot[ARM_JOINTS], float *lambda_used);

#endif /* ARMKIN_H */
