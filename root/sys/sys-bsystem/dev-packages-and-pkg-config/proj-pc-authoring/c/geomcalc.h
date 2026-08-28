/* include/geomcalc.h */
#ifndef GEOMCALC_H
#define GEOMCALC_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double x;
    double y;
} geom_point_t;

/* Обчислює площу трикутника за координатами вершин */
double geom_triangle_area(geom_point_t a, geom_point_t b, geom_point_t c);

/* Генерує стиснений бінарний звіт про геометрію (використовує zlib) */
int geom_export_compressed_report(const geom_point_t* points, size_t count, 
                                  unsigned char* out_buf, size_t* out_size);

#ifdef __cplusplus
}
#endif

#endif /* GEOMCALC_H */
