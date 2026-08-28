MAVLINK_MSG_ID_ATTITUDE = 30

class MAVLink_attitude_message(MAVLink_message):
    id = MAVLINK_MSG_ID_ATTITUDE
    msgname = "ATTITUDE"
    fieldnames = ["time_boot_ms", "roll", "pitch", "yaw",
                  "rollspeed", "pitchspeed", "yawspeed"]
    ordered_fieldnames = ["time_boot_ms", "roll", "pitch", "yaw",
                          "rollspeed", "pitchspeed", "yawspeed"]
    fieldtypes = ["uint32_t", "float", "float", "float", "float", "float", "float"]
    fieldunits_by_name = {"time_boot_ms": "ms", "roll": "rad", "pitch": "rad",
                          "yaw": "rad", "rollspeed": "rad/s",
                          "pitchspeed": "rad/s", "yawspeed": "rad/s"}
    orders = [0, 1, 2, 3, 4, 5, 6]
    lengths = [1, 1, 1, 1, 1, 1, 1]
    array_lengths = [0, 0, 0, 0, 0, 0, 0]
    crc_extra = 39
    unpacker = struct.Struct("<Iffffff")
    instance_field = None
    instance_offset = -1

# наприкінці модуля — відповідність визначника класові (запис на кожне повідомлення)
mavlink_map = {
    MAVLINK_MSG_ID_HEARTBEAT: MAVLink_heartbeat_message,
    MAVLINK_MSG_ID_SYS_STATUS: MAVLink_sys_status_message,
    MAVLINK_MSG_ID_ATTITUDE: MAVLink_attitude_message,
}
