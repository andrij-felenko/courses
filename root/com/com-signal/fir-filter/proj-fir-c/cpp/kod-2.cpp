/* лінійно-фазовий КІХ: buf[0] — найновіший, buf[NTAPS-1] — найстаріший */
float firf_sym_step(FirF *f, float x)
{
    for (int i = NTAPS - 1; i > 0; i--)  /* зсув на один (короткий фільтр) */
        f->buf[i] = f->buf[i - 1];
    f->buf[0] = x;

    float acc = 0.0f;
    int half = NTAPS / 2;
    for (int k = 0; k < half; k++)
        acc += f->b[k] * (f->buf[k] + f->buf[NTAPS - 1 - k]);  /* пара на один множник */
    acc += f->b[half] * f->buf[half];    /* центральний відвід — окремо */
    return acc;
}
