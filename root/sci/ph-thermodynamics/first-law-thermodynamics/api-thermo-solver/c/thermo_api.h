/* thermo_api.h - Заголовочний файл C-інтерфейсу термодинамічного розв'язувача */
#ifndef THERMO_API_H
#define THERMO_API_H

#ifdef __cplusplus
extern "C" {
#endif

/* Помилки виконання розрахунку */
typedef enum {
    THERMO_SUCCESS = 0,
    THERMO_ERR_INVALID_PRESSURE = -1,
    THERMO_ERR_INVALID_VOLUME = -2,
    THERMO_ERR_INVALID_TEMP = -3,
    THERMO_ERR_INVALID_MOLES = -4,
    THERMO_ERR_CONVERGENCE_FAILED = -5
} ThermoStatus;

/* Макроскопічний стан системи */
typedef struct {
    double p; /* Абсолютний тиск [Па] */
    double v; /* Повний об'єм [м³] */
    double t; /* Абсолютна температура [К] */
} ThermoState;

/* Термодинамічні властивості робочого тіла (газу) */
typedef struct {
    double molar_mass;          /* Молярна маса [кг/моль] */
    double degrees_of_freedom;  /* Число ступенів вільності i (3, 5, 6) */
    double c_v;                 /* Молярна ізохорна теплоємність [Дж/(моль·К)] */
    double c_p;                 /* Молярна ізобарна теплоємність [Дж/(моль·К)] */
    double gamma;               /* Показник адіабати (c_p / c_v) */
} GasProperties;

/* Результат розрахунку термодинамічного процесу */
typedef struct {
    ThermoState initial_state;
    ThermoState final_state;
    double n_moles;     /* Кількість речовини [моль] */
    double work;        /* Механічна робота W [Дж] */
    double heat;        /* Передане тепло Q [Дж] */
    double delta_u;     /* Зміна внутрішньої енергії dU [Дж] */
    double delta_h;     /* Зміна ентальпії dH [Дж] */
} ProcessRecord;

#ifdef __cplusplus
}
#endif

#endif /* THERMO_API_H */
