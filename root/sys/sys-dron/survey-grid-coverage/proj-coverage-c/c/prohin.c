int main(void)
{
    static const Pt field[] = {
        {  16,  12 }, { 272, 204 }, { 128, 396 }, {  48, 336 },
        { 108, 256 }, {  12, 184 }, { -48, 264 }, { -128, 204 }
    };
    const int    n   = (int)(sizeof field / sizeof field[0]);
    const double ang = atan2(0.6, 0.8);   /* 36.87°, дає крок «напрямок»   */
    const double d   = 40.0;              /* крок між галсами, м           */
    const double R   = 30.0;              /* мінімальний радіус розвороту  */
    const double ext = 25.0;              /* подовження кінців, м          */

    Seg segs[MAX_SEG];
    Pt  route[2 * MAX_SEG];
    double worst = 0.0;
    int nseg, np, i;

    nseg = coverage_segments(field, n, ang, d, d, segs, MAX_SEG);
    if (nseg < 0) { printf("полігон не вмістився\n"); return 1; }
    np = coverage_route(segs, nseg, ang, d, R, ext, route, 2 * MAX_SEG, &worst);
    if (np < 0) { printf("маршрут не вмістився\n"); return 1; }

    printf("галсів %d, точок %d, k = %d, найвужчий розворот %.1f м (треба %.1f)\n",
           nseg, np, (int)ceil(2.0 * R / d - EPS), worst, 2.0 * R);
    printf("  #  комірка         y        x0        x1   довжина\n");
    for (i = 0; i < nseg; i++)
        printf("%3d  %7d  %8.1f  %8.1f  %8.1f  %8.1f\n", i, segs[i].cell,
               segs[i].y, segs[i].x0, segs[i].x1, segs[i].x1 - segs[i].x0);
    printf("маршрут, метри місцевої системи:\n");
    for (i = 0; i < np; i++)
        printf("%3d  %9.1f  %9.1f\n", i, route[i].x, route[i].y);
    return 0;
}
