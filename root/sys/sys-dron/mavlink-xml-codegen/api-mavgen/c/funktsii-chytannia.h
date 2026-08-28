/* По одному читачеві на кожне поле: дістає значення просто з корисних даних. */
uint32_t mavlink_msg_attitude_get_time_boot_ms(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_roll(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_pitch(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_yaw(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_rollspeed(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_pitchspeed(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_yawspeed(const mavlink_message_t* msg);

/* Розкласти все повідомлення в структуру. */
void mavlink_msg_attitude_decode(const mavlink_message_t* msg, mavlink_attitude_t* attitude);
