// kalman2.h — скалярна величина + онлайн-оцінка сталого зсуву нуля.
#ifndef KALMAN2_H
#define KALMAN2_H

#include <stdint.h>
#include <stdbool.h>

// Стан стану — пара (величина x, зсув нуля b) і коваріація 2×2.
typedef struct {
    float x, b;                 // оцінка величини; оцінка зсуву нуля
    float P00, P01, P10, P11;   // коваріація: [ [P00 P01], [P10 P11] ]
    float Qx;                   // шум процесу величини (більший — дозволяємо рух)
    float Qb;                   // шум процесу зсуву (крихітний — зсув майже сталий)
    float R;                    // шум виміру давача (дисперсія)
} kalman2_t;

void  kalman2_init(kalman2_t *k, float x0, float b0,
                   float Qx, float Qb, float R);

// Один такт. z — сирий вимір (бачить суму x + b). Повертає ОЧИЩЕНУ оцінку x
// (зсув уже віднято всередині). Сам зсув доступний як k->b.
float kalman2_step(kalman2_t *k, float z);

#endif // KALMAN2_H
