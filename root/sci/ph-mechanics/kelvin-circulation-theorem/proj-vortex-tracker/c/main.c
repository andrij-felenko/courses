#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    double x;
    double y;
} Vector2D;

/* Поле швидкості 2D вихору Тейлора — Гріна */
Vector2D velocity_field(double x, double y, double t) {
    Vector2D u;
    u.x = -sin(PI * x) * cos(PI * y) * exp(-0.01 * t);
    u.y =  cos(PI * x) * sin(PI * y) * exp(-0.01 * t);
    return u;
}

/* Інтегрування позиції частинки методом RK4 */
Vector2D advance_rk4(Vector2D r, double t, double dt) {
    Vector2D k1 = velocity_field(r.x, r.y, t);
    
    Vector2D r2 = {r.x + 0.5 * dt * k1.x, r.y + 0.5 * dt * k1.y};
    Vector2D k2 = velocity_field(r2.x, r2.y, t + 0.5 * dt);
    
    Vector2D r3 = {r.x + 0.5 * dt * k2.x, r.y + 0.5 * dt * k2.y};
    Vector2D k3 = velocity_field(r3.x, r3.y, t + 0.5 * dt);
    
    Vector2D r4 = {r.x + dt * k3.x, r.y + dt * k3.y};
    Vector2D k4 = velocity_field(r4.x, r4.y, t + dt);
    
    Vector2D r_new;
    r_new.x = r.x + (dt / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
    r_new.y = r.y + (dt / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y);
    return r_new;
}

/* Обчислення дискретної циркуляції вздовж замкненого контуру */
double compute_circulation(const Vector2D* contour, int num_points, double t) {
    double gamma = 0.0;
    for (int i = 0; i < num_points; ++i) {
        int prev = (i - 1 + num_points) % num_points;
        int next = (i + 1) % num_points;
        
        double dx = 0.5 * (contour[next].x - contour[prev].x);
        double dy = 0.5 * (contour[next].y - contour[prev].y);
        
        Vector2D u = velocity_field(contour[i].x, contour[i].y, t);
        gamma += u.x * dx + u.y * dy;
    }
    return gamma;
}

int main(void) {
    const int N = 100;
    const double dt = 0.01;
    const int steps = 500;
    
    Vector2D* contour = (Vector2D*)malloc(sizeof(Vector2D) * N);
    if (!contour) return 1;

    /* Початковий коловий контур радіуса R = 0.25 навколо точки (0.5, 0.5) */
    double R = 0.25;
    for (int i = 0; i < N; ++i) {
        double theta = 2.0 * PI * i / N;
        contour[i].x = 0.5 + R * cos(theta);
        contour[i].y = 0.5 + R * sin(theta);
    }

    double t = 0.0;
    double gamma_initial = compute_circulation(contour, N, t);
    printf("t = %5.2f | Circulation Gamma = %.8f\n", t, gamma_initial);

    for (int step = 1; step <= steps; ++step) {
        for (int i = 0; i < N; ++i) {
            contour[i] = advance_rk4(contour[i], t, dt);
        }
        t += dt;
        
        if (step % 100 == 0) {
            double gamma_current = compute_circulation(contour, N, t);
            double rel_error = fabs(gamma_current - gamma_initial) / gamma_initial;
            printf("t = %5.2f | Circulation Gamma = %.8f | Rel Error = %.2e\n", 
                   t, gamma_current, rel_error);
        }
    }

    free(contour);
    return 0;
}
