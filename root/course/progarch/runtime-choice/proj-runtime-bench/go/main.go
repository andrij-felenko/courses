// Go + горутини: блокуючий код, як у потоках, — але ціна, як у циклу подій
package main

import (
	"fmt"; "net"; "os"; "runtime"; "strconv"
)

func hold(c net.Conn) {
	buf := make([]byte, 1)
	c.Read(buf) // БЛОКУЄ — але це горутина, а не потік ОС
}

func main() {
	N := 50000
	if len(os.Args) > 1 {
		N, _ = strconv.Atoi(os.Args[1])
	}
	keep := make([]net.Conn, 0, 2*N)
	for i := 0; i < N; i++ {
		a, b := net.Pipe() // два зв'язані кінці в пам'яті
		keep = append(keep, a, b)
		go hold(a)
	}
	runtime.GC()
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	fmt.Printf("%d горутин: стеки≈%d МБ, купа≈%d МБ\n",
		N, m.StackInuse/1024/1024, m.HeapAlloc/1024/1024)
	_ = keep
}
// 50 000 горутин × ~2 КБ стартового стека ≈ сотня МБ — і код лишився блокуючим.
