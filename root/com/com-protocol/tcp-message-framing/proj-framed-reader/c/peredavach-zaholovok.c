struct out_frame {
    uint8_t        hdr[HDR];   /* заголовок формують РАЗ, на початку */
    const uint8_t *body;       /* тіло не копіюють — воно має пережити відправлення */
    uint32_t       len;
    size_t         sent;       /* скільки байтів кадру (заголовок + тіло) вже пішло */
};

static void out_begin(struct out_frame *o, const uint8_t *body, uint32_t len)
{
    put_be32(o->hdr, len);
    o->body = body;
    o->len  = len;
    o->sent = 0;
}

/* 1 — кадр пішов увесь; 0 — черга відправлення заповнилася, повторити
   на готовність до запису; -1 — помилка. */
static int out_flush(int fd, struct out_frame *o)
{
    const size_t total = (size_t)HDR + o->len;

    while (o->sent < total) {
        struct iovec iov[2];
        int nv = 0;

        if (o->sent < HDR) {                       /* заголовок ще не весь */
            iov[nv].iov_base = o->hdr + o->sent;
            iov[nv].iov_len  = HDR - o->sent;
            nv++;
        }
        size_t body_sent = (o->sent > HDR) ? o->sent - HDR : 0;
        if (body_sent < o->len) {                  /* тіло ще не все */
            iov[nv].iov_base = (void *)(o->body + body_sent);
            iov[nv].iov_len  = o->len - body_sent;
            nv++;
        }

        struct msghdr mh;
        memset(&mh, 0, sizeof mh);
        mh.msg_iov    = iov;
        mh.msg_iovlen = (size_t)nv;

        ssize_t n = sendmsg(fd, &mh, MSG_NOSIGNAL);
        if (n < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) return 0;
            return -1;
        }
        o->sent += (size_t)n;
    }
    return 1;
}
