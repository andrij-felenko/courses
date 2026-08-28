#define NX 32   /* ширина сітки */
#define NY 32   /* висота сітки */

/* Релаксація потенціалу на сітці V[y][x] методом Гаусса–Зейделя.
   fixed[y][x] != 0 — клітина зафіксована (межа чи електрод), її не рухаємо.
   Повертає число зроблених проходів (max_iter, якщо не збіглося). */
int relax(float V[NY][NX], const unsigned char fixed[NY][NX],
          float eps, int max_iter)
{
    for (int iter = 1; iter <= max_iter; ++iter) {
        float delta = 0.0f;                  /* найбільша зміна за прохід */
        for (int y = 1; y < NY - 1; ++y) {
            for (int x = 1; x < NX - 1; ++x) {
                if (fixed[y][x])             /* задані клітини не чіпаємо */
                    continue;
                float avg = 0.25f * (V[y-1][x] + V[y+1][x] +
                                     V[y][x-1] + V[y][x+1]);
                float d = avg - V[y][x];
                if (d < 0.0f)
                    d = -d;                  /* |зміна| */
                if (d > delta)
                    delta = d;
                V[y][x] = avg;               /* пишемо на місці — Гаусс–Зейдель */
            }
        }
        if (delta < eps)                     /* картина застигла — виходимо */
            return iter;
    }
    return max_iter;                         /* ліміт проходів вичерпано */
}
