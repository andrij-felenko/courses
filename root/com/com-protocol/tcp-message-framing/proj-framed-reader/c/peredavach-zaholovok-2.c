/* Віддати один кадр. Цикл подій наш, тож недописаний кадр
   мусить пережити повернення з функції. */
struct conn_out { struct out_frame o; int busy; };

static int send_frame(int fd, struct conn_out *q,
                      const uint8_t *body, uint32_t len)
{
    if (q->busy)          return -1;   /* попередній кадр ще не пішов увесь */
    if (len > MAX_FRAME)  return -1;   /* власну стелю поважають і на передачі */

    out_begin(&q->o, body, len);
    int r = out_flush(fd, &q->o);
    q->busy = (r == 0);                /* 0 — сокет заповнився: доженемо на події */
    return r;                          /* body МУСИТЬ дожити, доки busy */
}
