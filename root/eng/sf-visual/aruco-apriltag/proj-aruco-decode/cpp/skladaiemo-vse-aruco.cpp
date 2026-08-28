// Один кандидат quad[4] → заповнена структура Marker (id=-1, якщо не мітка).
static void decode_candidate(const uint8_t *img, int W, int Himg,
                             const Pt quad[4], const Dict *dict, Marker *out) {
    out->id = -1;
    double Hm[9], Hi[9];
    if (!homography_to_square(quad, CANON, Hm)) return;   // вироджений кандидат
    if (!invert3x3(Hm, Hi)) return;

    int cells[GRID][GRID]; uint8_t bit[GRID][GRID];
    read_grid(img, W, Himg, Hi, cells);
    cells_to_bits(cells, bit);

    // рамка: рахуємо білі клітинки в зовнішньому кільці, поріг 35%
    int border_white = 0, border_total = 0;
    for (int g = 0; g < GRID; g++) {
        int edges[4][2] = {{g,0},{g,GRID-1},{0,g},{GRID-1,g}};
        for (int e = 0; e < 4; e++) { border_total++; border_white += bit[edges[e][1]][edges[e][0]]; }
    }
    if (border_white * 100 > border_total * 35) return;   // рамка світла → не мітка

    int rot;
    int id = identify(bit, dict, &rot);
    if (id < 0) return;

    // упорядкувати кути під знайдений оберт: циклічний зсув на rot позицій
    out->id = id;
    for (int i = 0; i < 4; i++) {
        out->corner[i][0] = quad[(i + rot) & 3].x;
        out->corner[i][1] = quad[(i + rot) & 3].y;
    }
}

// Головний вхід: кадр → масив міток. cand/ncand дає крок контурів (крок 2).
// integ — буфер (W+1)*(H+1), bin — буфер W*H; викликач виділяє їх один раз.
int aruco_decode(const uint8_t *img, int W, int Himg,
                 const Dict *dict, Marker *markers, int max_markers,
                 uint32_t *integ, uint8_t *bin) {
    // Крок 1 — поріг у маску чорнила bin. Вікно 23, C=7 (типові для aruco).
    adaptive_threshold(img, W, Himg, 23, 7, bin, integ);

    // Крок 2 — контури по bin → чотирикутники-кандидати. (трасування опущено;
    //           find_quads заповнює cand[] з масок; повертає їх кількість)
    Pt cand[4]; int found = 0;
    int ncand = find_quads(bin, W, Himg, /*out*/ NULL);   // заглушка інтерфейсу
    (void)ncand; (void)cand;

    // Крок 3–5 — для кожного кандидата (тут показано на одному quad):
    //   decode_candidate(img, W, Himg, quad, dict, &markers[found]);
    //   if (markers[found].id >= 0 && found < max_markers) found++;
    return found;
}
