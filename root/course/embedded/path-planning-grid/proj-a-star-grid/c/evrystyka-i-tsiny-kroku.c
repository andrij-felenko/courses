#define ORTHO_COST  1.0f
#define DIAG_COST   1.41421356f     // √2

// Восьмеро сусідів: dx, dy, ціна кроку.
typedef struct { int dx, dy; float cost; } Neighbour;
static const Neighbour NEIGH[8] = {
    {+1,  0, ORTHO_COST}, {-1,  0, ORTHO_COST},
    { 0, +1, ORTHO_COST}, { 0, -1, ORTHO_COST},
    {+1, +1, DIAG_COST},  {+1, -1, DIAG_COST},
    {-1, +1, DIAG_COST},  {-1, -1, DIAG_COST},
};

// Октильна (діагональна) евристика — точна довжина шляху в порожньому полі.
static float heuristic(int x, int y, int gx, int gy) {
    int dx = gx - x; if (dx < 0) dx = -dx;
    int dy = gy - y; if (dy < 0) dy = -dy;
    int diag     = (dx < dy) ? dx : dy;      // скільки навскіс
    int straight = (dx < dy) ? (dy - dx) : (dx - dy);  // решта прямо
    return diag * DIAG_COST + straight * ORTHO_COST;
}
