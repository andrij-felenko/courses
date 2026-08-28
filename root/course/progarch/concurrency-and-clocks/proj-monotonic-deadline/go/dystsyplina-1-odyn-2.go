func main() {
	fake := time.Date(2026, 1, 1, 15, 0, 0, 0, time.UTC)
	wall := func() time.Time { return fake }

	b := NewWallBudget(wall, 30*time.Second) // дедлайн = 15:00:30
	fake = fake.Add(3 * time.Second)          // минуло 3 с реального часу
	fmt.Println("залишок:", b.Remaining())    // 27s — поки все чесно

	fake = fake.Add(24 * time.Hour)           // ← NTP/адмін смикнув годинник на добу вперед
	fmt.Println("залишок:", b.Remaining())    // -23h59m33s ← ВІД'ЄМНИЙ бюджет!
}
