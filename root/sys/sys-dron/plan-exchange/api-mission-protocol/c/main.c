/* Той самий крок бібліотекою c_library_v2: віддати пункт у відповідь на запит.
   Викликається з обробника MISSION_REQUEST_INT. */
#include <math.h>
#include "common/mavlink.h"

void send_item(uint8_t chan, uint16_t seq, const struct plan_item *it)
{
    mavlink_message_t msg;

    mavlink_msg_mission_item_int_pack_chan(
        254,                                /* sysid  — наш номер системи      */
        MAV_COMP_ID_MISSIONPLANNER,         /* compid — 190, наземна станція   */
        chan, &msg,
        1,                                  /* target_system    — апарат       */
        MAV_COMP_ID_AUTOPILOT1,             /* target_component — 1            */
        seq,                                /* номер із запиту борту           */
        MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,  /* frame                           */
        it->command,
        seq == 0,                           /* current                         */
        1,                                  /* autocontinue                    */
        it->p1, it->p2, it->p3, it->p4,
        (int32_t)lround(it->lat_deg * 1e7), /* x — градуси · 10⁷               */
        (int32_t)lround(it->lon_deg * 1e7), /* y — градуси · 10⁷               */
        it->alt_m,                          /* z — метри, float                */
        MAV_MISSION_TYPE_MISSION);

    uint8_t  buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
    link_write(buf, len);                   /* запис у канал                   */
}
