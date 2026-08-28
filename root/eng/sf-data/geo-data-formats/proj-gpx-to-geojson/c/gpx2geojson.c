/* gpx2geojson.c — потоковий перетворювач GPX-треків на GeoJSON.
 *   cc -O2 -std=c11 -Wall -o gpx2geojson gpx2geojson.c -lexpat
 *   ./gpx2geojson track.gpx > track.geojson
 * -d <0..9>                  знаків після коми в координатах (типово 7)
 * --ele auto|ellipsoid|none  що робити з висотою (типово auto)
 * --no-times                 не збирати масив часів: пам'ять стає сталою */

#include <expat.h>
#include <locale.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define IOBUF   (64 * 1024)   /* шматок читання; пам'ять від нього не залежить */
#define TXTMAX  128           /* найдовший текстовий вузол, який нас цікавить  */
#define NAMEMAX 512           /* назва треку; довше — обрізаємо               */

enum { CAP_NONE = 0, CAP_ELE, CAP_TIME, CAP_GEOID, CAP_NAME };
enum { ELE_AUTO = 0, ELE_ELLIPSOID, ELE_NONE };

/* одна точка, зібрана з атрибутів і дочірніх елементів <trkpt> */
typedef struct {
    double lat, lon;
    int    has_pos;
    double ele, geoid;
    int    has_ele, has_geoid;
    char   time[TXTMAX];
    int    has_time;
} Pt;

/* буфер, що росте: сюди складаємо готовий текст масиву часів */
typedef struct { char *p; size_t n, cap; } Buf;

typedef struct {
    XML_Parser xp;
    FILE *out;
    int digits, ele_mode, want_times;

    int depth, d_ext, d_trk, d_seg, d_pt;   /* глибини відкритих елементів */

    int    cap_what;                        /* текст якого елемента збираємо */
    char  *cap_dst;
    size_t cap_sz, cap_len;
    char   txt[TXTMAX];
    char   name[NAMEMAX];
    int    has_name;

    Pt  cur, pend;                          /* поточна й відкладена точки */
    int pend_valid;

    long feats_written; int feat_started;
    long segs_written;  int seg_started; long pts_in_seg;

    int    dim_fixed, dim3;                 /* вимір позицій цього треку */
    double last_ele, last_geoid;

    long pts, no_time, ele_carried, geoid_carried,
         segs_dropped, pts_bad, trks_empty;

    Buf times;
    const char *abort_why;
} St;

static void die(const char *msg) {
    fprintf(stderr, "gpx2geojson: %s\n", msg);
    exit(1);
}

static void buf_write(Buf *b, const char *s, size_t k) {
    if (b->n + k + 1 > b->cap) {
        size_t cap = b->cap ? b->cap : 4096;
        char *q;
        while (cap < b->n + k + 1) cap *= 2;   /* подвоєння: амортизовано O(1) */
        q = realloc(b->p, cap);
        if (!q) die("бракує пам'яті на масив часів");
        b->p = q; b->cap = cap;
    }
    memcpy(b->p + b->n, s, k);
    b->n += k;
    b->p[b->n] = '\0';
}
static void buf_puts(Buf *b, const char *s) { buf_write(b, s, strlen(s)); }

/* JSON-рядок у лапках: expat уже гарантував коректний UTF-8, лишається
   сховати лапку, зворотну скісну й керівні символи */
static void json_quote(char *dst, size_t cap, const char *src) {
    const unsigned char *p;
    size_t j = 0;
#define PUT(c) do { if (j + 1 < cap) dst[j++] = (char)(c); } while (0)
    PUT('"');
    for (p = (const unsigned char *)src; *p; p++) {
        if (*p == '"' || *p == '\\')       { PUT('\\'); PUT(*p); }
        else if (*p == '\n')               { PUT('\\'); PUT('n'); }
        else if (*p == '\r')               { PUT('\\'); PUT('r'); }
        else if (*p == '\t')               { PUT('\\'); PUT('t'); }
        else if (*p < 0x20) {
            char u[8], *q;
            snprintf(u, sizeof u, "\\u%04x", (unsigned)*p);
            for (q = u; *q; q++) PUT(*q);
        }
        else PUT(*p);                      /* байти UTF-8 ≥ 0x20 — як є */
    }
    PUT('"');
    dst[j < cap ? j : cap - 1] = '\0';
#undef PUT
}

static char *trim(char *s) {
    char *e;
    while (*s == ' ' || *s == '\t' || *s == '\n' || *s == '\r') s++;
    e = s + strlen(s);
    while (e > s && (e[-1] == ' ' || e[-1] == '\t' ||
                     e[-1] == '\n' || e[-1] == '\r')) *--e = '\0';
    return s;
}

