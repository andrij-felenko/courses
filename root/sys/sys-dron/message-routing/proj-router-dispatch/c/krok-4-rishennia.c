/* Чи слати кадр f, що прийшов з каналу in, у канал out. */
static bool should_forward(const struct frame *f, const struct channel *in,
                           const struct channel *out, uint32_t now)
{
    if (out == in) {
        return false;                 /* назад у той самий дріт — ніколи  */
    }
    if (chan_heard(out, f->src_sys, f->src_comp, now)) {
        return false;                 /* джерело чути з того боку:        */
    }                                 /* кадр там уже є — інакше петля    */
    if (f->tgt_sys <= 0) {
        return true;                  /* −1 або 0 — широкомовний кадр     */
    }
    if (f->tgt_comp > 0) {
        return chan_heard(out, (uint8_t)f->tgt_sys, f->tgt_comp, now);
    }
    return chan_heard(out, (uint8_t)f->tgt_sys, -1, now);
}
