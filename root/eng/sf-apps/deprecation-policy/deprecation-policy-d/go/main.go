// Старий шлях лічить власне використання — щоб знати, чи можна прибирати.
var legacyHits atomic.Uint64

func sendRaw(bytes []byte) {
	legacyHits.Add(1) // хтось іще нами користується
	logDeprecated("sendRaw", currentCaller() /* хто саме */)
	/* … стара логіка досі працює … */
}

// Рішення прибирати ухвалюють НЕ за датою, а за цим числом:
func safeToRemove() bool {
	return legacyHits.Load() == 0 // вікно спорожніло — тепер безпечно
}
