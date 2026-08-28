/* src/geomcalc.c */
#include "geomcalc.h"
#include <math.h>
#include <zlib.h>
#include <stdlib.h>
#include <string.h>

double geom_triangle_area(geom_point_t a, geom_point_t b, geom_point_t c) {
    /* Формула Гауса для площі багатокутника з використанням fabs з math.h */
    double area = 0.5 * fabs(a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
    return area;
}

int geom_export_compressed_report(const geom_point_t* points, size_t count, 
                                  unsigned char* out_buf, size_t* out_size) {
    if (!points || count == 0 || !out_buf || !out_size) {
        return -1;
    }
    
    size_t raw_bytes = count * sizeof(geom_point_t);
    uLongf dest_len = (uLongf)(*out_size);
    
    int z_res = compress(out_buf, &dest_len, (const Bytef*)points, (uLong)raw_bytes);
    if (z_res != Z_OK) {
        return -2;
    }
    
    *out_size = (size_t)dest_len;
    return 0;
}
