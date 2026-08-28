#define BASE 8

static void rec_mult(int n, size_t a, size_t b, size_t c)
{
    if (n <= BASE) {
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                double s = rd(c + (size_t)i*N + j);
                for (int k = 0; k < n; k++)
                    s += rd(a + (size_t)i*N + k) * rd(b + (size_t)k*N + j);
                wr(c + (size_t)i*N + j, s);
            }
        return;
    }
    int h = n / 2;
    size_t A11 = a, A12 = a + h, A21 = a + (size_t)h*N, A22 = a + (size_t)h*N + h;
    size_t B11 = b, B12 = b + h, B21 = b + (size_t)h*N, B22 = b + (size_t)h*N + h;
    size_t C11 = c, C12 = c + h, C21 = c + (size_t)h*N, C22 = c + (size_t)h*N + h;

    rec_mult(h, A11, B11, C11);   rec_mult(h, A12, B21, C11);
    rec_mult(h, A11, B12, C12);   rec_mult(h, A12, B22, C12);
    rec_mult(h, A21, B11, C21);   rec_mult(h, A22, B21, C21);
    rec_mult(h, A21, B12, C22);   rec_mult(h, A22, B22, C22);
}
