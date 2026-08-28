// IsoCapturePoint захоплює одну калібрувальну точку: усереднює N читань АЦП.
// adcRead — апаратне читання коду АЦП приймача.
// Викликають двічі: подавши 4 мА, потім 20 мА на вхід ізолятора.
func IsoCapturePoint(adcRead func() int32, n int) int32 {
	var acc int64
	for k := 0; k < n; k++ {
		acc += int64(adcRead())
	}
	return int32(acc / int64(n)) // усереднений код точки
}

// IsoCalibrate — повне двоточкове калібрування ізолятора.
func IsoCalibrate(c *IsoCal, adcRead func() int32) {
	// Оператор подав на вхід ізолятора рівно 4.000 мА (еталонне джерело).
	c.ADCAt4mA = IsoCapturePoint(adcRead, 256)

	// Оператор подав рівно 20.000 мА.
	c.ADCAt20mA = IsoCapturePoint(adcRead, 256)

	// Далі c зберігають у незалежну пам'ять (EEPROM/Flash) —
	// щоб калібрування пережило вимкнення живлення.
}
