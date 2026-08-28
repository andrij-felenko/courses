// cache_gate.go — потоковий прогін ОДНОГО класу й TTL крізь лог.
// Читає stdin по рядку: "<секунда>\t<клас>\t<ключ>". У пам'яті тримає
// лише простір ключів (тисячі пристроїв), а не весь лог, — тож переживає
// мільярди рядків при пам'яті, що росте з числом ключів, а не подій.
//   go run cache_gate.go registry 300 < access.log
package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func main() {
	class := os.Args[1]
	ttl, _ := strconv.ParseFloat(os.Args[2], 64)

	expiry := make(map[string]float64) // ключ → час протухання копії
	var hits, misses int64
	var first, last float64
	seen := false

	sc := bufio.NewScanner(os.Stdin)
	sc.Buffer(make([]byte, 1<<20), 1<<20) // терпіти довгі рядки логу
	for sc.Scan() {
		p := strings.SplitN(sc.Text(), "\t", 3)
		if len(p) < 3 || p[1] != class {
			continue
		}
		t, _ := strconv.ParseFloat(p[0], 64)
		key := p[2]
		if !seen {
			first, seen = t, true
		}
		last = t

		if exp, ok := expiry[key]; ok && exp > t {
			hits++ // копія свіжа
		} else {
			misses++ // промах → до джерела
			expiry[key] = t + ttl
		}
	}

	window := last - first
	fmt.Printf("клас=%s TTL=%.0f влучність=%.1f%% QPS джерела=%.2f\n",
		class, ttl, 100*float64(hits)/float64(hits+misses),
		float64(misses)/window)
}
