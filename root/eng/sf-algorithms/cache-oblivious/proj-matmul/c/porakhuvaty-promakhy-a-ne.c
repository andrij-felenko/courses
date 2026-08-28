static void naive_mult(void)
{
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            double s = rd(C_OFF + (size_t)i*N + j);
            for (int k = 0; k < N; k++)
                s += rd(A_OFF + (size_t)i*N + k) * rd(B_OFF + (size_t)k*N + j);
            wr(C_OFF + (size_t)i*N + j, s);
        }
}
