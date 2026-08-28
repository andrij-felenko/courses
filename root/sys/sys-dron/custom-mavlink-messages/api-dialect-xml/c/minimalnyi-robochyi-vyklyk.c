#include <mavlink.h>

/* Скласти кадр у буфер. Повертає кількість записаних байтів. */
uint16_t build(uint8_t *buf, uint8_t chan)
{
    mavlink_message_t msg = {0};
    mavlink_msg_perimeter_beacon_status_pack_chan(
        255, MAV_COMP_ID_MISSIONPLANNER, chan, &msg,
        7,            /* beacon_id        — порядок ОПИСУ */
        12.5f,        /* range_m                          */
        88,           /* quality                          */
        1712345678ULL,/* time_usec                        */
        1, 1,         /* target_system, target_component  */
        137.0f);      /* bearing_deg — розширення         */
    return mavlink_msg_to_send_buffer(buf, &msg);
}

/* Розібрати вже прийнятий кадр. */
void consume(const mavlink_message_t *msg)
{
    if (msg->msgid != MAVLINK_MSG_ID_PERIMETER_BEACON_STATUS) {
        return;
    }
    mavlink_perimeter_beacon_status_t st = {0};
    mavlink_msg_perimeter_beacon_status_decode(msg, &st);
    /* st.bearing_deg == 0.0f, якщо відправник зібраний без цього розширення */
}
