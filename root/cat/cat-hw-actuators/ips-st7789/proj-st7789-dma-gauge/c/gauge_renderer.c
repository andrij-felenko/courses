/**
 * @file gauge_renderer.c
 * @brief Реалізація цілочисельного сканлайн-рендерингу шкали та фільтра демпфування стрілки.
 */

#include "gauge_renderer.h"
#include "st7789.h"

/* Масштабний множник тригонометричного LUT (формат Q10, 1.0 = 1024) */
#define TRIG_SCALE_Q10 1024

/*
 * Компактна таблиця синусів для першого квадранта (0°..90°) у форматі Q10 (1024 = 1.0).
 * Займає всього 91 * 2 = 182 байти Flash-пам'яті.
 * Значення розраховані як: round(1024 * sin(deg * PI / 180)).
 */
static const int16_t sin_lut_q10_0_to_90[91] = {
       0,   18,   36,   54,   71,   89,  107,  125,  143,  160,
     178,  195,  213,  230,  248,  265,  282,  299,  316,  333,
     350,  367,  384,  400,  417,  433,  449,  465,  481,  496,
     512,  527,  543,  558,  573,  587,  602,  616,  630,  644,
     658,  672,  685,  698,  711,  724,  737,  749,  761,  773,
     784,  796,  807,  818,  828,  839,  849,  859,  868,  878,
     887,  896,  904,  912,  920,  928,  935,  943,  949,  956,
     962,  968,  974,  979,  984,  989,  994,  998, 1002, 1005,
    1008, 1011, 1014, 1016, 1018, 1020, 1022, 1023, 1023, 1024,
    1024
};

/* Обчислення синуса для довільного кута за допомогою симетрії 4-х квадрантів */
static int16_t trig_sin_q10(int16_t angle_deg) {
    /* Нормалізація в інтервал [0, 359] */
    int16_t a = angle_deg % 360;
    if (a < 0) {
        a += 360;
    }

    if (a <= 90) {
        return sin_lut_q10_0_to_90[a];
    } else if (a <= 180) {
        return sin_lut_q10_0_to_90[180 - a];
    } else if (a <= 270) {
        return (int16_t)(-sin_lut_q10_0_to_90[a - 180]);
    } else {
        return (int16_t)(-sin_lut_q10_0_to_90[360 - a]);
    }
}

/* Обчислення косинуса через зсув фази: cos(a) = sin(a + 90) */
static int16_t trig_cos_q10(int16_t angle_deg) {
    return trig_sin_q10(angle_deg + 90);
}

void gauge_renderer_init(gauge_state_t *gauge, int16_t min_val, int16_t max_val, uint8_t damping_shift) {
    gauge->min_value = min_val;
    gauge->max_value = max_val;
    gauge->target_value = min_val;
    gauge->damping_shift = damping_shift;

    /* Початкове положення відповідає мінімуму шкали */
    gauge->current_angle_deg = GAUGE_MIN_ANGLE_DEG;
    gauge->current_angle_fp = (int32_t)GAUGE_MIN_ANGLE_DEG << GAUGE_FP_SHIFT;
}

void gauge_update_needle(gauge_state_t *gauge, int16_t target_value) {
    /* Обмеження цільового значення допустимим діапазоном шкали */
    if (target_value < gauge->min_value) {
        target_value = gauge->min_value;
    } else if (target_value > gauge->max_value) {
        target_value = gauge->max_value;
    }
    gauge->target_value = target_value;

    /* Розрахунок цільового кута в градусах */
    const int32_t val_range = (int32_t)gauge->max_value - (int32_t)gauge->min_value;
    const int32_t val_rel = (int32_t)gauge->target_value - (int32_t)gauge->min_value;
    const int16_t target_angle_deg = (int16_t)(GAUGE_MIN_ANGLE_DEG +
        (val_rel * GAUGE_TOTAL_SWEEP_DEG) / val_range);

    /*
     * Експоненційний цифровий фільтр згладжування (демпфування коливань стрілки):
     * current_angle += (target_angle - current_angle) >> shift
     *
     * Обчислення виконуються у форматі Q8 (помножено на 256), щоб уникнути
     * ефекту мертвої зони (коли різниця менша за дільник і цілочисельне ділення дає 0).
     */
    const int32_t target_angle_fp = (int32_t)target_angle_deg << GAUGE_FP_SHIFT;
    const int32_t error_fp = target_angle_fp - gauge->current_angle_fp;
    gauge->current_angle_fp += (error_fp >> gauge->damping_shift);

    /* Оновлюємо цілочисельний кут для геометричних функцій */
    gauge->current_angle_deg = (int16_t)(gauge->current_angle_fp >> GAUGE_FP_SHIFT);
}

