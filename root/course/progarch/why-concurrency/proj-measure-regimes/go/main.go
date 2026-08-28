package main

import (
	"fmt"
	"runtime"
	"sync"
	"time"
)

// ── Одиниця роботи (одна задача, важить ~1 секунду) ────────────────────
// I/O-задача: секунда СНУ. Сон — чесний замінник мережі: ядро на ньому
// нічого не рахує, лише жде, і планувальник на цей час вільний.
func ioOne() { time.Sleep(time.Second) }

// CPU-задача: секунда СПРАВЖНЬОЇ лічби, жодного сну. blackhole не дає
// компіляторові стерти «нікому не потрібний» цикл. N підбери під свою
// машину так, щоб одна задача важила ~1 с (див. пастку про розігрів).
var blackhole uint64

func cpuOne() {
	var sum uint64
	for n := uint64(0); n < 1_500_000_000; n++ {
		sum += n
	}
	blackhole += sum
}

// ── Режими: як прогнати ДВІ такі задачі ────────────────────────────────
func sequential(task func()) { task(); task() } // одна за одною → нуль відліку

func concurrent(task func()) { // дві незалежні одиниці виконання, заразом
	var wg sync.WaitGroup
	for i := 0; i < 2; i++ {
		wg.Add(1)
		go func() { defer wg.Done(); task() }()
	}
	wg.Wait()
}

// ── Секундомір: розігрів + кілька прогонів, беремо НАЙМЕНШИЙ (менше шуму) ─
func timeit(label string, run func()) {
	run() // РОЗІГРІВ — перший прогін не міряємо
	var best time.Duration
	for i := 0; i < 3; i++ {
		t0 := time.Now()
		run()
		if d := time.Since(t0); i == 0 || d < best {
			best = d
		}
	}
	fmt.Printf("%-30s %.2fs\n", label, best.Seconds())
}

func main() {
	fmt.Println("ядер у машині:", runtime.NumCPU())

	// GOMAXPROCS — той самий важіль: на скільки ЯДЕР лягає конкурентність.
	runtime.GOMAXPROCS(1) // навмисно одне ядро
	timeit("I/O · послідовно", func() { sequential(ioOne) })            // ≈ 2.00s
	timeit("I/O · конкурентно (1 ядро)", func() { concurrent(ioOne) })  // ≈ 1.00s
	timeit("CPU · послідовно", func() { sequential(cpuOne) })           // ≈ 2.00s
	timeit("CPU · конкурентно (1 ядро)", func() { concurrent(cpuOne) }) // ≈ 2.00s

	runtime.GOMAXPROCS(2) // тепер дозволяємо двом ядрам працювати водночас
	timeit("I/O · паралельно (2 ядра)", func() { concurrent(ioOne) })   // ≈ 1.00s — дарма
	timeit("CPU · паралельно (2 ядра)", func() { concurrent(cpuOne) })  // ≈ 1.00s — виграш
}
