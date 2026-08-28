package main

import (
	"time"

	"periph.io/x/conn/v3/gpio"
	"periph.io/x/conn/v3/gpio/gpioreg"
	"periph.io/x/host/v3"
)

// Ніжки контролера, з'єднані з лічильником:
var (
	clk gpio.PinIO // → CLK (крок по фронту 0→1)
	mr  gpio.PinIO // → MR  (скид у Q0; 1 = скинути)
)

func chaserInit() {
	// Скид на старті: коротким MR=1 гарантовано ставимо лічильник у Q0.
	// Це прибирає ризик стартувати з невизначеного стану (див. «граблі»).
	mr.Out(gpio.High)
	mr.Out(gpio.Low)  // відпустили скид — тепер рахуємо від Q0
	clk.Out(gpio.Low) // такт у низькому, чекає на фронт
}

// Один крок вогника: даємо рівно один фронт 0→1 на CLK.
func chaserStep() {
	clk.Out(gpio.High) // фронт наростання — лічильник крокує на наступний вихід
	clk.Out(gpio.Low)  // повертаємо CLK у низький, готуючи наступний фронт
}

func main() {
	host.Init()
	clk = gpioreg.ByName("GPIO6")
	mr = gpioreg.ByName("GPIO7")
	chaserInit()
	for {
		chaserStep()                // активний вихід перескочив на сусідній Qn
		time.Sleep(100 * time.Millisecond) // темп вогника: 10 кроків/с → повне коло за ~1 с
	}
}
