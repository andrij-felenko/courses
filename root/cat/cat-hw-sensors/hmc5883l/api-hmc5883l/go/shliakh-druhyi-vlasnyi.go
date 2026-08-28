package compass

import "encoding/binary"

// Bus реалізуєш під свою платформу (periph.io, golang.org/x/exp/io/i2c, тощо).
type Bus interface {
	WriteReg(addr, reg, val uint8) error
	ReadRegs(addr, reg uint8, n int) ([]byte, error)
}

const (
	hmcAddr     = 0x1E
	hmcConfigA  = 0x00
	hmcConfigB  = 0x01
	hmcMode     = 0x02
	hmcData     = 0x03 // далі 6 байтів: X(H,L) Z(H,L) Y(H,L)
	hmcIDA      = 0x0A // 'H' (0x48)
	hmcLSBGauss = 1090.0
)

// HMCDetect: true, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3').
func HMCDetect(bus Bus) bool {
	id, err := bus.ReadRegs(hmcAddr, hmcIDA, 3)
	if err != nil {
		return false
	}
	return string(id) == "H43" // 0x48 0x34 0x33
}

func HMCInit(bus Bus) error {
	if err := bus.WriteReg(hmcAddr, hmcConfigA, 0x70); err != nil { // 8 усереднень, 15 Гц
		return err
	}
	if err := bus.WriteReg(hmcAddr, hmcConfigB, 0x20); err != nil { // ±1.3 Гаус
		return err
	}
	return bus.WriteReg(hmcAddr, hmcMode, 0x00) // безперервний вимір
}

// HMCReadRaw повертає три осі; ok=false при переповненні або помилці шини.
func HMCReadRaw(bus Bus) (x, y, z int16, ok bool) {
	b, err := bus.ReadRegs(hmcAddr, hmcData, 6)
	if err != nil || len(b) != 6 {
		return 0, 0, 0, false
	}
	// Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
	x = int16(binary.BigEndian.Uint16(b[0:2]))
	z = int16(binary.BigEndian.Uint16(b[2:4]))
	y = int16(binary.BigEndian.Uint16(b[4:6]))
	// -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
	if x == -4096 || y == -4096 || z == -4096 {
		return 0, 0, 0, false
	}
	return x, y, z, true
}

// HMCToGauss переводить сирий відлік у Гауси (для діагностики / нахилокомпенсації).
func HMCToGauss(raw int16) float64 {
	return float64(raw) / hmcLSBGauss
}
