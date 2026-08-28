enum class Verdict { Accepted, Retry, Unsupported, Refused, Silence };

static void sendOrderRaw(Link &link, int param5, float value, float holdSec)
{
    mavlink_message_t msg;
    mavlink_msg_command_long_pack(GCS_SYSID, GCS_COMPID, &msg,
            link.targetSystem(), MAV_COMP_ID_AUTOPILOT1,
            MAV_CMD_ACTUATOR_TEST, 0,
            value,                        // param1 — уставка: 0…1 мотор, −1…1 серва, NaN — відпустити
            holdSec,                      // param2 — термін утримання, секунди
            0.f, 0.f,
            static_cast<float>(param5),   // param5 — кого крутити
            0.f, 0.f);
    link.send(msg);
}

static Verdict sendOrder(Link &link, int param5, float value, float holdSec, int waitMs = 60)
{
    sendOrderRaw(link, param5, value, holdSec);

    const int64_t deadline = nowMs() + waitMs;
    mavlink_message_t in;
    while (nowMs() < deadline) {
        if (!link.recv(in, 20) || in.msgid != MAVLINK_MSG_ID_COMMAND_ACK) continue;
        mavlink_command_ack_t ack;
        mavlink_msg_command_ack_decode(&in, &ack);
        if (ack.command != MAV_CMD_ACTUATOR_TEST) continue;
        switch (ack.result) {
        case MAV_RESULT_ACCEPTED:             return Verdict::Accepted;
        case MAV_RESULT_TEMPORARILY_REJECTED: return Verdict::Retry;
        case MAV_RESULT_UNSUPPORTED:          return Verdict::Unsupported;
        default:                              return Verdict::Refused;
        }
    }
    return Verdict::Silence;              // не «погано», а «поки що невідомо»
}

// Стандартна нумерація MAVLink адресує лише мотори й серви.
static int standardFunction(int px4Function)
{
    if (px4Function >= 101 && px4Function <= 112) return px4Function - 101 + 1;
    if (px4Function >= 201 && px4Function <= 215) return px4Function - 201 + 33;
    return -1;                            // шасі, захват, камера — запасного ходу немає
}
