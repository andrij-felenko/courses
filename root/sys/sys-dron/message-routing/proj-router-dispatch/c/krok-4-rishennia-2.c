#define MY_SYS   1
#define MY_COMP  MAV_COMP_ID_ONBOARD_COMPUTER   /* 191 */

static bool is_for_me(const struct frame *f)
{
    if (f->tgt_sys > 0 && f->tgt_sys != MY_SYS) {
        return false;
    }
    if (f->tgt_comp > 0 && f->tgt_comp != MY_COMP) {
        return false;
    }
    return true;                     /* широкомовне теж моє              */
}

static void route(const struct frame *f, struct channel *in,
                  struct channel *ch, int n, uint32_t now)
{
    for (int i = 0; i < n; i++) {
        if (should_forward(f, in, &ch[i], now)) {
            (void)write(ch[i].fd, f->bytes, f->len);   /* СИРІ байти      */
        }
    }
    if (is_for_me(f)) {
        local_handle(f);      /* ось тут кадр уже можна й треба розбирати */
    }
}
