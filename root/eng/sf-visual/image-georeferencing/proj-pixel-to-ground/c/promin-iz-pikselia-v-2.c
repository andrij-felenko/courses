typedef double M3[3][3];

static void euler_zyx(M3 r, Euler e)
{
    double cr = cos(e.roll),  sr = sin(e.roll);
    double cp = cos(e.pitch), sp = sin(e.pitch);
    double cy = cos(e.yaw),   sy = sin(e.yaw);
    r[0][0] = cy*cp; r[0][1] = cy*sp*sr - sy*cr; r[0][2] = cy*sp*cr + sy*sr;
    r[1][0] = sy*cp; r[1][1] = sy*sp*sr + cy*cr; r[1][2] = sy*sp*cr - cy*sr;
    r[2][0] = -sp;   r[2][1] = cp*sr;            r[2][2] = cp*cr;
}

static void m3_apply(double out[3], M3 a, const double v[3])
{
    double t[3];
    for (int i = 0; i < 3; i++)
        t[i] = a[i][0]*v[0] + a[i][1]*v[1] + a[i][2]*v[2];
    out[0] = t[0]; out[1] = t[1]; out[2] = t[2];
}

/* Одиничний напрямок погляду в місцевих осях «північ, схід, вниз». */
static void ray_ned(const Shot *s, double d_n[3])
{
    double x, y;
    undistort(&s->cam, s->u, s->v, &x, &y);
    double inv = 1.0 / sqrt(x*x + y*y + 1.0);
    double d_c[3] = { x*inv, y*inv, inv };      /* праворуч, униз по кадру, оптична вісь */

    M3 Rbore, Rg, Rb;
    euler_zyx(Rbore, s->bore);
    euler_zyx(Rg,    s->gimbal);
    euler_zyx(Rb,    s->body);

    double d[3];
    m3_apply(d, Rbore, d_c);                    /* вивірка живе в осях камери */
    double d_mount[3] = { d[2], d[0], d[1] };   /* стала перестановка осей у кріплення */
    m3_apply(d, Rg, d_mount);                   /* кути підвісу */
    m3_apply(d_n, Rb, d);                       /* крен, тангаж, курс */
}
