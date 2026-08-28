typedef struct {
    int  pt;                  /* номер типу навантаження */
    int  clock;               /* частота годинника міток, Гц */
    char codec[32];
    char control[256];        /* адреса доріжки, вже зведена до повної */
} track_t;

static const char *next_line(const char *p) {
    p = strchr(p, '\n');
    return p ? p + 1 : NULL;
}

/* a=control дає або повну адресу, або хвіст до базової, або «*» — сам сеанс. */
static void join_url(const char *base, const char *ctl, char *out, size_t n) {
    if (!strncasecmp(ctl, "rtsp://", 7)) { snprintf(out, n, "%s", ctl);  return; }
    if (!strcmp(ctl, "*"))               { snprintf(out, n, "%s", base); return; }
    size_t bl = strlen(base);
    const char *sep = (bl && base[bl-1] == '/') || ctl[0] == '/' ? "" : "/";
    snprintf(out, n, "%s%s%s", base, sep, ctl);
}

static int sdp_track(const char *sdp, const char *kind,
                     const char *base, track_t *t) {
    char want[32], v[256], name[32];
    int pt, clock;
    const char *p, *m = NULL;

    memset(t, 0, sizeof *t);
    t->pt = -1;
    snprintf(want, sizeof want, "m=%s ", kind);

    for (p = sdp; p; p = next_line(p))
        if (!strncmp(p, want, strlen(want))) { m = p; break; }
    if (!m) return -1;
    /* «m=video 0 RTP/AVP 96» — беремо перший номер зі списку профілю */
    if (sscanf(m, "m=%*s %*d %*s %d", &t->pt) != 1) return -1;

    for (p = next_line(m); p && strncmp(p, "m=", 2); p = next_line(p)) {
        if (sscanf(p, "a=rtpmap:%d %31[^/]/%d", &pt, name, &clock) == 3
            && pt == t->pt) {
            snprintf(t->codec, sizeof t->codec, "%s", name);
            t->clock = clock;
        } else if (sscanf(p, "a=control:%255[^\r\n]", v) == 1) {
            join_url(base, v, t->control, sizeof t->control);
        }
    }
    if (!t->control[0]) snprintf(t->control, sizeof t->control, "%s", base);
    /* Для номерів 0…95 частоту задає таблиця профілю, а для динамічних 96…127
       вона є ТІЛЬКИ в rtpmap — без неї мітки часу нічого не означають. */
    if (!t->clock && t->pt >= 96) return -1;
    return 0;
}
