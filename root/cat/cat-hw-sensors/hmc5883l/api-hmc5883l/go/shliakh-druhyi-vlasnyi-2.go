const (
	qmcAddr     = 0x0D
	qmcData     = 0x00 // X(L,H) Y(L,H) Z(L,H) — LSB першим
	qmcStatus   = 0x06 // біт 0 = DRDY (дані готові), біт 1 = OVL (переповнення)
	qmcConfig1  = 0x09
	qmcReset    = 0x0B
	qmcLSBGauss = 12000.0 // ±2G; ±8G → 3000 LSb/Gauss (datasheet QST)
)

func QMCInit(bus Bus) error {
	if err := bus.WriteReg(qmcAddr, 0x0A, 0x80); err != nil { // м'яке скидання
		return err
	}
	time.Sleep(5 * time.Millisecond) // коротка пауза
	if err := bus.WriteReg(qmcAddr, qmcReset, 0x01); err != nil { // SET/RESET — ОБОВ'ЯЗКОВО
		return err
	}
	return bus.WriteReg(qmcAddr, qmcConfig1, 0x1D) // 512x, ±2G, 200Гц, безперервний
}

// QMCReadRaw: ok=false — немає даних / переповнення / помилка шини.
func QMCReadRaw(bus Bus) (x, y, z int16, ok bool) {
	stBuf, err := bus.ReadRegs(qmcAddr, qmcStatus, 1)
	if err != nil {
		return 0, 0, 0, false
	}
	st := stBuf[0]
	if st&0x01 == 0 { // DRDY=0 → нових даних ще немає
		return 0, 0, 0, false
	}
	b, err := bus.ReadRegs(qmcAddr, qmcData, 6)
	if err != nil || len(b) != 6 {
		return 0, 0, 0, false
	}
	// little-endian: молодший байт першим
	x = int16(binary.LittleEndian.Uint16(b[0:2]))
	y = int16(binary.LittleEndian.Uint16(b[2:4]))
	z = int16(binary.LittleEndian.Uint16(b[4:6]))
	if st&0x02 != 0 { // OVL=1 → переповнення діапазону
		return 0, 0, 0, false
	}
	return x, y, z, true
}
