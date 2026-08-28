typedef struct { double readout;   /* час зчитування кадру згори вниз, с */
                 int height; } rs_geom;

/* Орієнтація камери на момент зчитування рядка r кадру k.
   Лінійно домішуємо між орієнтацією цього кадру і наступного за часткою,
   на яку рядок «з'їхав» у часі. att_k, att_k1 — кути кадрів k і k+1;
   dt_frame — час між кадрами (с). */
static att att_for_row(const att *att_k, const att *att_k1,
                       int r, const rs_geom *rs, double dt_frame)
{
    double t_into = (rs->height > 0)
                  ? ((double)r / rs->height) * rs->readout   /* зсув рядка в часі */
                  : 0.0;
    double frac = (dt_frame > 1e-9) ? t_into / dt_frame : 0.0; /* частка до наст. кадру */
    if (frac > 1.0) frac = 1.0;

    att a;                                  /* інтерполяція кутів між кадрами */
    a.ax = att_k->ax + frac * (att_k1->ax - att_k->ax);
    a.ay = att_k->ay + frac * (att_k1->ay - att_k->ay);
    a.az = att_k->az + frac * (att_k1->az - att_k->az);
    return a;
}

/* Зворотне відображення з урахуванням рядкової заслінки:
   для показаного пікселя (xd,yd) береться кут камери на момент ЙОГО рядка. */
static void sample_src_rs(const att *att_k, const att *att_k1,
                          const cam_geom *c, const rs_geom *rs, double dt_frame,
                          double xd, double yd, double *sx, double *sy)
{
    att a = att_for_row(att_k, att_k1, (int)yd, rs, dt_frame);  /* кут саме цього рядка */
    warp w = warp_for_frame(&a, c);                              /* його деформація */
    sample_src(&w, c, xd, yd, sx, sy);                           /* і вже звідки брати */
}
