typedef struct {
    double x;
    double y;
} Point2D;

/* Лінійна інтерполяція між двома точками */
static inline Point2D lerp_point(Point2D p0, Point2D p1, double t) {
    Point2D p;
    p.x = (1.0 - t) * p0.x + t * p1.x;
    p.y = (1.0 - t) * p0.y + t * p1.y;
    return p;
}

/* Обчислення точки на кубічній кривій Безьє за алгоритмом де Кастельжо.
   points: масив із 4 контрольних вершин [P0, P1, P2, P3].
   t: параметр нормованого діапазону [0.0, 1.0].
   Складність: 6 операцій lerp, час O(1), пам'ять O(1). */
Point2D bezier_cubic_eval(const Point2D points[4], double t) {
    // Рівень 1: обчислення 3 проміжних точок на відрізках P0-P1, P1-P2, P2-P3
    Point2D q0 = lerp_point(points[0], points[1], t);
    Point2D q1 = lerp_point(points[1], points[2], t);
    Point2D q2 = lerp_point(points[2], points[3], t);

    // Рівень 2: обчислення 2 проміжних точок на відрізках q0-q1, q1-q2
    Point2D r0 = lerp_point(q0, q1, t);
    Point2D r1 = lerp_point(q1, q2, t);

    // Рівень 3: фінальна точка на кривій Безьє B(t)
    return lerp_point(r0, r1, t);
}
