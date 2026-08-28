#include <mavlink.h>   /* згенерований діалект common */

/* ── 1. Попросити перелік записів ──────────────────────────────── */
void request_log_list(uint8_t chan, uint8_t tgt_sys, uint8_t tgt_comp)
{
    mavlink_message_t msg;
    mavlink_msg_log_request_list_pack_chan(
        MY_SYSID, MY_COMPID, chan, &msg,
        tgt_sys, tgt_comp,
        0,        /* start: від першого наявного */
        0xffff);  /* end:   до останнього наявного */

    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    link_write(buf, mavlink_msg_to_send_buffer(buf, &msg));
}

/* ── 2. Розібрати відповіді ────────────────────────────────────── */
static uint16_t id_offset = 0;   /* 1 для ArduPilot, 0 для решти */

void on_message(const mavlink_message_t *msg)
{
    switch (msg->msgid) {

    case MAVLINK_MSG_ID_LOG_ENTRY: {
        mavlink_log_entry_t e;
        mavlink_msg_log_entry_decode(msg, &e);

        if (e.num_logs == 0) {          /* записів немає — це вся відповідь */
            listing_done();
            return;
        }
        uint16_t index = e.id - id_offset;
        /* e.size — оцінка; e.time_utc == 0 означає «дати не знаю» */
        entry_seen(index, e.size, e.time_utc);
        return;
    }

    case MAVLINK_MSG_ID_LOG_DATA: {
        mavlink_log_data_t d;
        mavlink_msg_log_data_decode(msg, &d);

        if (d.count == 0) {             /* оголошений кінець запису */
            transfer_done();
            return;
        }
        /* корисні лише перші d.count байтів; решта d.data — нулі доповнення */
        file_write_at(d.ofs, d.data, d.count);
        return;
    }
    }
}

/* ── 3. Завершити роботу з логами — ЗАВЖДИ ─────────────────────── */
void finish(uint8_t chan, uint8_t tgt_sys, uint8_t tgt_comp)
{
    mavlink_message_t msg;
    mavlink_msg_log_request_end_pack_chan(
        MY_SYSID, MY_COMPID, chan, &msg, tgt_sys, tgt_comp);

    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    link_write(buf, mavlink_msg_to_send_buffer(buf, &msg));
}
