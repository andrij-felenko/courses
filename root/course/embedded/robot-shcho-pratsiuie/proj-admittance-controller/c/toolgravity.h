#ifndef TOOLGRAVITY_H
#define TOOLGRAVITY_H

/* Компенсація ваги робочого органа на зап'ястку.
   Матриця r_sensor — орієнтація давача відносно горизонту (з прямої
   кінематики руки), задана РЯДКАМИ: r[0..2] — перший рядок. */

typedef struct {
    float mass;   /* маса інструмента, кг */
    float com[3]; /* центр мас у системі давача, м */
    float g;      /* прискорення вільного падіння, м/с² */
} tool_inertia_t;

/* Внесок ваги у покази давача: сила Rᵀ·[0,0,−m·g] і момент com × сила. */
void tool_gravity_wrench(const tool_inertia_t *tool, const float r_sensor[9], float w_g[6]);

/* F_ext = F_raw − Rᵀ·[0,0,−m·g] (і те саме для моментів). */
void tool_gravity_compensate(const tool_inertia_t *tool, const float r_sensor[9],
                             const float w_raw[6], float w_ext[6]);

#endif /* TOOLGRAVITY_H */
