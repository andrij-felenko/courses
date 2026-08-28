# Розбір рядка GGA на координати. Повертає dict або None, якщо fix немає.
def parse_gga(line: str):
    if not checksum_ok(line):
        return None                            # спершу контрольна сума
    parts = line.split("*")[0].split(",")      # відкинути "*hh", поділити по комах
    if not parts[0].endswith("GGA"):           # "$GPGGA" / "$GNGGA"
        return None
    fix = int(parts[6]) if parts[6] else 0
    if fix == 0:
        return None                            # нема fix — координатам не вірити
    return {
        "lat":  to_degrees(parts[2], parts[3], 2),
        "lon":  to_degrees(parts[4], parts[5], 3),
        "sats": int(parts[7]) if parts[7] else 0,
        "fix":  fix,
    }
