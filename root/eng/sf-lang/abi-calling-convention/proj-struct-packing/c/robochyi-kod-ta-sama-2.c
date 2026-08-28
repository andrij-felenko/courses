// Звичайна:
sizeof(struct SensorPacket)                       == 12
offsetof(struct SensorPacket, msg_id)             == 0
offsetof(struct SensorPacket, timestamp)          == 4    // ← посунуте набивкою
offsetof(struct SensorPacket, temperature)        == 8
offsetof(struct SensorPacket, flags)              == 10

// Запакована:
sizeof(struct SensorPacketPacked)                 == 8
offsetof(struct SensorPacketPacked, msg_id)       == 0
offsetof(struct SensorPacketPacked, timestamp)    == 1    // ← впритул, НЕ кратне 4
offsetof(struct SensorPacketPacked, temperature)  == 5
offsetof(struct SensorPacketPacked, flags)        == 7
