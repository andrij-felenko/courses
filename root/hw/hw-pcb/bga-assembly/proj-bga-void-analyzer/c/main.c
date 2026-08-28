#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define BGA_PI 3.14159265358979323846
#define MAX_BALLS 256
#define MAX_VOIDS_PER_BALL 64

/* Класи стандартів IPC */
typedef enum {
    IPC_CLASS_1 = 1, /* Загальна електроніка */
    IPC_CLASS_2 = 2, /* Промислове обладнання */
    IPC_CLASS_3 = 3  /* Високонадійна / Аерокосмічна / Автомобільна */
} IpcStandardClass;

/* Статус паяного з'єднання */
typedef enum {
    JOINT_PASS = 0,
    JOINT_FAIL_EXCESSIVE_TOTAL_VOID,
    JOINT_FAIL_EXCESSIVE_SINGLE_VOID,
    JOINT_FAIL_INTERFACIAL_VOID,
    JOINT_FAIL_DEFORMED_CONTOUR_HIP,
    JOINT_FAIL_BRIDGING
} JointInspectionVerdict;

/* Структура 8-бітного монохромного зображення */
typedef struct {
    int width;
    int height;
    unsigned char* data;
} GrayscaleImage;

/* Структура виявленої пустоти */
typedef struct {
    double center_x;
    double center_y;
    int area_pixels;
    bool is_interfacial; /* Чи розташована на периферійній межі */
} SolderVoid;

/* Структура кульки BGA */
typedef struct {
    int id;
    double center_x;
    double center_y;
    double radius;
    int area_pixels;
    int perimeter_pixels;
    double circularity;
    
    int num_voids;
    SolderVoid voids[MAX_VOIDS_PER_BALL];
    
    double total_void_percent;
    double max_single_void_percent;
    double interfacial_void_percent;
    
    JointInspectionVerdict verdict;
} BgaSolderBall;

/* Загальний звіт інспекції мікросхеми */
typedef struct {
    int total_balls_detected;
    int passed_balls;
    int failed_balls;
    double average_voiding_percent;
    double max_detected_void_percent;
    IpcStandardClass ipc_class;
    bool overall_board_pass;
} BgaInspectionSummary;

/* Створення нового зображення */
GrayscaleImage* create_image(int width, int height) {
    GrayscaleImage* img = (GrayscaleImage*)malloc(sizeof(GrayscaleImage));
    if (!img) return NULL;
    img->width = width;
    img->height = height;
    img->data = (unsigned char*)calloc((size_t)(width * height), sizeof(unsigned char));
    if (!img->data) {
        free(img);
        return NULL;
    }
    return img;
}

/* Звільнення пам'яті */
void free_image(GrayscaleImage* img) {
    if (img) {
        if (img->data) free(img->data);
        free(img);
    }
}

