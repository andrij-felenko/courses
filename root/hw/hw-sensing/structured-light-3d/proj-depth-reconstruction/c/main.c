#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846f

typedef struct {
    float x, y, z;
    float intensity;
} Point3D;

typedef struct {
    float baseline_mm;    /* Базова лінія B між камерою та проектором */
    float focal_length_px;/* Фокусна відстань камери f_c в пікселях */
    float cx, cy;         /* Головна точка оптичної осі камери */
    int   proj_width_px;  /* Роздільна здатність проектора по горизонталі */
    int   fringe_periods; /* Кількість періодів високочастотної смуги (наприклад, 16) */
    float min_modulation; /* Поріг амплітуди B для відсікання тіней */
    float min_z_mm;       /* Мінімальна допустима дальність */
    float max_z_mm;       /* Максимальна допустима дальність */
} CalibrationParams;

/* Обчислення загорнутої фази та амплітуди модуляції з 4 кадрів */
void compute_4step_phase(const float* I0, const float* I1, 
                         const float* I2, const float* I3,
                         float* phase_out, float* mod_out,
                         int width, int height) {
    int total_pixels = width * height;
    for (int i = 0; i < total_pixels; ++i) {
        float num = I3[i] - I1[i];
        float den = I0[i] - I2[i];
        
        phase_out[i] = atan2f(num, den);
        mod_out[i]   = 0.5f * sqrtf(den * den + num * num);
    }
}

/* Двочастотне часове розгортання фази */
void temporal_unwrap(const float* coarse_phase, const float* fine_phase,
                     float* abs_phase_out, int width, int height, int n_periods) {
    int total_pixels = width * height;
    for (int i = 0; i < total_pixels; ++i) {
        /* Нормалізація грубої фази (1 період на весь кадр) до діапазону [0, 2π) */
        float phi1 = coarse_phase[i];
        if (phi1 < 0.0f) phi1 += 2.0f * PI;

        /* Нормалізація точної фази */
        float phi2 = fine_phase[i];
        if (phi2 < 0.0f) phi2 += 2.0f * PI;

        /* Визначення порядку періоду смуги k */
        float k_est = (n_periods * phi1 - phi2) / (2.0f * PI);
        int k = (int)roundf(k_est);
        if (k < 0) k = 0;
        if (k >= n_periods) k = n_periods - 1;

        /* Відновлення абсолютної неперервної фази */
        abs_phase_out[i] = phi2 + 2.0f * PI * (float)k;
    }
}

/* Тріангуляція фази у тривимірну хмару точок */
int reconstruct_point_cloud(const float* abs_phase, const float* modulation,
                            Point3D* cloud_out, int width, int height,
                            const CalibrationParams* calib) {
    int valid_points = 0;
    float max_abs_phase = 2.0f * PI * (float)calib->fringe_periods;

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int idx = y * width + x;

            /* Фільтрація тіней та перепадів яскравості за модуляцією */
            if (modulation[idx] < calib->min_modulation) {
                continue;
            }

            /* Відповідна неперервна координата на площині проектора */
            float u_proj = (abs_phase[idx] / max_abs_phase) * (float)calib->proj_width_px;

            /* Паралакс (диспаратність) вздовж ректифікованої лінії */
            float disparity = (float)x - u_proj;
            if (disparity <= 0.001f) {
                continue; /* Точка за нескінченністю або некоректна */
            }

            /* Гіперболічна тріангуляція Z = B · f / d */
            float z = (calib->baseline_mm * calib->focal_length_px) / disparity;
            if (z < calib->min_z_mm || z > calib->max_z_mm) {
                continue;
            }

            /* Зворотна проекція в декартові координати камери (X, Y) */
            float x_mm = ((float)x - calib->cx) * z / calib->focal_length_px;
            float y_mm = ((float)y - calib->cy) * z / calib->focal_length_px;

            cloud_out[valid_points].x = x_mm;
            cloud_out[valid_points].y = y_mm;
            cloud_out[valid_points].z = z;
            cloud_out[valid_points].intensity = modulation[idx];
            valid_points++;
        }
    }
    return valid_points;
}

/* Збереження хмари точок у форматі ASCII PLY */
bool export_ply(const char* filepath, const Point3D* cloud, int count) {
    FILE* fp = fopen(filepath, "w");
    if (!fp) return false;

    fprintf(fp, "ply\n");
    fprintf(fp, "format ascii 1.0\n");
    fprintf(fp, "element vertex %d\n", count);
    fprintf(fp, "property float x\n");
    fprintf(fp, "property float y\n");
    fprintf(fp, "property float z\n");
    fprintf(fp, "property float intensity\n");
    fprintf(fp, "end_header\n");

    for (int i = 0; i < count; ++i) {
        fprintf(fp, "%.3f %.3f %.3f %.1f\n", 
                cloud[i].x, cloud[i].y, cloud[i].z, cloud[i].intensity);
    }

    fclose(fp);
    return true;
}
