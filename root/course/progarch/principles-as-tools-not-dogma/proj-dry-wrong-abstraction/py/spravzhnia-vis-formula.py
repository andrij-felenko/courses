# одна формула небезпеки — єдине місце, де живе це знання
def danger_level(zone: str, now: float | None = None) -> int:
    base = ZONE_RISK.get(zone, 0)
    return base + 1 if is_night(now) else base    # ← правило ночі тепер в ОДНОМУ місці

# три користувачі кличуть ту саму формулу:
# notify_motion:
text += f" — небезпека {danger_level(ev.zone)}"
# notify_offline:
channels = ["sms", "push"] if danger_level(ev.zone) >= 2 else ["push"]
# arm_zone:
if danger_level(zone) >= 2:
    require_second_confirm(zone)
