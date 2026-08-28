// Налаштувати біквад на ФІЛЬТР НИЗЬКИХ ЧАСТОТ із частотою зрізу fc.
void biquad_lowpass(biquad_t *f, float fc, float fs, float Q) {
    float w0    = 2.0f * 3.14159265f * fc / fs;
    float cosw0 = cosf(w0);
    float alpha = sinf(w0) / (2.0f * Q);

    float b0 = (1.0f - cosw0) * 0.5f;
    float b1 =  1.0f - cosw0;
    float b2 = (1.0f - cosw0) * 0.5f;
    float a0 =  1.0f + alpha;
    float a1 = -2.0f * cosw0;
    float a2 =  1.0f - alpha;

    f->b0 = b0 / a0;  f->b1 = b1 / a0;  f->b2 = b2 / a0;
    f->a1 = a1 / a0;  f->a2 = a2 / a0;
    f->z1 = f->z2 = 0.0f;
}