void gauge_render_scanline(const gauge_state_t *gauge, uint16_t y, uint16_t *line_buffer) {
    const int16_t dy = (int16_t)y - GAUGE_CENTER_Y;
    const int32_t dy_sq = (int32_t)dy * (int32_t)dy;

    /*
     * 1. Розрахунок геометрії стрілки для поточного кадру.
     * Кут вимірюється від вертикальної осі дисплея (0° = вгору).
     * X = CenterX + L * sin(angle)
     * Y = CenterY - L * cos(angle)
     */
    const int16_t angle = gauge->current_angle_deg;
    const int16_t sin_a = trig_sin_q10(angle);
    const int16_t cos_a = trig_cos_q10(angle);

    /* Координати вістря стрілки */
    const int16_t tip_x = GAUGE_CENTER_X + (int16_t)(((int32_t)GAUGE_NEEDLE_LENGTH * sin_a) / TRIG_SCALE_Q10);
    const int16_t tip_y = GAUGE_CENTER_Y - (int16_t)(((int32_t)GAUGE_NEEDLE_LENGTH * cos_a) / TRIG_SCALE_Q10);

    /* Координати хвостової противаги стрілки */
    const int16_t tail_x = GAUGE_CENTER_X - (int16_t)(((int32_t)GAUGE_NEEDLE_TAIL_LENGTH * sin_a) / TRIG_SCALE_Q10);
    const int16_t tail_y = GAUGE_CENTER_Y + (int16_t)(((int32_t)GAUGE_NEEDLE_TAIL_LENGTH * cos_a) / TRIG_SCALE_Q10);

    /* Напрямний вектор вздовж осі стрілки: V = Tip - Tail */
    const int32_t vx = (int32_t)tip_x - (int32_t)tail_x;
    const int32_t vy = (int32_t)tip_y - (int32_t)tail_y;
    const int32_t v_len_sq = vx * vx + vy * vy;

    /* Перевірка вертикального діапазону (bounding box) для оптимізації */
    const int16_t min_needle_y = (tip_y < tail_y ? tip_y : tail_y) - 2;
    const int16_t max_needle_y = (tip_y > tail_y ? tip_y : tail_y) + 2;
    const bool needle_row_active = ((int16_t)y >= min_needle_y) && ((int16_t)y <= max_needle_y) && (v_len_sq > 0);

    /* Палітра стилізованого інтерфейсу */
    const uint16_t col_bg        = COLOR_RGB565(15U, 15U, 18U);   /* Зовнішній чорний фон */
    const uint16_t col_bezel_hi  = COLOR_RGB565(180U, 185U, 190U);/* Світла частина металевого обідка */
    const uint16_t col_bezel_lo  = COLOR_RGB565(70U, 75U, 85U);   /* Темна частина металевого обідка */
    const uint16_t col_dial_bg   = COLOR_RGB565(26U, 28U, 34U);   /* Глибокий графітовий циферблат */
    const uint16_t col_arc_green = COLOR_RGB565(30U, 210U, 70U);  /* Зелена зона (норма) */
    const uint16_t col_arc_yel   = COLOR_RGB565(250U, 190U, 20U); /* Жовта зона (увага) */
    const uint16_t col_arc_red   = COLOR_RGB565(240U, 35U, 35U);  /* Червона зона (критично) */
    const uint16_t col_needle    = COLOR_RGB565(255U, 40U, 40U);  /* Яскрава спортивна стрілка */
    const uint16_t col_hub       = COLOR_RGB565(45U, 48U, 55U);   /* Темна металева центральна кришка */
    const uint16_t col_hub_dot   = COLOR_RGB565(220U, 220U, 230U);/* Відблиск на осі */

    /* 2. Попіксельний розрахунок сканлайну */
    for (uint16_t x = 0; x < GAUGE_DISPLAY_WIDTH; x++) {
        const int16_t dx = (int16_t)x - GAUGE_CENTER_X;
        const int32_t dist_sq = (int32_t)dx * (int32_t)dx + dy_sq;
        uint16_t pixel;

        if (dist_sq > (int32_t)GAUGE_RADIUS_BEZEL_OUT * GAUGE_RADIUS_BEZEL_OUT) {
            /* Піксель лежить за межами круглого корпусу приладу */
            pixel = col_bg;
        } else if (dist_sq >= (int32_t)GAUGE_RADIUS_BEZEL_IN * GAUGE_RADIUS_BEZEL_IN) {
            /* Текстура металевого безеля зі світловим градієнтом */
            pixel = (dy < 0) ? col_bezel_hi : col_bezel_lo;
        } else {
            /* Внутрішній простір циферблата */
            pixel = col_dial_bg;

            /* Кольорова кругова шкала (дуга значень) */
            if (dist_sq <= (int32_t)GAUGE_RADIUS_ARC_OUT * GAUGE_RADIUS_ARC_OUT &&
                dist_sq >= (int32_t)GAUGE_RADIUS_ARC_IN * GAUGE_RADIUS_ARC_IN) {
                /*
                 * Виріз у нижній частині шкали (сектор 90°):
                 * dy > 0 та |dx| < dy утворюють розрив під стрілкою приладу
                 */
                const int16_t abs_dx = (dx < 0) ? (int16_t)(-dx) : dx;
                if (!(dy > 0 && abs_dx < dy)) {
                    if (dx < -25) {
                        pixel = col_arc_green;
                    } else if (dx < 35) {
                        pixel = col_arc_yel;
                    } else {
                        pixel = col_arc_red;
                    }
                }
            }

            /* Рендеринг стрілки приладу */
            if (needle_row_active) {
                /* Вектор від хвоста стрілки до поточного пікселя: W = P - Tail */
                const int32_t wx = (int32_t)x - (int32_t)tail_x;
                const int32_t wy = (int32_t)y - (int32_t)tail_y;

                /* Проекція вектора W на вісь стрілки: proj = W · V */
                const int32_t dot_proj = wx * vx + wy * vy;

                if (dot_proj >= 0 && dot_proj <= v_len_sq) {
                    /*
                     * Квадрат відстані по нормалі від пікселя до відрізка стрілки:
                     * dist_perp^2 = |W|^2 - (W · V)^2 / |V|^2
                     */
                    const int32_t w_len_sq = wx * wx + wy * wy;
                    const int32_t perp_dist_sq = w_len_sq - (int32_t)(((int64_t)dot_proj * dot_proj) / v_len_sq);

                    /* Товщина стрілки: напівширина 1.5 пікселя (квадрат <= 2) */
                    if (perp_dist_sq <= 2) {
                        pixel = col_needle;
                    }
                }
            }

            /* Центральна кришка кріплення стрілки (Hub) */
            if (dist_sq <= (int32_t)GAUGE_RADIUS_HUB * GAUGE_RADIUS_HUB) {
                if (dist_sq <= (int32_t)GAUGE_RADIUS_HUB_CORE * GAUGE_RADIUS_HUB_CORE) {
                    pixel = col_hub_dot;
                } else {
                    pixel = col_hub;
                }
            }
        }

        line_buffer[x] = pixel;
    }
}
