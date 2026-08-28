// analytics.go — важкий бік: обмежена черга → пул → канал → правила (рідний дім каналів)
package main

import "runtime"

type Frame   struct{ DeviceID string; Value float64 }
type Verdict struct{ DeviceID string; Risk  float64 }

// ШОВ Б: обмежена черга між ядром (продюсер) і пулом (споживачі). 256 — це і є шов.
var work = make(chan Frame, 256)
// ШОВ В: канал від пулу до стадії правил.
var verdicts = make(chan Verdict, 64)

func scoreAnomaly(f Frame) float64 { /* ~40 мс чистого CPU: вікно, кореляції, поріг */ return 0 }

func startPool() {
    for i := 0; i < runtime.NumCPU(); i++ {
        go func() {
            for f := range work {                              // N воркерів — з однієї черги
                verdicts <- Verdict{f.DeviceID, scoreAnomaly(f)} // ШОВ В: вирок у правила
            }
        }()
    }
}

func startRules() {
    go func() {
        for v := range verdicts {                              // стадія правил споживає вироки
            if v.Risk > 0.9 { /* дія: сповістити, вимкнути розетку */ }
        }
    }()
}

// міст від ядра: кладе кадр у чергу. Повно → блокується (зворотний тиск угору, до джерела).
func submit(f Frame) { work <- f }
