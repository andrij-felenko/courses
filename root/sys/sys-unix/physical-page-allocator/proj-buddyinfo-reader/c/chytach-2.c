static void human(unsigned long bytes, char *out, size_t cap)
{
    static const char *u[] = { "Б", "КіБ", "МіБ", "ГіБ", "ТіБ" };
    int i = 0;
    double v = (double) bytes;
    while (v >= 1024.0 && i < 4) { v /= 1024.0; i++; }
    snprintf(out, cap, "%.1f %s", v, u[i]);
}

/* Скільки кадрів лежить у посторінкових запасах ядер цієї зони: у /proc/zoneinfo
   це рядки «count:» усередині блоку «pagesets». У buddyinfo їх нема — і в
   MemFree теж нема, бо кадр, виданий у запас процесора, уже знято з обліку. */
static unsigned long pcp_hidden(const char *zi, int node, const char *zone)
{
    char hdr[64];
    snprintf(hdr, sizeof hdr, "Node %d, zone %8s", node, zone);
    const char *p = strstr(zi, hdr);
    if (!p) return 0;
    const char *stop = strstr(p + 1, "\nNode ");      /* межа наступної зони */
    const char *q = strstr(p, "\n  pagesets");
    if (!q || (stop && q > stop)) return 0;

    unsigned long sum = 0;
    while ((q = strstr(q + 1, "count:")) != NULL) {
        if (stop && q > stop) break;
        sum += strtoul(q + 6, NULL, 10);
    }
    return sum;
}
