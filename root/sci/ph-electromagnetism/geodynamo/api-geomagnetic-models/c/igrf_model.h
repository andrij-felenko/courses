/* igrf_model.h - C API специфікації геомагнітної моделі IGRF */
#ifndef IGRF_MODEL_H
#define IGRF_MODEL_H

#ifdef __cplusplus
extern "C" {
#endif

#define IGRF_MAX_DEGREE 13
#define IGRF_NUM_COEFFS (((IGRF_MAX_DEGREE + 1) * (IGRF_MAX_DEGREE + 2)) / 2)

/* Геодезичні координати спостерігача (WGS84) */
typedef struct {
    double latitude_deg;   /* Географічна широта [-90.0 .. +90.0] */
    double longitude_deg;  /* Географічна долгота [-180.0 .. +180.0] */
    double altitude_km;    /* Висота над рівнем моря WGS84 (км) */
    double epoch_year;     /* Епоха (наприклад, 2025.5) */
} GeodeticCoord;

/* Результуючий геомагнітний вектор */
typedef struct {
    double X_nT;  /* Північна компонента (нТл) */
    double Y_nT;  /* Східна компонента (нТл) */
    double Z_nT;  /* Вертикальна компонента вниз (нТл) */
    double H_nT;  /* Горизонтальна напруженість (нТл) */
    double F_nT;  /* Повний модуль магнітного поля (нТл) */
    double D_deg; /* Деклінація (градуси, схід > 0) */
    double I_deg; /* Інклінація (градуси, вниз > 0) */
} MagneticVector;

/* Структура коефіцієнтів Гаусса для конкретної епохи */
typedef struct {
    double epoch;
    double g[IGRF_MAX_DEGREE + 1][IGRF_MAX_DEGREE + 1];
    double h[IGRF_MAX_DEGREE + 1][IGRF_MAX_DEGREE + 1];
} IGRFCoefficients;

/**
 * Обчислення геомагнітного вектора за координатами WGS84.
 * @param coord Координати та епоха спостерігача
 * @param coeffs Завантажені коефіцієнти Гаусса
 * @param result Вихідний вектор магнітного поля
 * @return 0 при успіху, від'ємний код при помилці
 */
int igrf_calculate(const GeodeticCoord* coord, const IGRFCoefficients* coeffs, MagneticVector* result);

#ifdef __cplusplus
}
#endif

#endif /* IGRF_MODEL_H */
