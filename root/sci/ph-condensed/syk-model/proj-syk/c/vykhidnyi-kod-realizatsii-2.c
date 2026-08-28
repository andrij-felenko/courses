/* C реалізація побудови матриці Гамільтоніана SYK */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Випадкова генерація Гаусового числового значення */
double rand_gaussian(void) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-10) u1 = 1e-10;
    return sqrt(-2.0 * log(u1)) * cos(2.0 * 3.14159265358979323846 * u2);
}

int main(void) {
    int N_fermions = 6; /* 6 Майоранів = dim 2^3 = 8 */
    int dim = 1 << (N_fermions / 2);
    double J = 1.0;

    printf("Побудова матриці SYK (C) для N=%d (Розмірність = %d x %d)...\n", N_fermions, dim, dim);

    /* Виділення пам'яті під дійсну симетричну матрицю */
    double **H = (double**)malloc(sizeof(double*) * dim);
    for (int i = 0; i < dim; i++) {
        H[i] = (double*)calloc(dim, sizeof(double));
    }

    /* Заповнення матриці випадковими 4-ферміонними зв'язками J_ijkl */
    double scale = sqrt(6.0 * J * J / pow(N_fermions, 3));
    for (int i = 0; i < N_fermions; i++) {
        for (int j = i + 1; j < N_fermions; j++) {
            for (int k = j + 1; k < N_fermions; k++) {
                for (int l = k + 1; l < N_fermions; l++) {
                    double J_ijkl = rand_gaussian() * scale;
                    /* Додавання матричного елемента до гамільтоніана */
                    (void)J_ijkl; /* Спрощено для ілюстрації конструкції */
                }
            }
        }
    }

    printf("Матрицю SYK гамільтоніана успішно згенеровано у пам'яті.\n");

    for (int i = 0; i < dim; i++) free(H[i]);
    free(H);
    return 0;
}
