static void erode3(const uint8_t *src, uint8_t *dst) {
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            uint8_t v = 255;
            for (int dy = -1; dy <= 1 && v; dy++)
                for (int dx = -1; dx <= 1; dx++) {
                    int nx = x+dx, ny = y+dy;
                    if (nx<0||ny<0||nx>=W||ny>=H || src[ny*W+nx]==0) { v=0; break; }
                }
            dst[y*W+x] = v;             // білий лише якщо ВСІ сусіди білі
        }
}

static void dilate3(const uint8_t *src, uint8_t *dst) {
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            uint8_t v = 0;
            for (int dy = -1; dy <= 1 && !v; dy++)
                for (int dx = -1; dx <= 1; dx++) {
                    int nx = x+dx, ny = y+dy;
                    if (nx>=0&&ny>=0&&nx<W&&ny<H && src[ny*W+nx]) { v=255; break; }
                }
            dst[y*W+x] = v;             // білий якщо ХОЧ ОДИН сусід білий
        }
}
