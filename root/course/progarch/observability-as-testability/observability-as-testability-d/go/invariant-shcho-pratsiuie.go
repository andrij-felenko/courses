// Той самий інваріант, що в юніт-тесті: рівень заряду завжди 0..100.
// У тесті — assert. У проді світ не спиниш: перевіряємо й ПОДАЄМО СИГНАЛ, а не падаємо.
var invariantBroken = prometheus.NewCounterVec(
    prometheus.CounterOpts{Name: "invariant_violation_total"},
    []string{"name"},
)

func clampBattery(level int, deviceID string) int {
    if level < 0 || level > 100 {
        // «Такого не буває» — а сталося. Порахуй і розкажи, не мовчи.
        invariantBroken.WithLabelValues("battery_range").Inc()
        slog.Error("invariant.broken",
            "name", "battery_range", "device", deviceID, "got", level)
        if level < 0 {
            return 0
        }
        return 100
    }
    return level
}
