mavlink_event_t ev;
mavlink_msg_event_decode(&msg, &ev);

const uint8_t  ns_id    = (uint8_t)(ev.id >> 24);        /* простір імен у метаданих */
const uint32_t sub_id   = ev.id & 0x00FFFFFFu;           /* ключ події, десятковий */
const uint8_t  external = ev.log_levels & 0x0Fu;         /* рівень для людини */
const uint8_t  internal = (uint8_t)(ev.log_levels >> 4); /* рівень для журналу */

if (external >= 8) {
    return;   /* Protocol або Disabled — показувати нічого */
}
