/* Header: spectral_analysis_api.h */
#ifndef SPECTRAL_ANALYSIS_API_H
#define SPECTRAL_ANALYSIS_API_H

#ifdef __cplusplus
extern "C" {
#endif

/* Перераховуваний тип переліку віконних функцій */
typedef enum {
    WINDOW_RECTANGULAR = 0, /* Прямокутне вікно (без віконної обробки) */
    WINDOW_HANN        = 1, /* Вікно Хенна (рекомендоване для шумів) */
    WINDOW_HAMMING     = 2, /* Вікно Хеммінга */
    WINDOW_BLACKMAN    = 3, /* Вікно Блекмана з високим пригніченням */
    WINDOW_FLAT_TOP    = 4  /* Вікно з плоскою вершиною для калібрування */
} WindowType;

/* Коди помилок API */
typedef enum {
    PSD_SUCCESS           =  0, /* Успішне виконання операції */
    PSD_ERR_NULL_POINTER  = -1, /* Передано нульовий вказівник */
    PSD_ERR_INVALID_SIZE  = -2, /* Некоректний розмір БПФ (не є ступенем 2) */
    PSD_ERR_INVALID_RATE  = -3, /* Частота дискретизації <= 0 */
    PSD_ERR_NO_MEMORY     = -4  /* Помилка виділення динамічної пам'яті */
} PsdErrorCode;

/* Структура конфігурації аналізатора спектра Велча */
typedef struct {
    double     sample_rate_hz;  /* Частота дискретизації f_s (Гц), f_s > 0 */
    int        fft_size;        /* Розмір БПФ N_fft (2^K: 512, 1024, 2048...) */
    int        overlap_samples; /* Перекриття сегментів в відліках (N_fft / 2) */
    WindowType window_type;     /* Обраний тип згладжувального вікна */
} PsdConfig;

/* Структура конфігурації генератора гауссового білого шуму */
typedef struct {
    double       target_g0;     /* Цільова одностороння PSD G_0 (В²/Гц) */
    double       sample_rate_hz;/* Частота дискретизації f_s (Гц) */
    unsigned int seed;          /* Початкове зерно генератора випадкових чисел */
} NoiseGenConfig;

/* Структура з результатами спектрального аналізу */
typedef struct {
    double *freq_bins;         /* Масив частотних точок f_k від 0 до f_s/2 (Гц) */
    double *psd_density;       /* Масив значень PSD G_x(f) (В²/Гц) */
    int     num_bins;          /* Кількість частотних комірок (N_fft/2 + 1) */
    double  enbw_hz;           /* Еквівалентна шумова смуга однієї комірки (Гц) */
    int     segments_averaged; /* Кількість усереднених періодограм K */
} PsdResult;

/* Публічні функції програмного інтерфейсу */

/**
 * @brief Ініціалізація та перевірка коректності конфігурації аналізатора.
 * @param cfg Вказівник на структуру конфігурації PsdConfig.
 * @return PSD_SUCCESS у разі успіху або відповідний код помилки.
 */
int psd_analyzer_init(PsdConfig *cfg);

/**
 * @brief Обчислення спектральної щільності потужності методом Велча.
 * @param signal_in Вхідний масив відліків сигналу.
 * @param signal_len Загальна кількість відліків у масиві.
 * @param cfg Вказівник на налаштування аналізатора.
 * @param res_out Вказівник на структуру результату (пам'ять виділяється всередині).
 * @return PSD_SUCCESS або код помилки.
 */
int psd_compute_welch(const double *signal_in, int signal_len, 
                      const PsdConfig *cfg, PsdResult *res_out);

/**
 * @brief Звільнення динамічної пам'яті, виділеної під результат аналізу.
 * @param res_out Вказівник на структуру результату PsdResult.
 */
void psd_result_free(PsdResult *res_out);

#ifdef __cplusplus
}
#endif

#endif /* SPECTRAL_ANALYSIS_API_H */
