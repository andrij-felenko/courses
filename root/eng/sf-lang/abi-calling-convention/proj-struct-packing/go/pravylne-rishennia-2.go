package sensor

import "encoding/binary"

// Десеріалізація: 8 байтів дроту → структура. Читаємо побайтово,
// binary.LittleEndian збирає багатобайтові числа з молодшого байта.
func UnpackSensor(in []byte) SensorPacket {
	return SensorPacket{
		MsgID:       in[0],
		Timestamp:   binary.LittleEndian.Uint32(in[1:]),
		Temperature: int16(binary.LittleEndian.Uint16(in[5:])),
		Flags:       in[7],
	}
}
