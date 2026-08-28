import (
	"fmt"
	"time"
)

// --- тонкий шар приладу (SCPI текстом у порт) ---
// portSend(line)  — дописує "\n" і шле в UART
// portQuery(line) — шле запит, парсить число з відповіді

func psuSetVoltage(v float64)  { portSend(fmt.Sprintf("VOLT %.3f", v)) }
func loadSetCurrent(a float64) { portSend(fmt.Sprintf("CURR %.3f", a)) }

// один вузол сітки: повертає ккд у % (або -1 при відмові DUT)
func measurePoint(vinSet, ioutSet, voutNom float64) float64 {
	psuSetVoltage(vinSet)
	portSend("OUTP ON") // вхід під напругою
	loadSetCurrent(ioutSet)
	portSend("INP ON") // навантаження тримає струм

	time.Sleep(2 * time.Second) // ЧЕКАТИ усталення: електрика + тепловий дрейф

	vin := portQuery("MEAS:VOLT? PSU") // Kelvin-відбір — окремі дроти на клемах
	iin := portQuery("MEAS:CURR? PSU")
	vout := portQuery("MEAS:VOLT? LOAD")
	iout := portQuery("MEAS:CURR? LOAD")

	if vout < voutNom*0.9 { // вихід просів > 10 % → DUT у захисті/відмові
		portSend("INP OFF") // негайно зняти струм, не палити плату
		return -1.0
	}

	pin, pout := vin*iin, vout*iout
	if pin > 0.0 {
		return (pout / pin) * 100.0
	}
	return -1.0
}
