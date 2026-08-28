// Калібрування твердого заліза: крутимо пристрій повний оберт, ловимо min/max
type HardIronCalib struct {
	xmin, xmax, ymin, ymax int16
}

func NewHardIronCalib() *HardIronCalib {
	return &HardIronCalib{xmin: 32767, xmax: -32768, ymin: 32767, ymax: -32768}
}

func (c *HardIronCalib) Update(x, y int16) { // виклик у циклі під час обертання
	if x < c.xmin {
		c.xmin = x
	}
	if x > c.xmax {
		c.xmax = x
	}
	if y < c.ymin {
		c.ymin = y
	}
	if y > c.ymax {
		c.ymax = y
	}
}

func (c *HardIronCalib) Heading(x, y int16, declinationDeg float64) float64 {
	xoff := (c.xmax + c.xmin) / 2 // центр кола по X = зсув твердого заліза
	yoff := (c.ymax + c.ymin) / 2
	return CompassHeading(x-xoff, y-yoff, declinationDeg)
}
