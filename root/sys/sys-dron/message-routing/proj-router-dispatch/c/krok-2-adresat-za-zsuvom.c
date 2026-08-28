/* Дістає адресу одержувача, НЕ розбираючи повідомлення. */
static void frame_targets(const uint8_t *payload, uint8_t len, struct frame *f)
{
    f->tgt_sys = f->tgt_comp = -1;    /* у цього повідомлення полів адресата немає */

    const mavlink_msg_entry_t *e = mavlink_get_msg_entry(f->msgid);
    if (!e) {
        return;      /* незнайоме повідомлення: адресата не знаємо — отже, «всім» */
    }
    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_SYSTEM) {
        f->tgt_sys = (e->target_system_ofs < len)
                   ? payload[e->target_system_ofs]
                   : 0;              /* поле обрізане при відправленні → нуль */
    }
    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_COMPONENT) {
        f->tgt_comp = (e->target_component_ofs < len)
                    ? payload[e->target_component_ofs]
                    : 0;
    }
}