/* локальне ім'я: <gpx:trkpt> і <trkpt> для нас те саме */
static const char *local(const XML_Char *n) {
    const char *c = strrchr(n, ':');
    return c ? c + 1 : n;
}

/* число цілком або нічого: хвіст після числа означає, що рядок не число */
static int num(const char *s, double *out) {
    char *end;
    double v = strtod(s, &end);
    if (end == s) return 0;
    while (*end == ' ' || *end == '\t' || *end == '\n' || *end == '\r') end++;
    if (*end) return 0;
    *out = v;
    return 1;
}

static void cap_begin(St *s, int what, char *dst, size_t sz) {
    s->cap_what = what; s->cap_dst = dst; s->cap_sz = sz; s->cap_len = 0;
    dst[0] = '\0';
}

static void put(St *s, const char *t) { fputs(t, s->out); }

/* ── вивід ──────────────────────────────────────────────────────────────── */

static void emit_pos(St *s, const Pt *p) {
    char buf[96];
    double h;
    if (!s->dim_fixed) {              /* вимір визначає перша виведена точка */
        s->dim3 = (s->ele_mode == ELE_AUTO)      ? (p->has_ele && p->has_geoid)
                : (s->ele_mode == ELE_ELLIPSOID) ?  p->has_ele : 0;
        s->dim_fixed = 1;
    }
    if (!s->dim3) {
        snprintf(buf, sizeof buf, "[%.*f,%.*f]",
                 s->digits, p->lon, s->digits, p->lat);
        put(s, buf);
        return;
    }
    if (p->has_ele) s->last_ele = p->ele; else s->ele_carried++;
    h = s->last_ele;
    if (s->ele_mode == ELE_AUTO) {    /* h = H + N: з рівня моря на еліпсоїд */
        if (p->has_geoid) s->last_geoid = p->geoid; else s->geoid_carried++;
        h += s->last_geoid;
    }
    snprintf(buf, sizeof buf, "[%.*f,%.*f,%.2f]",
             s->digits, p->lon, s->digits, p->lat, h);
    put(s, buf);
}

static void emit_time(St *s, const Pt *p) {
    if (!p->has_time) s->no_time++;
    if (!s->want_times) return;
    if (p->has_time) {
        char q[TXTMAX * 6 + 4];
        json_quote(q, sizeof q, p->time);
        buf_puts(&s->times, q);
    } else {
        buf_puts(&s->times, "null");  /* дірка, а не пропуск: довжини рівні */
    }
}

static void emit_point(St *s, const Pt *p) {
    if (!s->feat_started) {
        if (s->feats_written) put(s, ",\n");
        put(s, "{\"type\":\"Feature\",\"geometry\":"
               "{\"type\":\"MultiLineString\",\"coordinates\":[");
        s->feat_started = 1;
    }
    if (!s->seg_started) {
        if (s->segs_written) { put(s, ","); if (s->want_times) buf_puts(&s->times, ","); }
        put(s, "[");           if (s->want_times) buf_puts(&s->times, "[");
        s->seg_started = 1; s->pts_in_seg = 0;
    }
    if (s->pts_in_seg) { put(s, ","); if (s->want_times) buf_puts(&s->times, ","); }
    emit_pos(s, p);
    emit_time(s, p);
    s->pts_in_seg++;
    s->pts++;
}

/* ── межі trkpt · trkseg · trk ──────────────────────────────────────────── */

static void pt_begin(St *s, const XML_Char **atts) {
    double lat = 0, lon = 0;
    int hlat = 0, hlon = 0, i;
    memset(&s->cur, 0, sizeof s->cur);
    for (i = 0; atts[i]; i += 2) {
        const char *a = local(atts[i]);
        if      (!strcmp(a, "lat")) hlat = num(atts[i + 1], &lat);
        else if (!strcmp(a, "lon")) hlon = num(atts[i + 1], &lon);
    }
    if (hlat && hlon && lat >= -90.0 && lat <= 90.0
                     && lon >= -180.0 && lon <= 180.0) {
        s->cur.lat = lat; s->cur.lon = lon; s->cur.has_pos = 1;
    }
}

static void pt_end(St *s) {
    if (!s->cur.has_pos) { s->pts_bad++; return; }
    if (s->pend_valid) emit_point(s, &s->pend);   /* попередня вже не одинока */
    s->pend = s->cur;
    s->pend_valid = 1;
}

