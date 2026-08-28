// Двопороговий гістерезис. nms[] — сила після NMS; edges[] — бінарний вихід (0/255).
// lo, hi — нижній і верхній пороги. Стек на H*W пар координат.
static void hysteresis(int H, int W, const int *nms, int lo, int hi,
                       uint8_t *edges) {
    enum { WEAK = 1, STRONG = 2 };
    uint8_t *mark = (uint8_t *)calloc((size_t)H * W, 1);
    int *stack = (int *)malloc((size_t)H * W * sizeof(int));
    int sp = 0;

    // 1) класифікація + засів стеку сильними
    for (int i = 0; i < H * W; i++) {
        if      (nms[i] >= hi) { mark[i] = STRONG; stack[sp++] = i; }
        else if (nms[i] >= lo)   mark[i] = WEAK;
        // інакше mark[i] лишається 0 (не межа)
    }

    // 2) BFS від сильних: будь-який слабкий сусід стає сильним і йде в стек
    static const int DY[8] = {-1,-1,-1, 0, 0, 1, 1, 1};
    static const int DX[8] = {-1, 0, 1,-1, 1,-1, 0, 1};
    while (sp > 0) {
        int i = stack[--sp];
        int y = i / W, x = i % W;
        for (int k = 0; k < 8; k++) {
            int ny = y + DY[k], nx = x + DX[k];
            if (ny < 0 || nx < 0 || ny >= H || nx >= W) continue;
            int j = IDX(ny, nx);
            if (mark[j] == WEAK) { mark[j] = STRONG; stack[sp++] = j; }
        }
    }

    // 3) вихід: лишилися тільки сильні (сильні від народження + дотягнуті слабкі)
    for (int i = 0; i < H * W; i++)
        edges[i] = (mark[i] == STRONG) ? 255 : 0;

    free(stack);
    free(mark);
}
