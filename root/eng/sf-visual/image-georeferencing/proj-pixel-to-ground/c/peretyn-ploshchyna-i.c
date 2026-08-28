static void cam_origin(const Shot *s, double p0[3])
{
    M3 Rb; euler_zyx(Rb, s->body);
    m3_apply(p0, Rb, s->lever);        /* зсув від антени до камери, метри NED */
}

static Status hit_plane(const Shot *s, const double p0[3], const double d[3],
                        double h_g, double *t)
{
    if (d[2] <= 0.0) return GEO_HORIZON;
    *t = (s->h0 - h_g - p0[2]) / d[2];
    return (*t > 0.0 && *t <= RANGE_MAX) ? GEO_OK : GEO_HORIZON;
}
