package sensor

import "encoding/binary"

type SensorPacket struct {
	MsgID       uint8
	Timestamp   uint32
	Temperature int16
	Flags       uint8
}

// Серіалізація: структура → рівно 8 байтів дроту. Порядок і розрядність — наші.
// binary.LittleEndian кладе молодший байт уперед; байти пишемо по одному —
// жодного припущення про розкладку структури в пам'яті.
func PackSensor(p SensorPacket, out []byte) int {
	out[0] = p.MsgID                                            // 1 байт
	binary.LittleEndian.PutUint32(out[1:], p.Timestamp)        // 4 байти
	binary.LittleEndian.PutUint16(out[5:], uint16(p.Temperature)) // 2 байти
	out[7] = p.Flags                                            // 1 байт
	return 8
}
