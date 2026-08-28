package main

import (
	"fmt"
	"math"
)

// Driver — параметри Тіле–Смолла, просто з даташита.
type Driver struct {
	fs  float64 // власна частота, Гц
	vas float64 // еквівалентний об'єм, літри
	qts float64 // повна добротність
}

// sealedVolumeLitres — об'єм закритого ящика під бажану Q_tc.
// Виводиться з V_box = V_as / (α² − 1), де α = Q_tc/Q_ts.
func sealedVolumeLitres(d Driver, qtcTarget float64) float64 {
	alpha := qtcTarget / d.qts // у скільки разів піднімаємо Q
	denom := alpha*alpha - 1.0 // α² − 1
	if denom <= 0.0 {
		return -1.0 // Q_tc ≤ Q_ts недосяжна в ЗАКРИТОМУ ящику
	}
	return d.vas / denom
}

// closedBoxFc — частота −3 дБ (для Батерворта Q_tc=0.707 вона дорівнює f_c).
func closedBoxFc(d Driver, vboxLitres float64) float64 {
	return d.fs * math.Sqrt(1.0+d.vas/vboxLitres)
}

func main() {
	woofer := Driver{fs: 40.0, vas: 20.0, qts: 0.35}

	qtc := 0.707
	vbox := sealedVolumeLitres(woofer, qtc)
	fc := closedBoxFc(woofer, vbox)

	fmt.Printf("Ціль Q_tc = %.3f\n", qtc)
	fmt.Printf("Об'єм коробки V_box = %.1f л\n", vbox)
	fmt.Printf("Частота в ящику f_c = %.1f Гц\n", fc)
}
