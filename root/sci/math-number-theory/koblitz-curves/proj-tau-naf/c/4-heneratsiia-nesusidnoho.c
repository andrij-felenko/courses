/* Генерація канонічної форми TNAF для редукованого залишку rho */
size_t koblitz_generate_tnaf(int8_t *tnaf, size_t max_len, ztau_elem_t rho, int8_t mu) {
    size_t len = 0;
    int64_t r0 = rho.r0;
    int64_t r1 = rho.r1;

    while ((r0 != 0 || r1 != 0) && len < max_len) {
        if (r0 & 1) {
            /* Правило Солінаса: u = 2 - ((r0 - 2*r1*mu) mod 4) */
            int64_t val = (r0 - 2 * r1 * mu) % 4;
            if (val < 0) val += 4;
            int8_t u = (int8_t)(2 - val);
            if (u != 1 && u != -1) {
                u = (val == 3) ? -1 : 1;
            }
            r0 -= u;
            tnaf[len++] = u;
        } else {
            tnaf[len++] = 0;
        }

        /* Ділення алгебраїчного числа (r0 + r1*tau) на tau */
        int64_t half_r0 = r0 / 2;
        int64_t next_r0 = r1 + mu * half_r0;
        int64_t next_r1 = -half_r0;

        r0 = next_r0;
        r1 = next_r1;
    }
    return len;
}
