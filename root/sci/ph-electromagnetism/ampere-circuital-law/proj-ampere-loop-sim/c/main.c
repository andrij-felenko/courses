#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Магнітна стала μ₀ (Гн/м)
#define MU_0 (4.0 * M_PI * 1e-7)

// Структура для опису прямолінійного провідника зі струмом
typedef struct {
    double x;       // X-координата провідника у метрах
    double y;       // Y-координата провідника у метрах
    double current; // Величина струму в Амперах (знак вказує напрямок)
} Wire;

// Структура для опису 2D точки / вектора
typedef struct {
    double x;
    double y;
} Point2D;

/**
 * Обчислює сумарний вектор магнітної індукції B = (Bx, By) у точці спостереження (x, y)
 * від усієї сукупності провідників за принципом суперпозиції.
 */
void compute_magnetic_field(double x, double y, const Wire* wires, size_t num_wires, double* bx, double* by) {
    *bx = 0.0;
    *by = 0.0;
    const double eps_sq = 1e-14; // Регуляризація для уникнення ділення на 0

    for (size_t i = 0; i < num_wires; ++i) {
        double dx = x - wires[i].x;
        double dy = y - wires[i].y;
        double r2 = dx * dx + dy * dy;

        // Якщо точка збігається з центром провідника, пропускаємо для уникнення сингулярності
        if (r2 < eps_sq) {
            continue;
        }

        // Закон Біо — Савара для прямого струму: B = (μ₀ · I) / (2·π·r)
        double coeff = (MU_0 * wires[i].current) / (2.0 * M_PI * r2);
        *bx += -coeff * dy;
        *by +=  coeff * dx;
    }
}

/**
 * Обчислює криволінійний інтеграл (циркуляцію) ∮ B · dl вздовж замкненого полігонального контуру.
 */
double calculate_circulation(const Point2D* contour, size_t num_points, const Wire* wires, size_t num_wires) {
    double circulation = 0.0;

    for (size_t i = 0; i < num_points; ++i) {
        size_t next_i = (i + 1) % num_points;

        // Початок та кінець поточного сегмента контуру
        double x1 = contour[i].x;
        double y1 = contour[i].y;
        double x2 = contour[next_i].x;
        double y2 = contour[next_i].y;

        // Обчислення середини сегмента (для підвищення точності квадратури)
        double x_mid = (x1 + x2) * 0.5;
        double y_mid = (y1 + y2) * 0.5;

        // Вектор елемента довжини dl = (dx, dy)
        double dl_x = x2 - x1;
        double dl_y = y2 - y1;

        // Обчислення вектора індукції B у середній точці
        double bx, by;
        compute_magnetic_field(x_mid, y_mid, wires, num_wires, &bx, &by);

        // Скалярний добуток B · dl
        circulation += (bx * dl_x + by * dl_y);
    }

    return circulation;
}

int main(void) {
    printf("=====================================================\n");
    printf("   Чисельне моделювання теореми Ампера про циркуляцію  \n");
    printf("=====================================================\n\n");

    // 1. Конфігурація джерел струму у просторі
    Wire wires[] = {
        { .x =  0.02, .y =  0.01, .current =  12.5 }, // Всередині контуру (+12.5 А)
        { .x = -0.04, .y = -0.03, .current =  -5.0 }, // Всередині контуру (-5.0 А)
        { .x =  0.35, .y =  0.40, .current =  50.0 }  // Зовні контуру (+50.0 А)
    };
    size_t num_wires = sizeof(wires) / sizeof(wires[0]);

    // 2. Створення замкненого еліптичного контуру (піввісі a=0.20м, b=0.10м)
    size_t contour_steps = 2000;
    Point2D* contour = (Point2D*)malloc(contour_steps * sizeof(Point2D));
    if (!contour) {
        fprintf(stderr, "Помилка виділення пам'яті під контур!\n");
        return 1;
    }

    double a = 0.20; // Велика піввісь (м)
    double b = 0.10; // Мала піввісь (м)
    for (size_t i = 0; i < contour_steps; ++i) {
        double angle = 2.0 * M_PI * (double)i / (double)contour_steps;
        contour[i].x = a * cos(angle);
        contour[i].y = b * sin(angle);
    }

    // 3. Обчислення чисельної циркуляції
    double calc_circ = calculate_circulation(contour, contour_steps, wires, num_wires);

    // 4. Теоретичне значення за законом Ампера: μ₀ · (I₁ + I₂)
    double enclosed_current = wires[0].current + wires[1].current; // 12.5 - 5.0 = 7.5 A
    double theory_circ = MU_0 * enclosed_current;
    double rel_error = fabs(calc_circ - theory_circ) / theory_circ * 100.0;

    printf("Розташування провідників:\n");
    for (size_t i = 0; i < num_wires; ++i) {
        printf("  Провідник №%zu: pos=(%.2f, %.2f) м, струм = %+.1f A\n", 
               i + 1, wires[i].x, wires[i].y, wires[i].current);
    }

    printf("\nПараметри контуру інтегрування:\n");
    printf("  Тип: Еліпс (a=%.2f м, b=%.2f м), кількість сегментів = %zu\n\n", a, b, contour_steps);

    printf("РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ:\n");
    printf("  Сумарний охоплений струм (I_охоп): %+.3f A\n", enclosed_current);
    printf("  Чисельна циркуляція ∮ B·dl:        %.9e Тл·м\n", calc_circ);
    printf("  Теоретична циркуляція (μ₀·I_охоп):  %.9e Тл·м\n", theory_circ);
    printf("  Відносна обчислювальна похибка:    %.6f %%\n", rel_error);

    free(contour);
    return 0;
}
