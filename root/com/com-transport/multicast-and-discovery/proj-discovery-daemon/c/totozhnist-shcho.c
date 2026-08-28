static int load_identity(const char *path)
{
    FILE *f = fopen(path, "r+b");
    if (f) {
        if (fread(me.id, 1, 16, f) == 16 &&
            fread(&me.incarnation, 1, 4, f) == 4) {
            me.incarnation++;                 /* новий запуск — нове втілення */
            rewind(f);
            fwrite(me.id, 1, 16, f);
            fwrite(&me.incarnation, 1, 4, f);
            fflush(f);
            fclose(f);
            return 0;
        }
        fclose(f);                            /* файл є, але зіпсутий — почнемо заново */
    }
    FILE *r = fopen("/dev/urandom", "rb");
    if (!r) return -1;
    size_t got = fread(me.id, 1, 16, r);
    fclose(r);
    if (got != 16) return -1;

    me.incarnation = 1;
    f = fopen(path, "wb");
    if (!f) return -1;
    fwrite(me.id, 1, 16, f);
    fwrite(&me.incarnation, 1, 4, f);
    fclose(f);
    return 0;
}
