#include <stdbool.h>
#include <stddef.h>
#include <math.h>

// Двовимірна точка з координатами подвійної точності
typedef struct {
    double x;
    double y;
} point_2d_t;

// Результати геометричного аналізу контуру багатокутника
typedef struct {
    double signed_area;  // орієнтована площа (>0: CCW, <0: CW)
    double abs_area;     // абсолютна площа
    point_2d_t centroid; // геометричний центр мас (центроїд)
    bool is_ccw;         // істинно, якщо вершини орієнтовані проти годинникової стрілки
} polygon_metrics_t;

// Обчислення площі, орієнтації та центроїда багатокутника за формулою шнурівки.
// Застосовує зсув до першої вершини для запобігання втраті точності.
bool calculate_polygon_metrics(const point_2d_t *pts, size_t count, polygon_metrics_t *out) {
    if (!pts || count < 3 || !out) {
        return false;
    }

    double double_area = 0.0;
    double cx_accum = 0.0;
    double cy_accum = 0.0;

    // Базова точка для локального зсуву (усунення катастрофічного скасування)
    const double x0 = pts[0].x;
    const double y0 = pts[0].y;

    for (size_t i = 0; i < count; ++i) {
        size_t next = (i + 1 == count) ? 0 : (i + 1);

        // Зміщені координати відносно базової вершини
        double xi = pts[i].x - x0;
        double yi = pts[i].y - y0;
        double x_next = pts[next].x - x0;
        double y_next = pts[next].y - y0;

        // Косий добуток: det | xi      yi     |
        //                    | x_next  y_next |
        double cross = (xi * y_next) - (x_next * yi);

        double_area += cross;
        cx_accum += (xi + x_next) * cross;
        cy_accum += (yi + y_next) * cross;
    }

    double signed_area = double_area * 0.5;
    out->signed_area = signed_area;
    out->abs_area = fabs(signed_area);
    out->is_ccw = (signed_area > 0.0);

    // Якщо багатокутник не вироджений у лінію чи точку, обчислюємо центроїд
    if (fabs(double_area) > 1e-12) {
        double factor = 1.0 / (3.0 * double_area);
        out->centroid.x = x0 + (cx_accum * factor);
        out->centroid.y = y0 + (cy_accum * factor);
    } else {
        out->centroid.x = x0;
        out->centroid.y = y0;
    }

    return true;
}
