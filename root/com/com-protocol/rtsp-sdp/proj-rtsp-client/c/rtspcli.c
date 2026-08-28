/* rtspcli.c — мінімальний клієнт RTSP.  Збирання: cc -O2 -o rtspcli rtspcli.c */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>          /* strncasecmp */
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <poll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

typedef struct {
    int  ctl;                 /* керувальний сокет TCP */
    int  cseq;                /* лічильник запитів */
    int  status;              /* код стану останньої відповіді */
    int  timeout;             /* оголошений термін життя сеансу, с */
    char base[256];           /* адреса, з якої почали */
    char session[64];         /* ідентифікатор сеансу; порожній до SETUP */
    char hdr[8192];           /* заголовки останньої відповіді */
    char body[16384];         /* тіло останньої відповіді (SDP) */
} rtsp_t;

/* Значення заголовка без урахування регістру: камери пишуть як заманеться —
   Content-length, CSEQ, session. */
static const char *hdr_find(const char *hdr, const char *name) {
    size_t nl = strlen(name);
    for (const char *p = hdr; p && *p; ) {
        if (!strncasecmp(p, name, nl)) {
            p += nl;
            while (*p == ' ' || *p == '\t') p++;
            return p;
        }
        p = strchr(p, '\n');
        if (p) p++;
    }
    return NULL;
}

static int read_byte(int fd, char *c) {
    ssize_t n;
    do { n = recv(fd, c, 1, 0); } while (n < 0 && errno == EINTR);
    return n == 1 ? 0 : -1;
}

/* Заголовки до порожнього рядка, тоді рівно Content-Length байтів тіла.
   Байт за байтом — щоб не забрати початок наступної одиниці в сокеті. */
static int rtsp_read(rtsp_t *r) {
    size_t n = 0;
    for (;;) {
        if (n + 1 >= sizeof r->hdr) return -1;
        if (read_byte(r->ctl, &r->hdr[n])) return -1;
        n++;
        if (n >= 2 && r->hdr[n-1] == '\n' && r->hdr[n-2] == '\n') break;  /* голий LF */
        if (n >= 4 && !memcmp(&r->hdr[n-4], "\r\n\r\n", 4)) break;
    }
    r->hdr[n] = '\0';
    r->status = 0;
    sscanf(r->hdr, "RTSP/%*d.%*d %d", &r->status);

    long len = 0;
    const char *cl = hdr_find(r->hdr, "Content-Length:");
    if (cl) len = strtol(cl, NULL, 10);
    if (len < 0 || (size_t) len >= sizeof r->body) return -1;
    for (long i = 0; i < len; i++)
        if (read_byte(r->ctl, &r->body[i])) return -1;
    r->body[len] = '\0';
    return 0;
}

/* extra — готові рядки заголовків, кожен зі своїм CRLF, або NULL. */
static int rtsp_send(rtsp_t *r, const char *method, const char *url,
                     const char *extra) {
    char req[1024];
    int n = snprintf(req, sizeof req,
        "%s %s RTSP/1.0\r\nCSeq: %d\r\nUser-Agent: minicli/1.0\r\n%s%s%s%s\r\n",
        method, url, ++r->cseq,
        r->session[0] ? "Session: " : "", r->session, r->session[0] ? "\r\n" : "",
        extra ? extra : "");
    if (n < 0 || n >= (int) sizeof req) return -1;
    return send(r->ctl, req, (size_t) n, 0) == n ? 0 : -1;
}
