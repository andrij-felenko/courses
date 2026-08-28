#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double* x;
    double* y;
    double* weights;
    size_t count;
    size_t capacity;
} BarycentricInterpolator;

BarycentricInterpolator* barycentric_create(size_t initial_capacity) {
    BarycentricInterpolator* interp = (BarycentricInterpolator*)malloc(sizeof(BarycentricInterpolator));
    if (!interp) return NULL;

    interp->capacity = initial_capacity > 0 ? initial_capacity : 8;
    interp->count = 0;
    interp->x = (double*)malloc(interp->capacity * sizeof(double));
    interp->y = (double*)malloc(interp->capacity * sizeof(double));
    interp->weights = (double*)malloc(interp->capacity * sizeof(double));

    if (!interp->x || !interp->y || !interp->weights) {
        free(interp->x);
        free(interp->y);
        free(interp->weights);
        free(interp);
        return NULL;
    }

    return interp;
}

void barycentric_free(BarycentricInterpolator* interp) {
    if (interp) {
        free(interp->x);
        free(interp->y);
        free(interp->weights);
        free(interp);
    }
}

bool barycentric_add_point(BarycentricInterpolator* interp, double new_x, double new_y) {
    // Перевіряємо дублікати
    for (size_t i = 0; i < interp->count; ++i) {
        if (fabs(interp->x[i] - new_x) < 1e-12) {
            return false; // Вузол вже існує
        }
    }

    // Розширення масиву при потребі
    if (interp->count >= interp->capacity) {
        size_t new_cap = interp->capacity * 2;
        double* nx = (double*)realloc(interp->x, new_cap * sizeof(double));
        double* ny = (double*)realloc(interp->y, new_cap * sizeof(double));
        double* nw = (double*)realloc(interp->weights, new_cap * sizeof(double));
        if (!nx || !ny || !nw) return false;
        interp->x = nx;
        interp->y = ny;
        interp->weights = nw;
        interp->capacity = new_cap;
    }

    size_t n = interp->count;
    interp->x[n] = new_x;
    interp->y[n] = new_y;

    // Оновлення існуючих ваг w_k = w_k / (x_k - new_x) за O(n)
    double new_w = 1.0;
    for (size_t k = 0; k < n; ++k) {
        double diff = interp->x[k] - new_x;
        interp->weights[k] /= diff;
        new_w /= (new_x - interp->x[k]);
    }
    interp->weights[n] = new_w;
    interp->count++;

    return true;
}

double barycentric_eval(const BarycentricInterpolator* interp, double target_x) {
    if (interp->count == 0) return NAN;

    double num = 0.0;
    double den = 0.0;

    for (size_t k = 0; k < interp->count; ++k) {
        double diff = target_x - interp->x[k];
        if (fabs(diff) < 1e-12) {
            return interp->y[k]; // Точний збіг з вузлом
        }
        double term = interp->weights[k] / diff;
        num += term * interp->y[k];
        den += term;
    }

    return num / den;
}

int main(void) {
    BarycentricInterpolator* interp = barycentric_create(4);
    
    barycentric_add_point(interp, 1.0, 1.0);
    barycentric_add_point(interp, 2.0, 4.0);
    barycentric_add_point(interp, 4.0, 16.0);

    printf("Барицентрична оцінка P(3.0) = %.4f\n", barycentric_eval(interp, 3.0));

    // Динамічно додаємо 4-ту точку x=5, y=25 за O(n)
    barycentric_add_point(interp, 5.0, 25.0);
    printf("Після додавання (5.0, 25.0): P(3.0) = %.4f\n", barycentric_eval(interp, 3.0));

    barycentric_free(interp);
    return 0;
}
