// Цілочисельні ціни: множимо на 1000, √2 ≈ 1.41421 → 1414.
#define ORTHO_I  1000
#define DIAG_I   1414
static int32_t g_cost_i[N_CELLS];   // ціле g замість float — швидше без FPU

static int32_t heuristic_i(int x, int y, int gx, int gy) {
    int dx = gx - x; if (dx < 0) dx = -dx;
    int dy = gy - y; if (dy < 0) dy = -dy;
    int diag     = (dx < dy) ? dx : dy;
    int straight = (dx < dy) ? (dy - dx) : (dx - dy);
    return diag * DIAG_I + straight * ORTHO_I;   // усе в цілих, без жодного float
}
