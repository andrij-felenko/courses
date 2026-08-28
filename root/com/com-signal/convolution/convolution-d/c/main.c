// x[0..nx-1] — сигнал, h[0..nh-1] — ядро, y[0..nx+nh-2] — результат
void convolve(const float *x, int nx,
              const float *h, int nh,
              float *y)
{
    int ny = nx + nh - 1;
    for (int m = 0; m < ny; m++) {
        float acc = 0.0f;
        for (int k = 0; k < nx; k++) {
            int j = m - k;                 // індекс ядра, біжить назустріч
            if (j >= 0 && j < nh)          // лише там, де ядро накриває сигнал
                acc += x[k] * h[j];        // помнож і додай
        }
        y[m] = acc;
    }
}