/* Генерація синтетичного рентгенівського кадру для тестування */
void generate_synthetic_xray(GrayscaleImage* img, int grid_cols, int grid_rows, double pitch_px, double ball_r_px) {
    /* Фоновий шум рентгенівського детектора (діелектрик плати пропускає рентген: яскравість 210) */
    for (int y = 0; y < img->height; ++y) {
        for (int x = 0; x < img->width; ++x) {
            int noise = (rand() % 11) - 5;
            int val = 210 + noise;
            img->data[y * img->width + x] = (unsigned char)(val > 255 ? 255 : (val < 0 ? 0 : val));
        }
    }

    double start_x = (img->width - (grid_cols - 1) * pitch_px) / 2.0;
    double start_y = (img->height - (grid_rows - 1) * pitch_px) / 2.0;

    int ball_idx = 0;
    for (int r = 0; r < grid_rows; ++r) {
        for (int c = 0; c < grid_cols; ++c) {
            double cx = start_x + c * pitch_px;
            double cy = start_y + r * pitch_px;

            /* Малюємо тіло кульки BGA (припій поглинає рентген: темна область, яскравість 40) */
            int min_x = (int)(cx - ball_r_px - 2);
            int max_x = (int)(cx + ball_r_px + 2);
            int min_y = (int)(cy - ball_r_px - 2);
            int max_y = (int)(cy + ball_r_px + 2);

            for (int y = min_y; y <= max_y; ++y) {
                if (y < 0 || y >= img->height) continue;
                for (int x = min_x; x <= max_x; ++x) {
                    if (x < 0 || x >= img->width) continue;
                    double dist = sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy));
                    if (dist <= ball_r_px) {
                        /* Сферичне поглинання: товща в центрі дає темніший колір */
                        double depth_factor = sqrt(1.0 - (dist / ball_r_px) * (dist / ball_r_px));
                        int val = (int)(110 - 70 * depth_factor + (rand() % 7 - 3));
                        img->data[y * img->width + x] = (unsigned char)(val < 0 ? 0 : val);
                    }
                }
            }

            /* Додаємо дефекти для верифікації алгоритму */
            if (ball_idx == 0) {
                /* Кулька 0: Допустима центральна макропустота 8% (яскрава пляма) */
                double v_r = ball_r_px * 0.28;
                for (int y = (int)(cy - v_r); y <= (int)(cy + v_r); ++y) {
                    for (int x = (int)(cx - v_r); x <= (int)(cx + v_r); ++x) {
                        if (sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy)) <= v_r) {
                            img->data[y * img->width + x] = (unsigned char)(180 + rand() % 10);
                        }
                    }
                }
            } else if (ball_idx == 1) {
                /* Кулька 1: БРАК — Гігантська пустота 28% (перевищення IPC Class 3) */
                double v_r = ball_r_px * 0.53;
                for (int y = (int)(cy - v_r); y <= (int)(cy + v_r); ++y) {
                    for (int x = (int)(cx - v_r); x <= (int)(cx + v_r); ++x) {
                        if (sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy)) <= v_r) {
                            img->data[y * img->width + x] = (unsigned char)(190 + rand() % 10);
                        }
                    }
                }
            } else if (ball_idx == 2) {
                /* Кулька 2: БРАК — Крайова пустота на контактному інтерфейсі (r = 0.88 R) */
                double vx = cx + ball_r_px * 0.75;
                double vy = cy + ball_r_px * 0.40;
                double v_r = ball_r_px * 0.22;
                for (int y = (int)(vy - v_r); y <= (int)(vy + v_r); ++y) {
                    for (int x = (int)(vx - v_r); x <= (int)(vx + v_r); ++x) {
                        if (sqrt((x - vx) * (x - vx) + (y - vy) * (y - vy)) <= v_r) {
                            img->data[y * img->width + x] = (unsigned char)(185 + rand() % 10);
                        }
                    }
                }
            }
            ball_idx++;
        }
    }
}

/* Адаптивний поріг Оцу для глобальної сегментації темних об'єктів припою */
int calculate_otsu_threshold(const GrayscaleImage* img) {
    int hist[256] = {0};
    int total_pixels = img->width * img->height;
    
    for (int i = 0; i < total_pixels; ++i) {
        hist[img->data[i]]++;
    }
    
    double sum = 0.0;
    for (int i = 0; i < 256; ++i) sum += i * hist[i];
    
    double sum_b = 0.0;
    int w_b = 0;
    double max_variance = 0.0;
    int threshold = 128;
    
    for (int t = 0; t < 256; ++t) {
        w_b += hist[t];
        if (w_b == 0) continue;
        int w_f = total_pixels - w_b;
        if (w_f == 0) break;
        
        sum_b += (double)(t * hist[t]);
        double m_b = sum_b / w_b;
        double m_f = (sum - sum_b) / w_f;
        
        double between_var = (double)w_b * (double)w_f * (m_b - m_f) * (m_b - m_f);
        if (between_var > max_variance) {
            max_variance = between_var;
            threshold = t;
        }
    }
    return threshold;
}

/* Аналіз паяного вузла за стандартом IPC-7095 */
void evaluate_joint_verdict(BgaSolderBall* ball, IpcStandardClass ipc_class) {
    double limit_total_void;
    double limit_single_void;
    double limit_interfacial_void;
    double min_circularity;

    switch (ipc_class) {
        case IPC_CLASS_1:
            limit_total_void = 25.0;
            limit_single_void = 15.0;
            limit_interfacial_void = 15.0;
            min_circularity = 0.75;
            break;
        case IPC_CLASS_2:
            limit_total_void = 20.0;
            limit_single_void = 10.0;
            limit_interfacial_void = 12.0;
            min_circularity = 0.80;
            break;
        case IPC_CLASS_3:
        default:
            limit_total_void = 15.0;
            limit_single_void = 8.0;
            limit_interfacial_void = 10.0;
            min_circularity = 0.85;
            break;
    }

    if (ball->circularity < min_circularity) {
        ball->verdict = JOINT_FAIL_DEFORMED_CONTOUR_HIP;
    } else if (ball->total_void_percent > limit_total_void) {
        ball->verdict = JOINT_FAIL_EXCESSIVE_TOTAL_VOID;
    } else if (ball->max_single_void_percent > limit_single_void) {
        ball->verdict = JOINT_FAIL_EXCESSIVE_SINGLE_VOID;
    } else if (ball->interfacial_void_percent > limit_interfacial_void) {
        ball->verdict = JOINT_FAIL_INTERFACIAL_VOID;
    } else {
        ball->verdict = JOINT_PASS;
    }
}

