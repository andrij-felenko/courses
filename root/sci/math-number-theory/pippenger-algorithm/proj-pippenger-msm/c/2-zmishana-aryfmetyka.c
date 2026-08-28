/* Додавання афінної точки до точки в координатах Якобі: res = p_jac + p_aff */
void point_add_mixed(point_jacobian_t *res, const point_jacobian_t *p_jac, const point_affine_t *p_aff) {
    if (p_aff->is_infinity) {
        *res = *p_jac;
        return;
    }
    if (fe256_is_zero(&p_jac->Z)) {
        res->X = p_aff->x;
        res->Y = p_aff->y;
        fe256_set_one(&res->Z);
        return;
    }

    fe256_t Z1Z1, U2, S2, H, HH, I, J, V, r;
    fe256_sqr(&Z1Z1, &p_jac->Z);              /* Z1^2 */
    fe256_mul(&U2, &p_aff->x, &Z1Z1);         /* U2 = x2 * Z1^2 */
    fe256_mul(&S2, &p_aff->y, &p_jac->Z);
    fe256_mul(&S2, &S2, &Z1Z1);               /* S2 = y2 * Z1^3 */

    fe256_sub(&H, &U2, &p_jac->X);            /* H = U2 - X1 */
    fe256_sub(&r, &S2, &p_jac->Y);            /* r = S2 - Y1 */

    if (fe256_is_zero(&H)) {
        if (fe256_is_zero(&r)) {
            point_double_jacobian(res, p_jac);
        } else {
            memset(res, 0, sizeof(point_jacobian_t)); /* Точка на нескінченності */
        }
        return;
    }

    fe256_sqr(&HH, &H);                       /* HH = H^2 */
    fe256_add(&I, &HH, &HH);
    fe256_add(&I, &I, &I);                    /* I = 4 * HH */
    fe256_mul(&J, &H, &I);                    /* J = H * I */
    fe256_mul(&V, &p_jac->X, &I);             /* V = X1 * I */

    /* X3 = r^2 - J - 2*V */
    fe256_sqr(&res->X, &r);
    fe256_sub(&res->X, &res->X, &J);
    fe256_sub(&res->X, &res->X, &V);
    fe256_sub(&res->X, &res->X, &V);

    /* Y3 = r * (V - X3) - 2 * Y1 * J */
    fe256_sub(&res->Y, &V, &res->X);
    fe256_mul(&res->Y, &res->Y, &r);
    fe256_t Y1J;
    fe256_mul(&Y1J, &p_jac->Y, &J);
    fe256_sub(&res->Y, &res->Y, &Y1J);
    fe256_sub(&res->Y, &res->Y, &Y1J);

    /* Z3 = (Z1 + H)^2 - Z1^2 - HH */
    fe256_add(&res->Z, &p_jac->Z, &H);
    fe256_sqr(&res->Z, &res->Z);
    fe256_sub(&res->Z, &res->Z, &Z1Z1);
    fe256_sub(&res->Z, &res->Z, &HH);
}

/* Додавання двох точок у координатах Якобі */
void point_add_jacobian(point_jacobian_t *res, const point_jacobian_t *p1, const point_jacobian_t *p2) {
    if (fe256_is_zero(&p1->Z)) { *res = *p2; return; }
    if (fe256_is_zero(&p2->Z)) { *res = *p1; return; }

    fe256_t Z1Z1, Z2Z2, U1, U2, S1, S2, H, I, J, r, V;
    fe256_sqr(&Z1Z1, &p1->Z);
    fe256_sqr(&Z2Z2, &p2->Z);

    fe256_mul(&U1, &p1->X, &Z2Z2);
    fe256_mul(&U2, &p2->X, &Z1Z1);

    fe256_mul(&S1, &p1->Y, &p2->Z);
    fe256_mul(&S1, &S1, &Z2Z2);

    fe256_mul(&S2, &p2->Y, &p1->Z);
    fe256_mul(&S2, &S2, &Z1Z1);

    fe256_sub(&H, &U2, &U1);
    fe256_sub(&r, &S2, &S1);

    if (fe256_is_zero(&H)) {
        if (fe256_is_zero(&r)) {
            point_double_jacobian(res, p1);
        } else {
            memset(res, 0, sizeof(point_jacobian_t));
        }
        return;
    }

    fe256_add(&I, &H, &H);
    fe256_sqr(&I, &I);
    fe256_mul(&J, &H, &I);
    fe256_mul(&V, &U1, &I);

    fe256_sqr(&res->X, &r);
    fe256_sub(&res->X, &res->X, &J);
    fe256_sub(&res->X, &res->X, &V);
    fe256_sub(&res->X, &res->X, &V);

    fe256_sub(&res->Y, &V, &res->X);
    fe256_mul(&res->Y, &res->Y, &r);
    fe256_t S1J;
    fe256_mul(&S1J, &S1, &J);
    fe256_sub(&res->Y, &res->Y, &S1J);
    fe256_sub(&res->Y, &res->Y, &S1J);

    fe256_add(&res->Z, &p1->Z, &p2->Z);
    fe256_sqr(&res->Z, &res->Z);
    fe256_sub(&res->Z, &res->Z, &Z1Z1);
    fe256_sub(&res->Z, &res->Z, &Z2Z2);
    fe256_mul(&res->Z, &res->Z, &H);
}
