/* mavrouter.c — мінімальний маршрутизатор MAVLink.
   cc -O2 -Wall mavrouter.c -I/usr/include/mavlink -o mavrouter          */
#include <common/mavlink.h>      /* заради mavlink_get_msg_entry і зсувів */
#include <poll.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <stdbool.h>

#pragma pack(push, 1)
struct mav2_hdr {
    uint8_t magic;           /* 0xFD                                     */
    uint8_t payload_len;
    uint8_t incompat_flags;  /* біт 0 — кадр підписаний                  */
    uint8_t compat_flags;
    uint8_t seq;
    uint8_t sysid;           /* ВІДПРАВНИК, а не одержувач               */
    uint8_t compid;
    uint8_t msgid[3];        /* 24 біти, молодшим байтом уперед          */
};
struct mav1_hdr {
    uint8_t magic;           /* 0xFE                                     */
    uint8_t payload_len;
    uint8_t seq;
    uint8_t sysid;
    uint8_t compid;
    uint8_t msgid;
};
#pragma pack(pop)

/* Усе, що маршрутизаторові треба знати про кадр. */
struct frame {
    const uint8_t *bytes;        /* початок кадру в буфері прийому       */
    uint16_t       len;          /* повна довжина кадру, з підписом      */
    uint32_t       msgid;
    uint8_t        src_sys, src_comp;
    int16_t        tgt_sys, tgt_comp;  /* −1 — полів адресата немає      */
};

static void frame_targets(const uint8_t *payload, uint8_t len, struct frame *f);

/* Розбирає ОБРАМЛЕННЯ першого кадру в буфері.
   Повертає, скільки байтів з початку буфера вже не потрібні;
   виставляє *got, якщо кадр зібрався повністю.                          */
static size_t frame_scan(const uint8_t *buf, size_t n, struct frame *f, bool *got)
{
    *got = false;

    size_t i = 0;
    while (i < n && buf[i] != MAVLINK_STX && buf[i] != MAVLINK_STX_MAVLINK1) {
        i++;                       /* сміття до стартового байта         */
    }
    if (i == n) {
        return n;                  /* самé сміття — буфер можна спорожнити */
    }

    const uint8_t *p     = buf + i;
    const size_t   avail = n - i;
    size_t  hdr_len, total;
    uint8_t payload_len;

    if (p[0] == MAVLINK_STX) {                          /* MAVLink v2    */
        if (avail < sizeof(struct mav2_hdr)) {
            return i;                                   /* дочитати      */
        }
        const struct mav2_hdr *h = (const struct mav2_hdr *)p;
        hdr_len     = sizeof(*h);
        payload_len = h->payload_len;
        total = hdr_len + payload_len + 2
              + ((h->incompat_flags & MAVLINK_IFLAG_SIGNED)
                     ? MAVLINK_SIGNATURE_BLOCK_LEN : 0);
        f->msgid = (uint32_t)h->msgid[0]
                 | ((uint32_t)h->msgid[1] << 8)
                 | ((uint32_t)h->msgid[2] << 16);
        f->src_sys  = h->sysid;
        f->src_comp = h->compid;
    } else {                                            /* MAVLink v1    */
        if (avail < sizeof(struct mav1_hdr)) {
            return i;
        }
        const struct mav1_hdr *h = (const struct mav1_hdr *)p;
        hdr_len     = sizeof(*h);
        payload_len = h->payload_len;
        total       = hdr_len + payload_len + 2;
        f->msgid    = h->msgid;
        f->src_sys  = h->sysid;
        f->src_comp = h->compid;
    }

    if (avail < total) {
        return i;                  /* кадр ще не дочитано                */
    }

    f->bytes = p;
    f->len   = (uint16_t)total;
    frame_targets(p + hdr_len, payload_len, f);
    *got = true;
    return i + total;
}
