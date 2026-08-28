// dh-temp — CLI над хабом Digital Homes: прочитати температуру кімнати.
// Результат → stdout · діагностика → stderr · рід результату → код виходу.
package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"

	"digitalhomes/hub" // той самий ReadTemp зі статті, лише експортований
)

const (
	exOK       = 0  // температура в stdout
	exUsage    = 2  // погана команда: нема / невідома кімната
	exSensor   = 3  // давач недоступний — збій світу, можна повторити
	exInternal = 70 // внутрішній баг (EX_SOFTWARE із sysexits)
)

var knownRooms = map[string]bool{"вітальня": true, "спальня": true, "кухня": true}

func fail(asJSON bool, room string, code int, kind, human string) {
	if asJSON {
		json.NewEncoder(os.Stderr).Encode(map[string]string{
			"error": kind, "room": room, "message": human})
	} else {
		fmt.Fprintf(os.Stderr, "dh-temp: %s\n", human) // діагностика — у stderr
	}
	os.Exit(code)
}

func main() {
	asJSON := flag.Bool("json", false, "машиночитний вивід")
	flag.Parse()
	if flag.NArg() != 1 {
		fmt.Fprintln(os.Stderr, "вжиток: dh-temp [--json] <кімната>")
		os.Exit(exUsage) // погана команда — свідомо 2
	}
	room := flag.Arg(0)

	if !knownRooms[room] { // ВХІД з краю — недовірений, перевіряємо тут
		fail(*asJSON, room, exUsage, "unknown-room", fmt.Sprintf("немає кімнати %q", room))
	}

	t, err := hub.ReadTemp(room) // помилка — звичайне значення, не виняток
	if err != nil {
		var un *hub.SensorUnavailable
		if errors.As(err, &un) { // очікуване, операційне → код 3
			fail(*asJSON, room, exSensor, "sensor-unavailable", err.Error())
		}
		fmt.Fprintf(os.Stderr, "dh-temp: внутрішній збій: %v\n", err) // несподіване = баг
		os.Exit(exInternal)                                          // тег — 70, не сирий 1
	}

	if *asJSON { // РЕЗУЛЬТАТ — і тільки він — у stdout
		json.NewEncoder(os.Stdout).Encode(map[string]any{"room": room, "temp_c": t})
	} else {
		fmt.Printf("%.1f\n", t)
	}
	os.Exit(exOK)
}
