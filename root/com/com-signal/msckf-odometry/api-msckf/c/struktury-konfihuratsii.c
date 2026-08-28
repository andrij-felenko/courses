#include <stdint.h>
#include <stdbool.h>

typedef struct {
    double x, y, z;
} MsckfVec3;

typedef struct {
    double w, x, y, z;
} MsckfQuat;

typedef struct {
    /* Геометричне калібрування камери відносно IMU (Body -> Camera) */
    MsckfVec3 body_T_cam;         /* вектор зміщення камери у системі корпусу, м */
    MsckfQuat body_R_cam;         /* кватерніон повороту камери відносно корпусу */
    
    /* Параметри ковзного вікна */
    uint32_t max_window_size;     /* максимальна кількість поз камери (типово 15–20) */
    uint32_t min_track_length;    /* мінімальна довжина треку для тріангуляції (типово 3) */
    
    /* Шумові характеристики давачів */
    double gyro_noise_density;    /* спектральна густина шуму гіроскопа, рад/(с·√Гц) */
    double accel_noise_density;   /* спектральна густина шуму акселерометра, м/(с²·√Гц) */
    double gyro_bias_random_walk; /* випадкове блукання зсуву гіроскопа, рад/(с²·√Гц) */
    double accel_bias_random_walk;/* випадкове блукання зсуву акселерометра, м/(с³·√Гц) */
    double pixel_noise_std;       /* СКП похибки детектора точок, нормовані пікселі */
    
    /* Чисельні пороги та перевірки */
    double min_triangulation_deg; /* мінімальний паралакс для тріангуляції, градуси (типово 1.5–2.0) */
    double chi2_rejection_prob;   /* рівень довіри для тесту χ² (типово 0.95 або 0.99) */
    bool enable_fej;              /* увімкнення Першої Оцінки Якобіанів (First-Estimate Jacobians) */
} MsckfConfig;
