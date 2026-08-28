uint8_t target_sys = 0, target_comp = 0;   // 0 — «широкомовно»
const mavlink_msg_entry_t *e = mavlink_get_msg_entry(msg->msgid);

if (e) {
    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_SYSTEM) {
        target_sys = _MAV_PAYLOAD(msg)[e->target_system_ofs];
    }
    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_COMPONENT) {
        target_comp = _MAV_PAYLOAD(msg)[e->target_component_ofs];
    }
}
