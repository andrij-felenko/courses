/* c_colorimetry.h - Повний C-інтерфейс колориметричного модуля */
#ifndef C_COLORIMETRY_H
#define C_COLORIMETRY_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define COLORIMETRY_SPECTRUM_MIN_WL  380
#define COLORIMETRY_SPECTRUM_MAX_WL  780
#define COLORIMETRY_CRI_SAMPLE_COUNT 15

/* Перелік кодів помилок для C API */
typedef enum {
    COLORIMETRY_OK                  =  0, /* Успішне виконання обчислення */
    COLORIMETRY_ERR_NULL_PTR        = -1, /* Передано нульовий указник */
    COLORIMETRY_ERR_INVALID_WL      = -2, /* Діапазон довжин хвиль не покриває 380..780 нм */
    COLORIMETRY_ERR_INVALID_STEP    = -3, /* Непідтримуваний крок сітки (дозволено 1 або 5 нм) */
    COLORIMETRY_ERR_ZERO_INTEGRAL   = -4, /* Сума тристимульних значень дорівнює нулю */
    COLORIMETRY_ERR_OUT_OF_RANGE    = -5  /* Значення CCT виходить за межі 1000K..25000K */
} colorimetry_error_t;

/* Дискретний спектральний розподіл потужності (SPD) */
typedef struct {
    uint16_t start_wavelength_nm; /* Початкова довжина хвилі (зазвичай 380 нм) */
    uint16_t step_wavelength_nm;  /* Крок дискретизації сітки (1 нм або 5 нм) */
    size_t   count;               /* Кількість дискретних відліків у масиві */
    const double* power_values;   /* Масив спектральної густини потужності (Вт/(м²·нм)) */
} spectral_data_t;

/* Тристимульний вектор CIE 1931 XYZ */
typedef struct {
    double X; /* Червона уявна складова (абсолютна або відносна) */
    double Y; /* Фотометрична яскравість у кд/м² (або відносний світловий потік) */
    double Z; /* Синя уявна складова */
} tristimulus_xyz_t;

/* Двовимірні координати хроматичності */
typedef struct {
    double x;       /* Координата x стандарту CIE 1931 */
    double y;       /* Координата y стандарту CIE 1931 */
    double u_prime; /* Рівномірна координата u' стандарту CIE 1976 UCS */
    double v_prime; /* Рівномірна координата v' стандарту CIE 1976 UCS */
} chromaticity_coords_t;

/* Результат обчислення корельованої колірної температури */
typedef struct {
    double cct_kelvin; /* Обчислена колірна температура у Кельвінах */
    double duv;        /* Ортогональне відхилення від лінії чорного тіла */
    bool   is_valid;   /* Прапорець достовірності обчислення */
} cct_result_t;

/* Результати обчислення індексу кольоропередачі CRI */
typedef struct {
    double R_a; /* Загальний індекс кольоропередачі (середнє R1..R8) */
    double R_i[COLORIMETRY_CRI_SAMPLE_COUNT]; /* Окремі індекси R1..R15 */
    double R_9; /* Спеціальний індекс для насиченого червоного колірного зразка */
} cri_result_t;

#endif /* C_COLORIMETRY_H */
