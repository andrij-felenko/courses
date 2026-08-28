// Перебір зерен: знайти перше, що ламає інваріант, і тут-таки відтворити його.
func sweep(naive bool, seeds uint64) {
	for seed := uint64(0); seed < seeds; seed++ {
		ok, value, _ := runOnce(seed, naive)
		if !ok {
			fmt.Printf("ЗБІЙ на зерні %d: value=%d, а мало бути ≤ %d\n", seed, value, K)
			_, _, log := runOnce(seed, naive) // ТЕ САМЕ зерно → ТОЙ САМИЙ журнал
			for _, line := range log {
				fmt.Println("   ", line)
			}
			return
		}
	}
	fmt.Printf("усі %d зерен пройшли інваріант\n", seeds)
}

func main() {
	fmt.Println("== наївний сервер ==")
	sweep(true, 1_000_000)
	fmt.Println("== виправлений (ідемпотентний) сервер ==")
	sweep(false, 1_000_000)
}
