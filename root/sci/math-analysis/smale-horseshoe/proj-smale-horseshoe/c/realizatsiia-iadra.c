#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    double alpha;
    double beta;
} HorseshoeParams;

bool horseshoe_forward(const Point2D* in, Point2D* out, const HorseshoeParams* params) {
    if (in->x < 0.0 || in->x > 1.0 || in->y < 0.0 || in->y > 1.0) {
        return false;
    }
    
    if (in->y >= 0.0 && in->y <= params->alpha) {
        out->x = params->alpha * in->x;
        out->y = params->beta * in->y;
        return true;
    } else if (in->y >= (1.0 - params->alpha) && in->y <= 1.0) {
        out->x = 1.0 - params->alpha * in->x;
        out->y = params->beta * (1.0 - in->y);
        return true;
    }
    
    return false;
}

bool horseshoe_inverse(const Point2D* in, Point2D* out, const HorseshoeParams* params) {
    if (in->x < 0.0 || in->x > 1.0 || in->y < 0.0 || in->y > 1.0) {
        return false;
    }
    
    if (in->x >= 0.0 && in->x <= params->alpha) {
        out->x = in->x / params->alpha;
        out->y = in->y / params->beta;
        return true;
    } else if (in->x >= (1.0 - params->alpha) && in->x <= 1.0) {
        out->x = (1.0 - in->x) / params->alpha;
        out->y = 1.0 - (in->y / params->beta);
        return true;
    }
    
    return false;
}

void compute_lyapunov(const HorseshoeParams* params, double* lyap_x, double* lyap_y) {
    *lyap_x = log(params->alpha);
    *lyap_y = log(params->beta);
}

int main(void) {
    HorseshoeParams params = { .alpha = 0.35, .beta = 2.4 };
    Point2D p = { .x = 0.4, .y = 0.2 };
    Point2D next_p;
    
    printf("--- Симуляція відображення підкови Смейла (C) ---\n");
    printf("Параметри: alpha = %.3f, beta = %.3f\n", params.alpha, params.beta);
    
    double lx, ly;
    compute_lyapunov(&params, &lx, &ly);
    printf("Показники Ляпунова: lambda_x = %.5f, lambda_y = %.5f\n", lx, ly);
    
    if (horseshoe_forward(&p, &next_p, &params)) {
        printf("Пряме відображення (%.4f, %.4f) -> (%.4f, %.4f)\n", p.x, p.y, next_p.x, next_p.y);
    } else {
        printf("Точка залишає квадрат S\n");
    }
    
    return 0;
}
