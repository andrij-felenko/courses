#ifndef GLASS_CATALOG_H
#define GLASS_CATALOG_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Довжини хвиль спектральних ліній Фраунгофера у мікрометрах */
#define LAMBDA_I_UM 0.365015  /* Ртуть i */
#define LAMBDA_H_UM 0.404656  /* Ртуть h */
#define LAMBDA_G_UM 0.435834  /* Ртуть g */
#define LAMBDA_F_UM 0.486133  /* Водень F */
#define LAMBDA_E_UM 0.546074  /* Ртуть e */
#define LAMBDA_D_UM 0.587562  /* Гелій d */
#define LAMBDA_C_UM 0.656273  /* Водень C */
#define LAMBDA_R_UM 0.706519  /* Гелій r */
#define LAMBDA_S_UM 0.852110  /* Цезій s */
#define LAMBDA_T_UM 1.013980  /* Ртуть t */

/* Тип формули дисперсії */
typedef enum {
    DISPERSION_FORMULA_SELLMEIER1 = 1, /* 6-параметричне рівняння Зельмейєра */
    DISPERSION_FORMULA_CAUCHY     = 2, /* Степеневе розкладення Коші */
    DISPERSION_FORMULA_HARTMANN   = 3  /* Емпірична формула Хартманна */
} DispersionFormulaType;

/* Коефіцієнти Зельмейєра: B1, B2, B3 (безрозмірні) та C1, C2, C3 (мкм²) */
typedef struct {
    double B1, B2, B3;
    double C1, C2, C3;
} SellmeierCoefficientsC;

/* Термооптичні коефіцієнти зміщення dn/dT (1/К) */
typedef struct {
    double D0; /* Постійний коефіцієнт (10^-6 / K) */
    double D1; /* Лінійний температурний коефіцієнт */
    double D2; /* Квадратичний температурний коефіцієнт */
    double E0; /* УФ-термічний зміщувач */
    double E1; /* ІЧ-термічний зміщувач */
} ThermoOpticCoefficientsC;

/* Повний двійковий паспорт оптичного матеріалу */
typedef struct {
    const char* material_name;     /* Строкове ім'я матеріалу (наприклад "N-BK7") */
    const char* glass_code;        /* 6-значний індекс (наприклад "517642") */
    const char* supplier;          /* Виробник (Schott, Ohara, Hoya) */
    DispersionFormulaType formula; /* Тип дисперсійного рівняння */
    SellmeierCoefficientsC sellmeier; /* Набір коефіцієнтів Зельмейєра */
    ThermoOpticCoefficientsC thermo;  /* Термооптичні параметри */
    double n_d;                    /* Каталожний показник заломлення на лінії d */
    double V_d;                    /* Каталожне число Аббе V_d */
    double density_g_cm3;          /* Питома густина скла (г/см³) */
    double lambda_min_um;          /* УФ-межа прозорості (мкм) */
    double lambda_max_um;          /* ІЧ-межа прозорості (мкм) */
} GlassMaterialSpecC;

/* Функція обчислення показника заломлення n(lambda) за паспортом C-структури */
double glass_calculate_n(const GlassMaterialSpecC* glass, double lambda_um);

/* Функція обчислення числового значення числа Аббе V_d */
double glass_calculate_v_d(const GlassMaterialSpecC* glass);

#ifdef __cplusplus
}
#endif

#endif /* GLASS_CATALOG_H */
