static bool shoot_one(int32_t *out_index, uint32_t timeout_ms)
{
    static float seq = 0.0f;
    const float p[7] = { 0.0f,      /* усі сенсори цієї камери */
                         0.0f,      /* інтервал не потрібен    */
                         1.0f,      /* один кадр               */
                         ++seq, 0.0f, 0.0f, 0.0f };
    send_command(MAV_CMD_IMAGE_START_CAPTURE, CAMERA_COMP, p);

    const uint32_t t0 = now_ms();
    bool acked = false;
    mavlink_message_t m;

    while (now_ms() - t0 < timeout_ms) {
        if (!recv_msg(&m, 100)) continue;

        if (m.msgid == MAVLINK_MSG_ID_COMMAND_ACK) {
            mavlink_command_ack_t ack;
            mavlink_msg_command_ack_decode(&m, &ack);
            if (ack.command != MAV_CMD_IMAGE_START_CAPTURE) continue;
            if (ack.result == MAV_RESULT_IN_PROGRESS)       continue;
            if (ack.result != MAV_RESULT_ACCEPTED)          return false;
            acked = true;                   /* наказ прийнято — кадру ще нема */
            continue;
        }

        if (acked && m.msgid == MAVLINK_MSG_ID_CAMERA_IMAGE_CAPTURED) {
            mavlink_camera_image_captured_t ev;
            mavlink_msg_camera_image_captured_decode(&m, &ev);
            if (!ev.capture_result) return false;   /* камера зізналася, що не вийшло */
            *out_index = ev.image_index;
            return true;
        }
    }
    return false;
}
