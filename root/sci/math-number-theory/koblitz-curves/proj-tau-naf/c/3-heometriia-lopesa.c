/* Покоординатний ендоморфізм Фробеніуса: tau(x, y) = (x², y²) */
void point_frobenius(point_proj_t *out, const point_proj_t *in) {
    if (in->is_infinity) {
        out->is_infinity = true;
        return;
    }
    fe233_sqr(&out->X, &in->X);
    fe233_sqr(&out->Y, &in->Y);
    fe233_sqr(&out->Z, &in->Z);
    out->is_infinity = false;
}

/* Заперечення точки в характеристиці 2: -(X : Y : Z) = (X : X*Z + Y : Z) */
void point_negate(point_proj_t *out, const point_proj_t *in) {
    if (in->is_infinity) {
        out->is_infinity = true;
        return;
    }
    out->X = in->X;
    out->Z = in->Z;
    /* У координатах Лопеса-Дахаба: Y' = Y + X * Z */
    /* Тут виконується fe233_mul_add(&out->Y, &in->Y, &in->X, &in->Z); */
    out->is_infinity = false;
}
