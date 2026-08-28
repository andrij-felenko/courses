typedef struct { double lat, lon, h, range; } Fix;   /* радіани, метри */

static Status georef(const Shot *s, const Grid *dem, double h_plane, Fix *f)
{
    double p0[3], d[3], t;
    cam_origin(s, p0);
    ray_ned(s, d);

    Status st = dem ? hit_terrain(s, p0, d, dem, 10.0, 0.01, &t)
                    : hit_plane(s, p0, d, h_plane, &t);
    if (st != GEO_OK) return st;

    double dN = p0[0] + t*d[0], dE = p0[1] + t*d[1];
    f->h     = s->h0 - (p0[2] + t*d[2]);
    f->range = t;
    ned_to_geodetic(s->lat0, s->lon0, f->h, dN, dE, &f->lat, &f->lon);
    return GEO_OK;
}

#define GN 24                 /* вузлів сітки на північ і на схід */

int main(void)
{
    Shot s = {
        .u = 2938.65, .v = 2063.66,             /* піксель, ЯК ЙОГО ЗАПИСАЛА камера */
        .cam    = { 2400, 2400, 2000, 1500, -0.28, 0.09, 0.0, 0.0006, -0.0004 },
        .body   = { 0.0, 0.0, 0.0 },            /* рівний політ курсом на північ */
        .gimbal = { 0.0, -45.0*DEG, 0.0 },      /* камера нахилена на 45° униз */
        .bore   = { 0.0, 0.0, 0.0 },
        .lat0 = 50.45*DEG, .lon0 = 30.52*DEG, .h0 = 280.0,
        .lever = { 0.0, 0.0, 0.0 }
    };
    Fix f;

    if (georef(&s, NULL, 160.0, &f) == GEO_OK)  /* поле — площина на 160 м */
        printf("площина: %.6f %.6f  висота %.1f м, похила дальність %.1f м\n",
               f.lat/DEG, f.lon/DEG, f.h, f.range);

    static double dem_h[GN*GN];                 /* рівний схил 8 % на північ */
    for (int i = 0; i < GN; i++)
        for (int j = 0; j < GN; j++)
            dem_h[i*GN + j] = 160.0 + 0.08*(-200.0 + 20.0*i);
    Grid dem = { dem_h, GN, GN, 20.0, -200.0, -200.0 };

    if (georef(&s, &dem, 0.0, &f) == GEO_OK)
        printf("рельєф:  %.6f %.6f  висота %.1f м, похила дальність %.1f м\n",
               f.lat/DEG, f.lon/DEG, f.h, f.range);
    return 0;
}
