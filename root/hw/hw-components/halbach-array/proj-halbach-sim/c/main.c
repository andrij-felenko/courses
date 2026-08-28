#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846
#define MU_0 (4.0 * PI * 1e-7)
#define EPSILON 1e-9

/* Структура двовимірного вектора поля */
typedef struct {
    double x;
    double y;
} Vec2D;

/* Структура прямокутного магнітного сегмента */
typedef struct {
    double x_min;
    double x_max;
    double y_min;
    double y_max;
    double mx; /* Намагніченість по осі X, А/м */
    double my; /* Намагніченість по осі Y, А/м */
} MagnetBlock;

/* Обчислення внеску магнітної індукції від одного прямокутного блоку */
Vec2D compute_block_field(const MagnetBlock *b, double x, double y) {
    Vec2D b_field = {0.0, 0.0};
    
    /* Чотири вершини прямокутника в порядку обходу:
       1: (x_min, y_min)
       2: (x_max, y_min)
       3: (x_max, y_max)
       4: (x_min, y_max) */
    double vx[4] = {b->x_min, b->x_max, b->x_max, b->x_min};
    double vy[4] = {b->y_min, b->y_min, b->y_max, b->y_max};
    
    /* Знаки для чергування вершин за формулою Гріна */
    double signs[4] = {+1.0, -1.0, +1.0, -1.0};
    
    double bx_sum = 0.0;
    double by_sum = 0.0;
    
    for (int k = 0; k < 4; ++k) {
        double dx = x - vx[k];
        double dy = y - vy[k];
        double r_sq = dx * dx + dy * dy;
        
        /* Захист від сингулярності на кутах */
        if (r_sq < EPSILON * EPSILON) {
            r_sq = EPSILON * EPSILON;
        }
        
        double r = sqrt(r_sq);
        double log_r = log(r);
        double theta = atan2(dy, dx);
        
        double sign = signs[k];
        
        /* Аналітичні вирази для граней еквівалентних зарядів */
        bx_sum += sign * (b->my * log_r + b->mx * theta);
        by_sum += sign * (b->my * theta - b->mx * log_r);
    }
    
    double factor = MU_0 / (2.0 * PI);
    b_field.x = factor * bx_sum;
    b_field.y = factor * by_sum;
    
    return b_field;
}

/* Обчислення сумарного поля від масиву блоків */
Vec2D compute_array_field(const MagnetBlock *blocks, size_t count, double x, double y) {
    Vec2D total = {0.0, 0.0};
    for (size_t i = 0; i < count; ++i) {
        Vec2D fb = compute_block_field(&blocks[i], x, y);
        total.x += fb.x;
        total.y += fb.y;
    }
    return total;
}

int main(void) {
    /* Параметри масиву: 5 сегментів, довжина періоду λ = 40 мм */
    const size_t num_segments = 5;
    const double block_width = 0.010;  /* 10 мм на сегмент */
    const double block_height = 0.010; /* 10 мм товщина */
    const double remanence_br = 1.40;  /* NdFeB N48: 1.40 Тл */
    const double m_val = remanence_br / MU_0; /* Намагніченість M0, А/м */
    
    MagnetBlock halbach[5];
    MagnetBlock conventional[5];
    
    /* Напрямки для масиву Гальбаха: ↑, →, ↓, ←, ↑ */
    double h_dirs[5][2] = {
        { 0.0, +1.0}, /* ↑ N */
        {+1.0,  0.0}, /* → E */
        { 0.0, -1.0}, /* ↓ S */
        {-1.0,  0.0}, /* ← W */
        { 0.0, +1.0}  /* ↑ N */
    };
    
    /* Напрямки для звичайного масиву: ↑, ↓, ↑, ↓, ↑ */
    double c_dirs[5][2] = {
        {0.0, +1.0},
        {0.0, -1.0},
        {0.0, +1.0},
        {0.0, -1.0},
        {0.0, +1.0}
    };
    
    for (size_t i = 0; i < num_segments; ++i) {
        double x0 = i * block_width;
        double x1 = x0 + block_width;
        double y0 = -block_height;
        double y1 = 0.0;
        
        halbach[i].x_min = x0;
        halbach[i].x_max = x1;
        halbach[i].y_min = y0;
        halbach[i].y_max = y1;
        halbach[i].mx = h_dirs[i][0] * m_val;
        halbach[i].my = h_dirs[i][1] * m_val;
        
        conventional[i].x_min = x0;
        conventional[i].x_max = x1;
        conventional[i].y_min = y0;
        conventional[i].y_max = y1;
        conventional[i].mx = c_dirs[i][0] * m_val;
        conventional[i].my = c_dirs[i][1] * m_val;
    }
    
    printf("=== ПЕРЕВІРКА СУПЕРПОЗИЦІЇ МАСИВУ ГАЛЬБАХА ===\n\n");
    printf("Зазор z = 2.0 мм над центром масиву (x = 25.0 мм):\n");
    
    double test_x = 0.025; /* Центр середнього сегмента (25 мм) */
    double airgap = 0.002; /* 2 мм зазор */
    
    /* Робочий бік (y = +airgap) */
    Vec2D b_h_strong = compute_array_field(halbach, num_segments, test_x, +airgap);
    Vec2D b_c_strong = compute_array_field(conventional, num_segments, test_x, +airgap);
    
    /* Слабкий бік (y = -block_height - airgap) */
    double y_weak = -block_height - airgap;
    Vec2D b_h_weak = compute_array_field(halbach, num_segments, test_x, y_weak);
    Vec2D b_c_weak = compute_array_field(conventional, num_segments, test_x, y_weak);
    
    double mod_h_strong = hypot(b_h_strong.x, b_h_strong.y);
    double mod_h_weak   = hypot(b_h_weak.x, b_h_weak.y);
    double mod_c_strong = hypot(b_c_strong.x, b_c_strong.y);
    double mod_c_weak   = hypot(b_c_weak.x, b_c_weak.y);
    
    printf("  Масив Гальбаха:  |B_сильний| = %.4f Тл, |B_слабкий| = %.4f Тл\n", 
           mod_h_strong, mod_h_weak);
    printf("  Звичайний масив: |B_сильний| = %.4f Тл, |B_слабкий| = %.4f Тл\n", 
           mod_c_strong, mod_c_weak);
    printf("  Коефіцієнт підсилення на робочому боці: %.2f x\n", 
           mod_h_strong / mod_c_strong);
    printf("  Коефіцієнт пригнічення слабкого боку:   %.2f x (у %d разів менше)\n",
           mod_h_weak / mod_h_strong, (int)(mod_h_strong / mod_h_weak));
    
    return 0;
}
