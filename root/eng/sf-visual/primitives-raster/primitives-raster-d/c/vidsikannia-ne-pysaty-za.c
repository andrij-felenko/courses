#define OUT_LEFT   1
#define OUT_RIGHT  2
#define OUT_BOTTOM 4
#define OUT_TOP    8

static int outcode(int x, int y, int xmin, int ymin, int xmax, int ymax)
{
    int c = 0;
    if (x < xmin) c |= OUT_LEFT;  else if (x > xmax) c |= OUT_RIGHT;
    if (y < ymin) c |= OUT_BOTTOM; else if (y > ymax) c |= OUT_TOP;
    return c;
}
