#include <stdio.h>
#include <math.h>

/* Спрощений демонстраційний розрахунок для 3 змінних */
int main(void) {
    /* Плаваючі оцінки */
    double a_hat[3] = { 5.45, 12.35, 8.85 };

    /* Наївне покомпонентне округлення */
    long a_round[3] = { (long)round(a_hat[0]), (long)round(a_hat[1]), (long)round(a_hat[2]) };

    /* Результат, знайдений алгоритмом LAMBDA */
    long a_lambda[3] = { 5, 12, 9 };

    printf("Плаваючий вектор (float):   [ %.2f, %.2f, %.2f ]\n",
           a_hat[0], a_hat[1], a_hat[2]);
    printf("Наївне округлення [a]:      [ %ld, %ld, %ld ]\n",
           a_round[0], a_round[1], a_round[2]);
    printf("Розв'язок LAMBDA (fix):     [ %ld, %ld, %ld ]\n",
           a_lambda[0], a_lambda[1], a_lambda[2]);

    return 0;
}
