/* Додавання двох точок кривої у координатах Лопеса-Дахаба */
void point_add(point_proj_t *r, const point_proj_t *p, const point_proj_t *q);

/* Повне скалярне множення точки Q = [k]P на кривій Кобліца */
void koblitz_scalar_mul_tnaf(point_proj_t *Q, const point_proj_t *P, ztau_elem_t rho, int8_t mu) {
    int8_t tnaf[MAX_TNAF_LEN];
    size_t len = koblitz_generate_tnaf(tnaf, MAX_TNAF_LEN, rho, mu);

    point_proj_t negP;
    point_negate(&negP, P);

    /* Ініціалізація точки нескінченності: Q = O */
    Q->is_infinity = true;

    /* Схема Горнера: обхід від старшого розряду (len - 1) до молодшого (0) */
    for (size_t i = len; i > 0; --i) {
        size_t idx = i - 1;
        
        /* Заміна геометричного подвоєння [2]Q на ендоморфізм Фробеніуса */
        point_frobenius(Q, Q);

        if (tnaf[idx] == 1) {
            point_add(Q, Q, P);
        } else if (tnaf[idx] == -1) {
            point_add(Q, Q, &negP);
        }
    }
}