static void seg_end(St *s) {
    if (s->pend_valid && s->seg_started) emit_point(s, &s->pend);
    s->pend_valid = 0;
    if (s->seg_started) {
        put(s, "]"); if (s->want_times) buf_puts(&s->times, "]");
        s->segs_written++; s->seg_started = 0;
    } else {
        s->segs_dropped++;      /* нуль або одна точка — лінії з такого нема */
    }
}

static void trk_begin(St *s) {
    s->feat_started = 0; s->seg_started = 0; s->pend_valid = 0;
    s->segs_written = 0; s->pts_in_seg = 0;
    s->has_name = 0; s->name[0] = '\0';
    s->dim_fixed = 0; s->dim3 = 0; s->last_ele = 0; s->last_geoid = 0;
    s->pts = s->no_time = s->ele_carried = s->geoid_carried = 0;
    s->segs_dropped = s->pts_bad = 0;
    s->times.n = 0;             /* довжина в нуль, місце лишається за нами */
}

static void trk_end(St *s) {
    char q[NAMEMAX * 6 + 4], tail[512];
    if (!s->feat_started) { s->trks_empty++; return; }

    put(s, "]},\"properties\":{\"name\":");
    if (s->has_name) { json_quote(q, sizeof q, s->name); put(s, q); }
    else             put(s, "null");

    snprintf(tail, sizeof tail,
        ",\"elevation\":\"%s\",\"conversion\":{\"digits\":%d,\"points\":%ld,"
        "\"segments\":%ld,\"segments_dropped\":%ld,\"points_without_time\":%ld,"
        "\"elevation_carried\":%ld,\"geoidheight_carried\":%ld,"
        "\"points_dropped\":%ld}",
        !s->dim3 ? "none"
                 : (s->ele_mode == ELE_AUTO ? "wgs84-ellipsoid (ele + geoidheight)"
                                            : "wgs84-ellipsoid (ele прийнято за h)"),
        s->digits, s->pts, s->segs_written, s->segs_dropped,
        s->no_time, s->ele_carried, s->geoid_carried, s->pts_bad);
    put(s, tail);

    if (s->want_times) {
        put(s, ",\"coordinateProperties\":{\"times\":[");
        if (s->times.n) fwrite(s->times.p, 1, s->times.n, s->out);
        put(s, "]}");
    }
    put(s, "}}");
    s->feats_written++;
}

/* ── обробники подій expat ──────────────────────────────────────────────── */

static void XMLCALL on_start(void *ud, const XML_Char *el, const XML_Char **atts) {
    St *s = (St *)ud;
    const char *n = local(el);
    s->depth++;

    if (s->d_ext) return;                     /* усередині extensions — сліпі */
    if (!strcmp(n, "extensions")) { s->d_ext = s->depth; return; }

    if (!s->d_trk) {
        if (!strcmp(n, "trk")) { s->d_trk = s->depth; trk_begin(s); }
        return;                               /* wpt, rte, metadata — не наше */
    }
    if (!s->d_seg) {
        if (!strcmp(n, "trkseg")) { s->d_seg = s->depth; s->seg_started = 0; }
        else if (!strcmp(n, "name") && !s->has_name)
            cap_begin(s, CAP_NAME, s->name, sizeof s->name);
        return;
    }
    if (!s->d_pt) {
        if (!strcmp(n, "trkpt")) { s->d_pt = s->depth; pt_begin(s, atts); }
        return;
    }
    if      (!strcmp(n, "ele"))         cap_begin(s, CAP_ELE,   s->txt, sizeof s->txt);
    else if (!strcmp(n, "time"))        cap_begin(s, CAP_TIME,  s->txt, sizeof s->txt);
    else if (!strcmp(n, "geoidheight")) cap_begin(s, CAP_GEOID, s->txt, sizeof s->txt);
}

/* текст одного вузла приходить ЧАСТИНАМИ — накопичуємо, не перезаписуємо */
static void XMLCALL on_text(void *ud, const XML_Char *t, int len) {
    St *s = (St *)ud;
    size_t k = (size_t)len;
    if (!s->cap_what) return;
    if (s->cap_len + k >= s->cap_sz) k = s->cap_sz - 1 - s->cap_len;
    if (!k) return;
    memcpy(s->cap_dst + s->cap_len, t, k);
    s->cap_len += k;
    s->cap_dst[s->cap_len] = '\0';
}

