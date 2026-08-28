typedef struct { int x, y; } Pt;

// площа замкненого контуру (формула шнурівки) і периметр
static void contour_geom(const Pt *c, int n, double *area, double *perim) {
    double A = 0.0, P = 0.0;
    for (int i = 0; i < n; i++) {
        Pt a = c[i], b = c[(i + 1) % n];
        A += (double)a.x * b.y - (double)b.x * a.y;     // шнурівка (Гаусса)
        double dx = b.x - a.x, dy = b.y - a.y;
        P += sqrt(dx * dx + dy * dy);                    // довжина сторони
    }
    *area  = fabs(A) * 0.5;
    *perim = P;
}

static int is_circle(const Pt *c, int n, double min_area) {
    if (n < 5) return 0;                                 // замало точок на коло
    double A, P;
    contour_geom(c, n, &A, &P);
    if (A < min_area || P <= 0.0) return 0;              // шум або вироджений контур
    double circularity = 4.0 * 3.14159265 * A / (P * P);
    return circularity > 0.85;                           // близько до ідеального кола
}
