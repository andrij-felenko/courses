// А — актор: поклали в пошту, актор застосує сам, по черзі, без гонок
homeActor(homeId).tell({ type: "reported", device: "heater", state: "off" });

// Б — рядки в базі: прочитали, змінили, записали назад (RMW у шард)
const row = await db.get("device_state", homeId);
row.devices.heater = "off";
await db.put("device_state", homeId, row);   // контеншен, якщо дім активний

// В — журнал: дописали факт; поточний стан порахує проєкція згорткою
await log.append(homeId, { type: "HeaterReported", state: "off", at: now() });
// стан = events.reduce(apply, initial) — колись згодом, у проєкції
