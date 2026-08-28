// thin[] ← локальні максимуми сили вздовж квантованого напряму.
static void nms_quantized(int H, int W, const int *mag, const uint8_t *dir,
                          int *thin) {
    const int Wn = W;
    for (int i = 0; i < H * W; i++) thin[i] = 0;
    for (int y = 1; y < H - 1; y++)
        for (int x = 1; x < W - 1; x++) {
            int c = mag[y * Wn + x];
            int a, b;
            switch (dir[y * Wn + x]) {                 // сектор 0..3
                case 0: a = mag[y*Wn + x-1];     b = mag[y*Wn + x+1];     break; // ─
                case 1: a = mag[(y+1)*Wn + x-1]; b = mag[(y-1)*Wn + x+1]; break; // /
                case 2: a = mag[(y-1)*Wn + x];   b = mag[(y+1)*Wn + x];   break; // │
                default:a = mag[(y-1)*Wn + x-1]; b = mag[(y+1)*Wn + x+1]; break; // \
            }
            if (c >= a && c >= b) thin[y * Wn + x] = c; // на гребені — лишаємо
        }
}
