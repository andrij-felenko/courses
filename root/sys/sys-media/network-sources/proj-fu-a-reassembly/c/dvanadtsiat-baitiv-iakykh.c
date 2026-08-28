typedef struct {
    uint8_t        pt;      /* тип корисного навантаження: 96 у типовому H.264 */
    bool           marker;  /* останній пакет кадру — для відео саме так */
    uint16_t       seq;
    uint32_t       ts, ssrc;
    const uint8_t *pl;      /* корисне навантаження й тільки воно */
    size_t         pl_len;
} rtp_view;

static bool rtp_parse(const uint8_t *p, size_t n, rtp_view *r)
{
    if (n < 12 || (p[0] >> 6) != 2)          /* версія RTP мусить бути 2 */
        return false;

    size_t hdr = 12 + 4u * (p[0] & 0x0F);    /* CC: скільки 4-байтових CSRC */
    if (n < hdr) return false;

    if (p[0] & 0x10) {                       /* X: за списком CSRC іде розширення */
        if (n < hdr + 4) return false;
        size_t words = ((size_t)p[hdr + 2] << 8) | p[hdr + 3];
        hdr += 4 + 4 * words;                /* довжина — у 32-бітних словах */
        if (n < hdr) return false;
    }

    size_t end = n;
    if (p[0] & 0x20) {                       /* P: у хвості вирівнювання */
        uint8_t skip = p[n - 1];             /* останній байт — його довжина */
        if (skip == 0 || skip > end - hdr) return false;
        end -= skip;
    }
    if (end <= hdr) return false;            /* порожнє навантаження */

    r->pt     = p[1] & 0x7F;
    r->marker = (p[1] & 0x80) != 0;
    r->seq    = (uint16_t)((p[2] << 8) | p[3]);
    r->ts     = ((uint32_t)p[4] << 24) | ((uint32_t)p[5] << 16)
              | ((uint32_t)p[6] <<  8) |  (uint32_t)p[7];
    r->ssrc   = ((uint32_t)p[8] << 24) | ((uint32_t)p[9] << 16)
              | ((uint32_t)p[10] << 8) |  (uint32_t)p[11];
    r->pl     = p + hdr;
    r->pl_len = end - hdr;
    return true;
}
