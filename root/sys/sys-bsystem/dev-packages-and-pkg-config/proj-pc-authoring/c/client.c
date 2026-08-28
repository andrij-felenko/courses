/* client.c */
#include <geomcalc.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    geom_point_t p1 = {0.0, 0.0};
    geom_point_t p2 = {4.0, 0.0};
    geom_point_t p3 = {0.0, 3.0};
    
    double area = geom_triangle_area(p1, p2, p3);
    printf("Обчислена площа трикутника: %.2f (очікується 6.00)\n", area);
    
    geom_point_t pts[3] = {p1, p2, p3};
    unsigned char compressed[128];
    size_t comp_size = sizeof(compressed);
    
    if (geom_export_compressed_report(pts, 3, compressed, &comp_size) == 0) {
        printf("Звіт успішно стиснуто до %zu байтів.\n", comp_size);
    }
    
    return EXIT_SUCCESS;
}
