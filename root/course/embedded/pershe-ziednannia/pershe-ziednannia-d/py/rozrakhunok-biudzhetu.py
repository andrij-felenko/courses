# Конфігурація частоти ATTITUDE на 20 Гц через pymavlink
def configure_attitude_stream(master, target_sys, target_comp):
    master.mav.command_long_send(
        target_sys, target_comp,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0,       # confirmation
        30.0,    # param1: Message ID (30 = ATTITUDE)
        50000.0, # param2: 50 000 мкс = 20 Гц
        0, 0, 0, 0, 0
    )