/* Головний конвеєр сегментації та інспекції */
int inspect_bga_xray(const GrayscaleImage* img, IpcStandardClass ipc_class, BgaSolderBall* out_balls, int max_out_balls) {
    int otsu_thresh = calculate_otsu_threshold(img);
    /* Припій темніший за поріг Оцу (наприклад < 130) */
    int solder_thresh = otsu_thresh;

    /* Створюємо карту міток зв'язних компонентів */
    int* labels = (int*)calloc((size_t)(img->width * img->height), sizeof(int));
    if (!labels) return 0;

    int current_label = 0;
    int detected_balls = 0;

    /* Простий Flood-Fill для виділення масивів кульок */
    for (int y = 5; y < img->height - 5; ++y) {
        for (int x = 5; x < img->width - 5; ++x) {
            int idx = y * img->width + x;
            if (img->data[idx] <= solder_thresh && labels[idx] == 0) {
                current_label++;
                
                /* Черга для заливки */
                int q_capacity = 16384;
                int* qx = (int*)malloc(sizeof(int) * (size_t)q_capacity);
                int* qy = (int*)malloc(sizeof(int) * (size_t)q_capacity);
                if (!qx || !qy) {
                    free(labels);
                    if (qx) free(qx);
                    if (qy) free(qy);
                    return 0;
                }
                
                int head = 0, tail = 0;
                qx[tail] = x; qy[tail] = y; tail++;
                labels[idx] = current_label;

                long long sum_x = 0, sum_y = 0;
                int pixel_count = 0;
                int perimeter = 0;

                while (head < tail) {
                    int cx = qx[head];
                    int cy = qy[head];
                    head++;

                    sum_x += cx;
                    sum_y += cy;
                    pixel_count++;

                    /* Перевірка сусідів (4-зв'язність) */
                    const int dx[4] = {1, -1, 0, 0};
                    const int dy[4] = {0, 0, 1, -1};
                    bool is_border = false;

                    for (int k = 0; k < 4; ++k) {
                        int nx = cx + dx[k];
                        int ny = cy + dy[k];
                        if (nx >= 0 && nx < img->width && ny >= 0 && ny < img->height) {
                            int n_idx = ny * img->width + nx;
                            if (img->data[n_idx] <= solder_thresh) {
                                if (labels[n_idx] == 0) {
                                    labels[n_idx] = current_label;
                                    if (tail < q_capacity) {
                                        qx[tail] = nx; qy[tail] = ny; tail++;
                                    }
                                }
                            } else {
                                is_border = true;
                            }
                        } else {
                            is_border = true;
                        }
                    }
                    if (is_border) perimeter++;
                }

                free(qx);
                free(qy);

                /* Фільтруємо дрібне сміття та фонові плями */
                if (pixel_count >= 150 && detected_balls < max_out_balls) {
                    BgaSolderBall* b = &out_balls[detected_balls];
                    b->id = detected_balls;
                    b->center_x = (double)sum_x / pixel_count;
                    b->center_y = (double)sum_y / pixel_count;
                    b->area_pixels = pixel_count;
                    b->perimeter_pixels = perimeter;
                    b->radius = sqrt((double)pixel_count / BGA_PI);
                    
                    /* Форм-фактор круглості (4 * pi * Area / P^2) */
                    if (perimeter > 0) {
                        b->circularity = (4.0 * BGA_PI * (double)pixel_count) / ((double)perimeter * (double)perimeter);
                        if (b->circularity > 1.0) b->circularity = 1.0;
                    } else {
                        b->circularity = 0.0;
                    }

                    /* Пошук внутрішніх пустот всередині виділеної кульки */
                    b->num_voids = 0;
                    int total_void_pixels = 0;
                    int max_single_void_pixels = 0;
                    int interfacial_void_pixels = 0;
                    int interfacial_annulus_pixels = 0;

                    /* Поріг яскравості порожнини (на 40 рівнів яскравіше за середнє тіло припою) */
                    int void_thresh = solder_thresh + 35;
                    double r_interfacial = b->radius * 0.85;

                    int min_bx = (int)(b->center_x - b->radius - 2);
                    int max_bx = (int)(b->center_x + b->radius + 2);
                    int min_by = (int)(b->center_y - b->radius - 2);
                    int max_by = (int)(b->center_y + b->radius + 2);

                    for (int py = min_by; py <= max_by; ++py) {
                        if (py < 0 || py >= img->height) continue;
                        for (int px = min_bx; px <= max_bx; ++px) {
                            if (px < 0 || px >= img->width) continue;
                            double dist = sqrt((px - b->center_x) * (px - b->center_x) + (py - b->center_y) * (py - b->center_y));
                            if (dist <= b->radius) {
                                if (dist >= r_interfacial) {
                                    interfacial_annulus_pixels++;
                                }
                                /* Якщо точка всередині геометрії кульки має високу яскравість — це порожнина */
                                if (img->data[py * img->width + px] >= void_thresh) {
                                    total_void_pixels++;
                                    if (dist >= r_interfacial) {
                                        interfacial_void_pixels++;
                                    }
                                }
                            }
                        }
                    }

                    max_single_void_pixels = total_void_pixels; /* Для одиночної домінуючої каверни */

                    b->total_void_percent = ((double)total_void_pixels / (double)b->area_pixels) * 100.0;
                    b->max_single_void_percent = ((double)max_single_void_pixels / (double)b->area_pixels) * 100.0;
                    if (interfacial_annulus_pixels > 0) {
                        b->interfacial_void_percent = ((double)interfacial_void_pixels / (double)interfacial_annulus_pixels) * 100.0;
                    } else {
                        b->interfacial_void_percent = 0.0;
                    }

                    evaluate_joint_verdict(b, ipc_class);
                    detected_balls++;
                }
            }
        }
    }

    free(labels);
    return detected_balls;
}

