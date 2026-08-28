// помаранчевий — один суцільний діапазон тону
static inline int is_orange(Hsv p) {
    return p.h2 >= 10 && p.h2 <= 20 && p.s >= 120 && p.v >= 60;
}

// червоний — ДВА діапазони: біля 0 і біля 180 (h2), бо тон перетинає край кола
static inline int is_red(Hsv p) {
    int hue_ok = (p.h2 <= 8) || (p.h2 >= 172);   // 0..16° АБО 344..360°
    return hue_ok && p.s >= 120 && p.v >= 60;
}

static void threshold_color(const uint8_t *rgb, uint8_t *m) {
    for (int i = 0; i < W * H; i++) {
        Hsv p = rgb_to_hsv(rgb[3*i], rgb[3*i+1], rgb[3*i+2]);
        m[i] = is_red(p) ? 255 : 0;        // тут — шукаємо червоний маркер
    }
}
