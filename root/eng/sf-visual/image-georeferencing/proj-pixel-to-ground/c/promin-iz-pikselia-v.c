/* Обернути дисторсію: із записаного пікселя дістати нормовані координати
   ідеальної камери. Вісім проходів — із великим запасом навіть для широкого кута. */
static void undistort(const Camera *c, double u, double v, double *x, double *y)
{
    double xd = (u - c->cx) / c->fx, yd = (v - c->cy) / c->fy;
    double xx = xd, yy = yd;
    for (int i = 0; i < 8; i++) {
        double r2  = xx*xx + yy*yy;
        double rad = 1.0 + r2*(c->k1 + r2*(c->k2 + r2*c->k3));
        double dx  = 2.0*c->p1*xx*yy + c->p2*(r2 + 2.0*xx*xx);
        double dy  = c->p1*(r2 + 2.0*yy*yy) + 2.0*c->p2*xx*yy;
        xx = (xd - dx) / rad;
        yy = (yd - dy) / rad;
    }
    *x = xx; *y = yy;
}