static void XMLCALL on_end(void *ud, const XML_Char *el) {
    St *s = (St *)ud;
    int d = s->depth--;
    (void)el;

    if (s->d_ext) { if (d == s->d_ext) s->d_ext = 0; return; }

    if (s->cap_what) {
        char *v = trim(s->cap_dst);
        double x;
        switch (s->cap_what) {
        case CAP_ELE:   if (num(v, &x)) { s->cur.ele = x;   s->cur.has_ele = 1; } break;
        case CAP_GEOID: if (num(v, &x)) { s->cur.geoid = x; s->cur.has_geoid = 1; } break;
        case CAP_TIME:  if (*v) { snprintf(s->cur.time, sizeof s->cur.time, "%s", v);
                                  s->cur.has_time = 1; } break;
        case CAP_NAME:  if (*v) { memmove(s->name, v, strlen(v) + 1); s->has_name = 1; } break;
        }
        s->cap_what = CAP_NONE;
        return;
    }
    if (d == s->d_pt)  { s->d_pt  = 0; pt_end(s);  return; }
    if (d == s->d_seg) { s->d_seg = 0; seg_end(s); return; }
    if (d == s->d_trk) { s->d_trk = 0; trk_end(s); return; }
}

/* у GPX сутностей не буває — оголошення сутності означає чужий намір */
static void XMLCALL on_entity(void *ud, const XML_Char *nm, int is_param,
                              const XML_Char *val, int val_len,
                              const XML_Char *base, const XML_Char *sysid,
                              const XML_Char *pubid, const XML_Char *nota) {
    St *s = (St *)ud;
    (void)nm; (void)is_param; (void)val; (void)val_len;
    (void)base; (void)sysid; (void)pubid; (void)nota;
    s->abort_why = "у вхідному файлі оголошено сутність (DOCTYPE) — відхилено";
    XML_StopParser(s->xp, XML_FALSE);
}

int main(int argc, char **argv) {
    St s;
    FILE *in;
    XML_Parser xp;
    const char *path = NULL;
    int i;

    /* і strtod, і printf мають бачити КРАПКУ — інакше JSON виходить кривий */
    setlocale(LC_NUMERIC, "C");

    memset(&s, 0, sizeof s);
    s.out = stdout; s.digits = 7; s.ele_mode = ELE_AUTO; s.want_times = 1;

    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-d") && i + 1 < argc) {
            s.digits = atoi(argv[++i]);
            if (s.digits < 0 || s.digits > 9) die("-d поза межами 0..9");
        } else if (!strcmp(argv[i], "--ele") && i + 1 < argc) {
            const char *m = argv[++i];
            if      (!strcmp(m, "auto"))      s.ele_mode = ELE_AUTO;
            else if (!strcmp(m, "ellipsoid")) s.ele_mode = ELE_ELLIPSOID;
            else if (!strcmp(m, "none"))      s.ele_mode = ELE_NONE;
            else die("--ele: auto | ellipsoid | none");
        } else if (!strcmp(argv[i], "--no-times")) {
            s.want_times = 0;
        } else {
            path = argv[i];
        }
    }

    in = path ? fopen(path, "rb") : stdin;
    if (!in) die("не відкривається вхідний файл");

    xp = XML_ParserCreate(NULL);   /* NULL — кодування взяти з декларації файлу */
    if (!xp) die("не створюється парсер");
    s.xp = xp;
    XML_SetUserData(xp, &s);
    XML_SetElementHandler(xp, on_start, on_end);
    XML_SetCharacterDataHandler(xp, on_text);
    XML_SetEntityDeclHandler(xp, on_entity);

    put(&s, "{\"type\":\"FeatureCollection\",\"features\":[\n");

    for (;;) {
        void *buf = XML_GetBuffer(xp, IOBUF);
        size_t got;
        int last;
        if (!buf) die("бракує пам'яті у парсері");
        got = fread(buf, 1, IOBUF, in);
        if (ferror(in)) die("помилка читання входу");
        last = (got == 0);
        if (XML_ParseBuffer(xp, (int)got, last) == XML_STATUS_ERROR) {
            fprintf(stderr, "gpx2geojson: %s (рядок %lu: %s)\n",
                    s.abort_why ? s.abort_why : "розбір XML не вдався",
                    (unsigned long)XML_GetCurrentLineNumber(xp),
                    XML_ErrorString(XML_GetErrorCode(xp)));
            return 2;                        /* вивід недописаний і невалідний */
        }
        if (last) break;
    }

    put(&s, "\n]}\n");

    XML_ParserFree(xp);
    free(s.times.p);
    if (path) fclose(in);
    fprintf(stderr, "gpx2geojson: треків виведено %ld, порожніх пропущено %ld\n",
            s.feats_written, s.trks_empty);
    if (fflush(s.out) || ferror(s.out)) die("вивід записався не повністю");
    return 0;
}
