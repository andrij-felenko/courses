// За квантованим сектором лишаємо тільки локальні максимуми вздовж градієнта.
static void nms_quantized(int H, int W, const int *mag, const uint8_t *dir,
                          int *out) {
    for (int i = 0; i < H * W; i++) out[i] = 0;        // обнулити, край лишиться 0
    for (int y = 1; y < H - 1; y++) {
        for (int x = 1; x < W - 1; x++) {
            int m = mag[IDX(y, x)];
            int a, b;                                   // два сусіди вздовж градієнта
            switch (dir[IDX(y, x)]) {                                      // порівнюємо ВЗДОВЖ градієнта
                case 0: a = mag[IDX(y,   x-1)]; b = mag[IDX(y,   x+1)]; break;  // ліво / право
                case 1: a = mag[IDX(y-1, x-1)]; b = mag[IDX(y+1, x+1)]; break;  // діаг. \ : ↖ / ↘
                case 2: a = mag[IDX(y-1, x)];   b = mag[IDX(y+1, x)];   break;  // верх / низ
                default:a = mag[IDX(y+1, x-1)]; b = mag[IDX(y-1, x+1)]; break;  // діаг. / : ↙ / ↗
            }
            if (m >= a && m >= b) out[IDX(y, x)] = m;   // гребінь — лишаємо силу
        }
    }
}
