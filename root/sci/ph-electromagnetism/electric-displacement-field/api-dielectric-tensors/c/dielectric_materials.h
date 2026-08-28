/* dielectric_materials.h — Специфікація тензорних матеріалів для C-солверів */
#ifndef DIELECTRIC_MATERIALS_H
#define DIELECTRIC_MATERIALS_H

#include <stdbool.h>

typedef enum {
    MAT_ISOTROPIC,
    MAT_UNIAXIAL,
    MAT_BIAXIAL,
    MAT_FERROELECTRIC
} MaterialType;

typedef struct {
    char name[64];
    MaterialType type;
    double eps_tensor[3][3];  /* Тензор відносної проникності */
    double tan_delta;         /* Тангенс кута втрат */
    double breakdown_field;   /* Електрична міцність, В/м */
    bool is_nonlinear;
    double chi2[3][3][3];     /* Тензор 2-ї нелінійності */
} DielectricMaterial;

static inline void mat_set_isotropic(DielectricMaterial *m, const char *name, double eps_r, double tan_d) {
    int i, j;
    snprintf(m->name, sizeof(m->name), "%s", name);
    m->type = MAT_ISOTROPIC;
    m->tan_delta = tan_d;
    m->is_nonlinear = false;
    for (i = 0; i < 3; i++) {
        for (j = 0; j < 3; j++) {
            m->eps_tensor[i][j] = (i == j) ? eps_r : 0.0;
        }
    }
}

static inline void mat_set_uniaxial(DielectricMaterial *m, const char *name, double eps_perp, double eps_para) {
    mat_set_isotropic(m, name, eps_perp, 0.0);
    m->type = MAT_UNIAXIAL;
    m->eps_tensor[2][2] = eps_para; /* Оптична вісь Z */
}

#endif /* DIELECTRIC_MATERIALS_H */
