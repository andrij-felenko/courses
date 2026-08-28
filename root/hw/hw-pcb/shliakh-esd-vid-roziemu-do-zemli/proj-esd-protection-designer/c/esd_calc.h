/* esd_calc.h — Заголовний файл бібліотеки інженерного розрахунку ESD-тракту (C99) */
#ifndef ESD_CALC_H
#define ESD_CALC_H

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Рівні випробувальної напруги за стандартом IEC 61000-4-2 */
typedef enum {
    ESD_LEVEL_1_2KV = 0, /* Контактний розряд 2 кВ (піковий струм 7.5 А) */
    ESD_LEVEL_2_4KV = 1, /* Контактний розряд 4 кВ (піковий струм 15.0 А) */
    ESD_LEVEL_3_6KV = 2, /* Контактний розряд 6 кВ (піковий струм 22.5 А) */
    ESD_LEVEL_4_8KV = 3, /* Контактний розряд 8 кВ (піковий струм 30.0 А) */
    ESD_LEVEL_CUSTOM = 4  /* Довільна випробувальна напруга в кіловольтах */
} EsdTestLevel;

/* Геометрія провідників і переходів друкованої плати */
typedef struct {
    double trace_len_mm;       /* Довжина вхідної доріжки роз'єм-TVS (мм) */
    double trace_width_mm;     /* Ширина сигнальної доріжки (мм) */
    double cu_thickness_um;    /* Товщина міді (типово 35 мкм для 1 oz) */
    double dielectric_h_mm;    /* Висота діелектрика до опорної землі GND (мм) */
    double stub_len_mm;        /* Довжина T-відгалуження до площадки TVS (мм, 0 = feedthrough) */
    double stub_width_mm;      /* Ширина доріжки відгалуження (мм) */
    double via_height_mm;      /* Довжина перехідного отвору (товщина плати, мм) */
    double via_diameter_mm;    /* Діаметр отвору via (мм, типово 0.3 мм) */
    double via_pitch_mm;       /* Відстань між центрами отворів (мм) */
    unsigned int via_count;    /* Кількість паралельних отворів заземлення TVS */
} PcbTraceConfig;

/* Параметри TVS-діода */
typedef struct {
    double v_breakdown;        /* Напруга лавинного пробою V_BR (В) */
    double r_dynamic;          /* Динамічний диференційний опір R_dyn (Ом) */
    double c_io_pf;            /* Паразитна ємність виводу C_io (пФ) */
    double l_package_nh;       /* Власна індуктивність виводів корпусу (нГн) */
    double v_standoff;         /* Максимальна робоча напруга V_RWM (В) */
    double p_ppm_watts;        /* Пікова імпульсна потужність розсіювання (Вт) */
} TvsDiodeConfig;

/* Параметри захищуваного входу мікроконтролера чи мікросхеми */
typedef struct {
    double v_supply;           /* Напруга живлення V_DD (В) */
    double v_abs_max;          /* Абсолютна максимальна напруга виводу (В) */
    double i_internal_max_ma;  /* Гранично допустимий імпульсний струм внутрішніх діодів (мА) */
    double r_internal_dyn;     /* Динамічний опір внутрішнього діода кристала (Ом) */
    double c_pin_pf;           /* Вхідна паразитна ємність буфера (пФ) */
    double r_series_ohms;      /* Встановлений на платі послідовний резистор (Ом) */
} ProtectedIcConfig;

/* Результати детального інженерного розрахунку */
typedef struct {
    double peak_current_a;       /* Піковий струм розряду стандарту (А) */
    double max_di_dt_a_per_ns;   /* Максимальна швидкість наростання di/dt (А/нс) */
    double l_stub_nh;            /* Індуктивність відгалуження до діода (нГн) */
    double l_gnd_array_nh;       /* Еквівалентна індуктивність масиву отворів GND (нГн) */
    double l_total_parasitic_nh; /* Сумарна паразитна індуктивність скидання (нГн) */
    double v_inductive_overshoot;/* Індуктивний стрибок напруги L * (di/dt) (В) */
    double v_tvs_clamped_peak;   /* Повний пік напруги на контактній площадці TVS (В) */
    double v_ic_pin_peak;        /* Пікова залишкова напруга на вході мікросхеми (В) */
    double i_internal_diode_ma;  /* Струм крізь внутрішні захисні діоди чипа (мА) */
    double r_series_recommended; /* Рекомендований мінімальний опір R_series (Ом) */
    double cutoff_freq_mhz;      /* Смуга пропускання за рівнем -3 дБ (МГц) */
    bool   is_safe_voltage;      /* Чи перебуває напруга в межах v_abs_max */
    bool   is_safe_current;      /* Чи перебуває струм діодів у межах безпеки */
    bool   is_design_passed;     /* Підсумковий вердикт валідності захисту */
} EsdAnalysisResult;

/* Функції розрахунку */
double esd_calc_microstrip_inductance(double len_mm, double width_mm, double thickness_um);
double esd_calc_via_array_inductance(double h_mm, double d_mm, double pitch_mm, unsigned int count);
double esd_calc_iec_current_at_time(EsdTestLevel level, double custom_kv, double t_ns);

bool esd_analyze_protection_path(EsdTestLevel level,
                                 double custom_kv,
                                 const PcbTraceConfig* trace,
                                 const TvsDiodeConfig* tvs,
                                 const ProtectedIcConfig* ic,
                                 EsdAnalysisResult* result);

#ifdef __cplusplus
}
#endif

#endif /* ESD_CALC_H */
