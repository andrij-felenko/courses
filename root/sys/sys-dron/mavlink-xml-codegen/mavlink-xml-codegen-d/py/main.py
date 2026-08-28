# Згенеровано з common.xml — руками не правити.
class MAVLink_attitude_message(MAVLink_message):
    id = 30
    name = 'ATTITUDE'
    # порядок полів — дротовий, той самий, що в C-структурі
    fieldnames = ['time_boot_ms', 'roll', 'pitch', 'yaw',
                  'rollspeed', 'pitchspeed', 'yawspeed']
    format = '<Iffffff'          # рядок пакування: I = uint32, f = float, < = little-endian
    crc_extra = 39

    def __init__(self, time_boot_ms, roll, pitch, yaw,
                 rollspeed, pitchspeed, yawspeed): ...
