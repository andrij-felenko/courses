static int bind_pair(int *rtp, int *rtcp, int *port) {
    struct sockaddr_in sa;
    for (int p = 5000; p < 5100; p += 2) {
        int a = socket(AF_INET, SOCK_DGRAM, 0);
        int b = socket(AF_INET, SOCK_DGRAM, 0);
        if (a < 0 || b < 0) { if (a >= 0) close(a); if (b >= 0) close(b); return -1; }
        memset(&sa, 0, sizeof sa);
        sa.sin_family = AF_INET;
        sa.sin_addr.s_addr = htonl(INADDR_ANY);
        sa.sin_port = htons((unsigned short) p);
        int ok = bind(a, (struct sockaddr *) &sa, sizeof sa) == 0;
        sa.sin_port = htons((unsigned short) (p + 1));
        ok = ok && bind(b, (struct sockaddr *) &sa, sizeof sa) == 0;
        if (ok) { *rtp = a; *rtcp = b; *port = p; return 0; }
        close(a); close(b);
    }
    return -1;
}

/* «Session: 12AF6C;timeout=60» — ідентифікатор до крапки з комою, термін після.
   Шукати timeout треба В МЕЖАХ рядка: слово трапляється й в інших заголовках. */
static void parse_session(rtsp_t *r) {
    const char *v = hdr_find(r->hdr, "Session:"), *eol, *t;
    size_t i = 0;
    if (!v) return;
    while (v[i] && v[i] != ';' && v[i] != '\r' && v[i] != '\n'
           && i + 1 < sizeof r->session) { r->session[i] = v[i]; i++; }
    r->session[i] = '\0';
    r->timeout = 60;                       /* чинне за замовчуванням */
    eol = strpbrk(v, "\r\n");
    t   = strstr(v, "timeout=");
    if (t && (!eol || t < eol)) r->timeout = (int) strtol(t + 8, NULL, 10);
    if (r->timeout < 2) r->timeout = 60;   /* сміття в полі не має ставати нулем */
}

/* RTP-Info: url=…;seq=9810092;rtptime=3450012 — опорна точка нового діапазону.
   Доріжок може бути кілька, через кому; тут беремо ділянку потрібної адреси. */
static void parse_rtp_info(const char *hdr, const char *url,
                           unsigned *seq, unsigned *ts) {
    const char *v = hdr_find(hdr, "RTP-Info:"), *s, *t;
    const char *tail = url ? strrchr(url, '/') : NULL;
    if (!v) return;
    if (tail && (s = strstr(v, tail + 1)) != NULL) v = s;   /* ділянка цієї доріжки */
    s = strstr(v, "seq=");
    t = strstr(v, "rtptime=");
    if (s) *seq = (unsigned) strtoul(s + 4, NULL, 10);
    if (t) *ts  = (unsigned) strtoul(t + 8, NULL, 10);
}
