// I/O-bound: секунда сну = чекання на мережу, ядро вільне.
// Навіть на ОДНОМУ ядрі дві задачі перекриваються — конкурентність без паралелізму.
runtime.GOMAXPROCS(1) // навмисно одне ядро — щоб довести: паралелізм тут ні до чого

var wg sync.WaitGroup
start := time.Now()
for i := 0; i < 2; i++ {
    wg.Add(1)
    go func() { defer wg.Done(); time.Sleep(time.Second) }() // «чекаємо на пристрій»
}
wg.Wait()
fmt.Println(time.Since(start)) // ≈ 1s, а не 2s: поки одна спить, ядро крутить другу
