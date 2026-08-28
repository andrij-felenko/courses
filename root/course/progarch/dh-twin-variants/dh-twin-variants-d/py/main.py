# А — актор: поклали в пошту, актор застосує сам, по черзі, без гонок
home_actor(home_id).tell({"type": "reported", "device": "heater", "state": "off"})

# Б — рядки в базі: прочитали, змінили, записали назад (RMW у шард)
row = db.get("device_state", home_id)
row["devices"]["heater"] = "off"
db.put("device_state", home_id, row)          # контеншен, якщо дім активний

# В — журнал: дописали факт; поточний стан порахує проєкція згорткою
log.append(home_id, {"type": "HeaterReported", "state": "off", "at": now()})
# стан = reduce(apply, events, initial) — колись згодом, у проєкції
