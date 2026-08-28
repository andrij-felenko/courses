// Один крок згладженої лінії Ву по осі X: два пікселі з вагами c і 1-c.
// fy — точна (дробова) y-координата лінії в стовпці x.
static inline void plot_aa(uint16_t *fb, int W, int H,
                           int x, float fy, uint16_t fg, uint16_t bg)
{
    int    yi = (int)floorf(fy);
    float  c  = fy - yi;                 // частка над нижнім пікселем
    set_pixel(x, yi,     blend(fg, bg, 1.0f - c));  // ближчий — яскравіший
    set_pixel(x, yi + 1, blend(fg, bg, c));         // дальший — тьмяніший
}
