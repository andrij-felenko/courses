typedef struct { double lat_deg, lon_deg, alt_m; } geo_t;

/* Кути на ціль: рискання від півночі, тангаж від горизонту, обидва в радіанах. */
static void aim_angles(const geo_t *v, const geo_t *t, float *yaw_earth, float *pitch)
{
    const double a   = 6378137.0;          /* велика піввісь WGS-84, м        */
    const double e2  = 6.69437999014e-3;   /* квадрат першого ексцентриситету */
    const double phi = v->lat_deg * M_PI / 180.0;
    const double s   = sin(phi);
    const double w   = 1.0 - e2 * s * s;

    const double N = a / sqrt(w);                    /* радіус першого вертикала */
    const double M = a * (1.0 - e2) / (w * sqrt(w)); /* меридіанний радіус       */

    const double north = (t->lat_deg - v->lat_deg) * M_PI / 180.0 * M;
    const double east  = (t->lon_deg - v->lon_deg) * M_PI / 180.0 * N * cos(phi);
    const double up    = t->alt_m - v->alt_m;

    *yaw_earth = (float)atan2(east, north);
    *pitch     = (float)atan2(up, hypot(north, east));
}
