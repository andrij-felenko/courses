package main

import "fmt"

// Усі величини — у базових одиницях СІ: кулони, ампери, фаради, секунди, вольти.
type BootParams struct {
	Qg           float64 // заряд затвора верхнього ключа, Кл (з даташита MOSFET)
	Qls          float64 // заряд зсуву рівня за такт, Кл (з даташита драйвера)
	Qrr          float64 // зворотний заряд відновлення діода, Кл (0 для Шотткі)
	Iqbs         float64 // струм спокою верхнього боку, А (макс із даташита)
	IcbsLeak     float64 // витік плаваючої шини драйвера + конденсатора, А
	IgLeak       float64 // витік затвора + зсуву рівня в статиці, А
	F            float64 // частота ШІМ, Гц
	DutyMax      float64 // максимальна робоча шпаруватість, 0..1
	DVAllow      float64 // дозволене просідання VB-VS, В
	RCharge      float64 // сумарний послідовний опір доливу, Ом
	DcbiasDerate float64 // частка ємності, що лишається під напругою (напр. 0.5)
	Margin       float64 // додатковий запас (пуск, розкид), напр. 3.0
}

// Нижня межа: скільки ємності треба, щоб не просісти за найдовший відкритий такт.
func cbsMin(p BootParams) (cbs, qTotal float64) {
	tOn := p.DutyMax / p.F                    // найдовший відкритий час
	qOnce := p.Qg + p.Qls + p.Qrr            // разові порції
	iFlow := p.Iqbs + p.IcbsLeak + p.IgLeak
	qFlow := iFlow * tOn                      // цівки × час
	qTotal = qOnce + qFlow
	return qTotal / p.DVAllow, qTotal         // Cbs >= Qвитрат / ΔV
}

// Верхня межа: більше цієї ємності не встигне долитися за паузу tOff (5·τ).
func cbsMax(p BootParams) float64 {
	tOff := (1.0 - p.DutyMax) / p.F           // закрита частина періоду
	tauAllow := tOff / 5.0                    // 5 сталих часу на долив
	return tauAllow / p.RCharge               // Cbs_max = t_off / (5·R)
}

// Номінал, який реально ставимо: підлогу ділимо на DC-bias і множимо на запас.
func cbsPick(p BootParams) float64 {
	lo, _ := cbsMin(p)
	return lo / p.DcbiasDerate * p.Margin     // компенсуємо DC-bias і запас
}

func main() {
	p := BootParams{
		Qg: 50e-9, Qls: 5e-9, Qrr: 2e-9,
		Iqbs: 230e-6, IcbsLeak: 50e-6, IgLeak: 0.3e-6,
		F: 20e3, DutyMax: 0.90, DVAllow: 0.5,
		RCharge: 10.0, DcbiasDerate: 0.5, Margin: 3.0,
	}

	lo, qTotal := cbsMin(p)
	hi := cbsMax(p)
	pick := cbsPick(p)

	fmt.Printf("Qвитрат   = %.1f нКл\n", qTotal*1e9)
	fmt.Printf("Cbs(min)  = %.0f нФ   (нижня межа з балансу заряду)\n", lo*1e9)
	fmt.Printf("Cbs(max)  = %.0f нФ   (верхня межа з перезаряду)\n", hi*1e9)
	fmt.Printf("ставимо   ~ %.2f мкФ  (з DC-bias і запасом)\n", pick*1e6)

	if pick > hi {
		fmt.Println("УВАГА: потрібна ємність не долиється за паузу!")
		fmt.Println("  → знизь R доливу, зменш стелю шпаруватості або візьми зарядову помпу.")
	}
}
