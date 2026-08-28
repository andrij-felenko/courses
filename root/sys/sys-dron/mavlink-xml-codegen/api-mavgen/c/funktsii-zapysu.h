void mavlink_msg_attitude_send(mavlink_channel_t chan,
        uint32_t time_boot_ms, float roll, float pitch, float yaw,
        float rollspeed, float pitchspeed, float yawspeed);

void mavlink_msg_attitude_send_struct(mavlink_channel_t chan,
        const mavlink_attitude_t* attitude);

void mavlink_msg_attitude_send_buf(mavlink_message_t* msgbuf, mavlink_channel_t chan,
        uint32_t time_boot_ms, float roll, float pitch, float yaw,
        float rollspeed, float pitchspeed, float yawspeed);
