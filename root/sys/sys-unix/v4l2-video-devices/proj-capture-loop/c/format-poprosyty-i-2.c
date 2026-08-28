/* Кладе кадр на диск без дірок вирівнювання. */
static void save_raw(const char *path, const unsigned char *base,
                     unsigned stride, unsigned row, unsigned height)
{
    FILE *f = fopen(path, "wb");
    if (!f) FAIL("fopen");
    for (unsigned y = 0; y < height; y++)
        fwrite(base + (size_t) y * stride, 1, row, f);   /* крок stride, корисних row */
    fclose(f);
}
