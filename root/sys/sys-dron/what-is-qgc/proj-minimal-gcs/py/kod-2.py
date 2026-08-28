state = {'mode': '?', 'armed': False, 'volts': None, 'pct': None,
         'lat': None, 'lon': None, 'alt': None}

def apply(msg, st):
    """Оновити знімок. Повертає result із COMMAND_ACK на нашу команду або None."""
    kind = msg.get_type()
    if kind == 'HEARTBEAT':
        if msg.get_srcComponent() != AUTOPILOT:
            return None                      # камери й підвіси теж б'ють серцем
        st['mode']  = mavutil.mode_string_v10(msg)   # своя таблиця назв на кожен стек
        st['armed'] = bool(msg.base_mode & mav.MAV_MODE_FLAG_SAFETY_ARMED)
    elif kind == 'SYS_STATUS':
        st['volts'] = msg.voltage_battery / 1000     # мВ → В
        st['pct']   = msg.battery_remaining          # −1, якщо борт не знає
    elif kind == 'GLOBAL_POSITION_INT':
        st['lat'] = msg.lat / 1e7                    # degE7 → °
        st['lon'] = msg.lon / 1e7
        st['alt'] = msg.relative_alt / 1000          # мм → м
    elif kind == 'COMMAND_ACK' and msg.command == mav.MAV_CMD_SET_MESSAGE_INTERVAL:
        return msg.result
    return None
