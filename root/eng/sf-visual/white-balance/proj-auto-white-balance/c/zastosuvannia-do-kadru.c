// Застосувати коефіцієнти до всього кадру на місці (in-place).
void apply_awb(RGB *img, int n, uint16_t gR, uint16_t gG, uint16_t gB) {
    for (int i = 0; i < n; i++) {
        img[i].r = apply_gain(img[i].r, gR);
        img[i].g = apply_gain(img[i].g, gG);
        img[i].b = apply_gain(img[i].b, gB);
    }
}

// Повний автобаланс: оцінити й застосувати.
void auto_white_balance(RGB *img, int H, int W) {
    int n = H * W;
    uint16_t gR, gG, gB;
    estimate_awb(img, n, &gR, &gG, &gB);
    apply_awb(img, n, gR, gG, gB);
}