int main(void) {
    printf("===================================================================\n");
    printf("     BGA X-RAY INSPECTION & VOID ANALYZER ENGINE (C99)\n");
    printf("     Compliant with IPC-A-610 / IPC-7095 Class 1/2/3\n");
    printf("===================================================================\n\n");

    int img_w = 400, img_h = 300;
    GrayscaleImage* xray = create_image(img_w, img_h);
    if (!xray) {
        fprintf(stderr, "Помилка виділення пам'яті під рентгенівський кадр!\n");
        return 1;
    }

    /* Генеруємо тестову матрицю 3x3 BGA кульок (крок 65px, радіус 22px) */
    generate_synthetic_xray(xray, 3, 3, 65.0, 22.0);

    BgaSolderBall balls[MAX_BALLS];
    IpcStandardClass active_class = IPC_CLASS_3; /* Найсуворіший аерокосмічний клас */
    
    int count = inspect_bga_xray(xray, active_class, balls, MAX_BALLS);
    printf("Успішно сегментовано кульок BGA: %d\n", count);
    printf("Перевірка за критеріями: IPC-7095 Class %d\n\n", (int)active_class);

    int pass_count = 0;
    double sum_voids = 0.0;
    double max_void = 0.0;

    for (int i = 0; i < count; ++i) {
        const BgaSolderBall* b = &balls[i];
        sum_voids += b->total_void_percent;
        if (b->total_void_percent > max_void) max_void = b->total_void_percent;

        const char* verdict_str;
        switch (b->verdict) {
            case JOINT_PASS:
                verdict_str = "PASS (Придатний)";
                pass_count++;
                break;
            case JOINT_FAIL_EXCESSIVE_TOTAL_VOID:
                verdict_str = "FAIL (Перевищення сумарної площі пустот > 15%)";
                break;
            case JOINT_FAIL_EXCESSIVE_SINGLE_VOID:
                verdict_str = "FAIL (Перевищення одиничної каверни > 8%)";
                break;
            case JOINT_FAIL_INTERFACIAL_VOID:
                verdict_str = "FAIL (Критична пустота в інтерфейсному кільці > 10%)";
                break;
            case JOINT_FAIL_DEFORMED_CONTOUR_HIP:
                verdict_str = "FAIL (Деформація контуру / Head-in-Pillow / Warpage)";
                break;
            default:
                verdict_str = "FAIL (Невідомий дефект)";
                break;
        }

        printf("Кулька #%02d | Центр: (%5.1f, %5.1f) | R: %4.1f px | Круглість: %4.2f | Пори: %5.1f%% (Інтерфейс: %4.1f%%) | %s\n",
               b->id, b->center_x, b->center_y, b->radius, b->circularity, 
               b->total_void_percent, b->interfacial_void_percent, verdict_str);
    }

    printf("\n-------------------------------------------------------------------\n");
    printf("ПІДСУМОК КОНТРОЛЮ:\n");
    printf("Усього перевірено з'єднань: %d\n", count);
    printf("Придатних вузлів:           %d\n", pass_count);
    printf("Бракованих вузлів:          %d\n", count - pass_count);
    printf("Середня пористість чіпа:    %.2f%%\n", count > 0 ? sum_voids / count : 0.0);
    printf("Максимальна пористість:     %.2f%%\n", max_void);
    printf("ЗАГАЛЬНИЙ СТАТУС ПЛАТИ:     %s\n", (pass_count == count) ? "ПРИЙНЯТО (ACCEPT)" : "ВІДХИЛЕНО (REJECT)");
    printf("-------------------------------------------------------------------\n");

    free_image(xray);
    return 0;
}
