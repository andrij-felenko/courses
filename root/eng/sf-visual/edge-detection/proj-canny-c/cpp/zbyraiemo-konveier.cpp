// Повний Канні. in[H*W] → edges[H*W] (0/255). lo, hi — пороги гістерезису.
// Повертає 0 при успіху, -1 при браку пам'яті.
int canny(int H, int W, const uint8_t *in, uint8_t *edges, int lo, int hi) {
    size_t n = (size_t)H * W;
    uint8_t *blur = malloc(n);
    int     *mag  = malloc(n * sizeof(int));
    uint8_t *dir  = malloc(n);
    int     *thin = malloc(n * sizeof(int));
    if (!blur || !mag || !dir || !thin) {
        free(blur); free(mag); free(dir); free(thin);
        return -1;
    }
    gauss_blur(H, W, in, blur);          // 1) шум геть
    sobel_grad(H, W, blur, mag, dir);    // 2) сила + сектор напряму
    nms_quantized(H, W, mag, dir, thin); // 3) стоншити до гребеня
    hysteresis(H, W, thin, lo, hi, edges); // 4) сполучити й відсіяти
    free(blur); free(mag); free(dir); free(thin);
    return 0;
}
