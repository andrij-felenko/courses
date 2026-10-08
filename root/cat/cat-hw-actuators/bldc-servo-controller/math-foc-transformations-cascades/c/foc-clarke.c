#include <math.h>

typedef struct {
    float a;
    float b;
    float c;
} Vector3f;

typedef struct {
    float alpha;
    float beta;
} Vector2f_AlphaBeta;

typedef struct {
    float d;
    float q;
} Vector2f_DQ;

// Пряме перетворення Кларка (амплітудно-збережене)
Vector2f_AlphaBeta foc_clarke(float i_a, float i_b) {
    Vector2f_AlphaBeta out;
    out.alpha = i_a;
    out.beta = (i_a + 2.0f * i_b) * 0.57735026919f; // 1 / sqrt(3)
    return out;
}

// Пряме перетворення Парка
Vector2f_DQ foc_park(Vector2f_AlphaBeta in, float sin_theta, float cos_theta) {
    Vector2f_DQ out;
    out.d =  in.alpha * cos_theta + in.beta * sin_theta;
    out.q = -in.alpha * sin_theta + in.beta * cos_theta;
    return out;
}

// Зворотне перетворення Парка
Vector2f_AlphaBeta foc_inv_park(Vector2f_DQ in, float sin_theta, float cos_theta) {
    Vector2f_AlphaBeta out;
    out.alpha = in.d * cos_theta - in.q * sin_theta;
    out.beta  = in.d * sin_theta + in.q * cos_theta;
    return out;
}

// Зворотне перетворення Кларка
Vector3f foc_inv_clarke(Vector2f_AlphaBeta in) {
    Vector3f out;
    out.a = in.alpha;
    out.b = -0.5f * in.alpha + 0.86602540378f * in.beta; // sqrt(3) / 2
    out.c = -0.5f * in.alpha - 0.86602540378f * in.beta;
    return out;
}
