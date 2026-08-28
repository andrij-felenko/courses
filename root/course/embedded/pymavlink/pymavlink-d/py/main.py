def request_message_interval(m, message_id, rate_hz):
    interval_us = int(1e6 / rate_hz)             # 10 Гц → 100000 мкс
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0,                                        # confirmation
        message_id,                               # param1: ЯКЕ повідомлення
        interval_us,                              # param2: інтервал, мкс
        0, 0, 0, 0, 0)

# приклад: хочу ATTITUDE удесятеро частіше за GLOBAL_POSITION_INT
request_message_interval(m, mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 10)
request_message_interval(m, mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 1)
